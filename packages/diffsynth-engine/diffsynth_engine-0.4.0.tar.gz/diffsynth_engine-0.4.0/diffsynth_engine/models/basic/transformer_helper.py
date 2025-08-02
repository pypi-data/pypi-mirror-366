import torch
import torch.nn as nn


def modulate(x: torch.Tensor, shift: torch.Tensor, scale: torch.Tensor):
    return x * (1 + scale) + shift


class AdaLayerNorm(nn.Module):
    def __init__(self, dim: int, eps: float = 1e-6, device: str = "cuda:0", dtype: torch.dtype = torch.float16):
        super().__init__()
        self.linear = nn.Linear(dim, dim * 2, device=device, dtype=dtype)
        self.norm = nn.LayerNorm(dim, elementwise_affine=False, eps=1e-6, device=device, dtype=dtype)
        self.silu = nn.SiLU()

    def forward(self, x, emb):
        shift, scale = self.linear(self.silu(emb)).unsqueeze(1).chunk(2, dim=2)
        return modulate(self.norm(x), shift, scale)


class AdaLayerNormZero(nn.Module):
    def __init__(self, dim, device: str, dtype: torch.dtype):
        super().__init__()
        self.silu = nn.SiLU()
        self.linear = nn.Linear(dim, dim * 3, bias=True, device=device, dtype=dtype)
        self.norm = nn.LayerNorm(dim, elementwise_affine=False, eps=1e-6, device=device, dtype=dtype)

    def forward(self, x, emb):
        shift, scale, gate = self.linear(self.silu(emb)).unsqueeze(1).chunk(3, dim=2)
        return modulate(self.norm(x), shift, scale), gate


class RoPEEmbedding(nn.Module):
    def __init__(self, dim, theta, axes_dim):
        super().__init__()
        self.dim = dim
        self.theta = theta
        self.axes_dim = axes_dim

    def rope(self, pos: torch.Tensor, dim: int, theta: int) -> torch.Tensor:
        assert dim % 2 == 0, "The dimension must be even."

        scale = torch.arange(0, dim, 2, dtype=torch.float64, device=pos.device) / dim
        omega = 1.0 / (theta**scale)

        batch_size, seq_length = pos.shape
        out = torch.einsum("...n,d->...nd", pos, omega)
        cos_out = torch.cos(out)
        sin_out = torch.sin(out)

        stacked_out = torch.stack([cos_out, -sin_out, sin_out, cos_out], dim=-1)
        out = stacked_out.view(batch_size, -1, dim // 2, 2, 2)
        return out.float()

    def forward(self, ids):
        n_axes = ids.shape[-1]
        emb = torch.cat([self.rope(ids[..., i], self.axes_dim[i], self.theta) for i in range(n_axes)], dim=-3)
        return emb.unsqueeze(1)


class RMSNorm(nn.Module):
    def __init__(
        self,
        dim,
        eps=1e-5,
        elementwise_affine=True,
        device: str = "cuda:0",
        dtype: torch.dtype = torch.bfloat16,
    ):
        super().__init__()
        self.eps = eps
        self.dim = dim
        self.elementwise_affine = elementwise_affine
        if elementwise_affine:
            self.weight = nn.Parameter(torch.ones(dim, device=device, dtype=dtype))

    def norm(self, x):
        return x * torch.rsqrt(x.pow(2).mean(dim=-1, keepdim=True) + self.eps)

    def forward(self, x):
        norm_result = self.norm(x.float()).to(x.dtype)
        if self.elementwise_affine:
            return norm_result * self.weight
        return norm_result
