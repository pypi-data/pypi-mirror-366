import torch
import torch.distributed as dist
import numpy as np
from einops import rearrange
from typing import Callable, List, Tuple, Optional
from tqdm import tqdm
from PIL import Image

from diffsynth_engine.configs import WanPipelineConfig
from diffsynth_engine.algorithm.noise_scheduler.flow_match import RecifitedFlowScheduler
from diffsynth_engine.algorithm.sampler import FlowMatchEulerSampler
from diffsynth_engine.models.wan.wan_dit import WanDiT
from diffsynth_engine.models.wan.wan_text_encoder import WanTextEncoder
from diffsynth_engine.models.wan.wan_vae import WanVideoVAE
from diffsynth_engine.models.wan.wan_image_encoder import WanImageEncoder
from diffsynth_engine.models.basic.lora import LoRAContext
from diffsynth_engine.tokenizers import WanT5Tokenizer
from diffsynth_engine.pipelines import BasePipeline, LoRAStateDictConverter
from diffsynth_engine.utils.constants import WAN_TOKENIZER_CONF_PATH
from diffsynth_engine.utils.download import fetch_model
from diffsynth_engine.utils.fp8_linear import enable_fp8_linear
from diffsynth_engine.utils.parallel import ParallelWrapper
from diffsynth_engine.utils import logging


logger = logging.get_logger(__name__)


class WanLoRAConverter(LoRAStateDictConverter):
    def _from_diffsynth(self, state_dict):
        dit_dict = {}
        for key, param in state_dict.items():
            lora_args = {}
            if ".lora_A.default.weight" not in key:
                continue

            lora_args["up"] = state_dict[key.replace(".lora_A.default.weight", ".lora_B.default.weight")]
            lora_args["down"] = param
            lora_args["rank"] = lora_args["up"].shape[1]
            if key.replace(".lora_A.default.weight", ".alpha") in state_dict:
                lora_args["alpha"] = state_dict[key.replace(".lora_A.default.weight", ".alpha")]
            else:
                lora_args["alpha"] = lora_args["rank"]
            key = key.replace(".lora_A.default.weight", "")
            dit_dict[key] = lora_args
        return {"dit": dit_dict}

    def _from_civitai(self, state_dict):
        dit_dict = {}
        for key, param in state_dict.items():
            if ".lora_A.weight" not in key:
                continue

            lora_args = {}
            lora_args["up"] = state_dict[key.replace(".lora_A.weight", ".lora_B.weight")]
            lora_args["down"] = param
            lora_args["rank"] = lora_args["up"].shape[1]
            if key.replace(".lora_A.weight", ".alpha") in state_dict:
                lora_args["alpha"] = state_dict[key.replace(".lora_A.weight", ".alpha")]
            else:
                lora_args["alpha"] = lora_args["rank"]
            key = key.replace("diffusion_model.", "").replace(".lora_A.weight", "")
            dit_dict[key] = lora_args
        return {"dit": dit_dict}

    def _from_fun(self, state_dict):
        dit_dict = {}
        for key, param in state_dict.items():
            if ".lora_down.weight" not in key:
                continue

            lora_args = {}
            lora_args["up"] = state_dict[key.replace(".lora_down.weight", ".lora_up.weight")]
            lora_args["down"] = param
            lora_args["rank"] = lora_args["up"].shape[1]
            if key.replace(".lora_down.weight", ".alpha") in state_dict:
                lora_args["alpha"] = state_dict[key.replace(".lora_down.weight", ".alpha")]
            else:
                lora_args["alpha"] = lora_args["rank"]
            key = key.replace("lora_unet_blocks_", "blocks.").replace(".lora_down.weight", "")
            key = key.replace("_self_attn_", ".self_attn.")
            key = key.replace("_cross_attn_", ".cross_attn.")
            key = key.replace("_ffn_", ".ffn.")
            dit_dict[key] = lora_args
        return {"dit": dit_dict}

    def convert(self, state_dict):
        if "lora_unet_blocks_0_cross_attn_k.lora_down.weight" in state_dict:
            state_dict = self._from_fun(state_dict)
            logger.info("use fun format state dict")
        elif "diffusion_model.blocks.0.cross_attn.k.lora_A.weight" in state_dict:
            state_dict = self._from_civitai(state_dict)
            logger.info("use civitai format state dict")
        else:
            state_dict = self._from_diffsynth(state_dict)
            logger.info("use diffsynth format state dict")
        return state_dict


SHIFT_FACTORS = {
    "1.3b-t2v": 5.0,
    "14b-t2v": 5.0,
    "14b-i2v": 5.0,
    "14b-flf2v": 16.0,
}


class WanVideoPipeline(BasePipeline):
    lora_converter = WanLoRAConverter()

    def __init__(
        self,
        config: WanPipelineConfig,
        tokenizer: WanT5Tokenizer,
        text_encoder: WanTextEncoder,
        dit: WanDiT,
        vae: WanVideoVAE,
        image_encoder: WanImageEncoder,
    ):
        super().__init__(
            vae_tiled=config.vae_tiled,
            vae_tile_size=config.vae_tile_size,
            vae_tile_stride=config.vae_tile_stride,
            device=config.device,
            dtype=config.model_dtype,
        )
        self.config = config
        # sampler
        self.noise_scheduler = RecifitedFlowScheduler(
            shift=config.shift if config.shift is not None else 5.0,
            sigma_min=0.001,
            sigma_max=0.999,
        )
        self.sampler = FlowMatchEulerSampler()
        # models
        self.tokenizer = tokenizer
        self.text_encoder = text_encoder
        self.dit = dit
        self.vae = vae
        self.image_encoder = image_encoder
        self.model_names = ["text_encoder", "dit", "vae", "image_encoder"]

    def load_loras(self, lora_list: List[Tuple[str, float]], fused: bool = True, save_original_weight: bool = False):
        assert self.config.tp_degree is None or self.config.tp_degree == 1, (
            "load LoRA is not allowed when tensor parallel is enabled; "
            "set tp_degree=None or tp_degree=1 during pipeline initialization"
        )
        assert not (self.config.use_fsdp and fused), (
            "load fused LoRA is not allowed when fully sharded data parallel is enabled; "
            "either load LoRA with fused=False or set use_fsdp=False during pipeline initialization"
        )
        super().load_loras(lora_list, fused, save_original_weight)

    def unload_loras(self):
        self.dit.unload_loras()
        self.text_encoder.unload_loras()

    def denoising_model(self):
        return self.dit

    def encode_prompt(self, prompt):
        ids, mask = self.tokenizer(prompt, return_mask=True, add_special_tokens=True)
        ids = ids.to(self.device)
        mask = mask.to(self.device)
        prompt_emb = self.text_encoder(ids, mask)
        prompt_emb = prompt_emb.masked_fill(mask.unsqueeze(-1).expand_as(prompt_emb) == 0, 0)
        return prompt_emb

    def encode_image(self, images: Image.Image | List[Image.Image], num_frames, height, width):
        if isinstance(images, Image.Image):
            images = [images]
        images = [
            self.preprocess_image(image.resize((width, height), Image.Resampling.LANCZOS)).to(
                device=self.device, dtype=self.config.image_encoder_dtype
            )
            for image in images
        ]
        clip_context = self.image_encoder.encode_image(images).to(self.dtype)

        indices = torch.linspace(0, num_frames - 1, len(images), dtype=torch.long)
        msk = torch.zeros(1, num_frames, height // 8, width // 8, device=self.device, dtype=self.config.vae_dtype)
        msk[:, indices] = 1
        msk = torch.concat([torch.repeat_interleave(msk[:, 0:1], repeats=4, dim=1), msk[:, 1:]], dim=1)
        msk = msk.view(1, msk.shape[1] // 4, 4, height // 8, width // 8)
        msk = msk.transpose(1, 2).squeeze(0)

        video = torch.zeros(3, num_frames, height, width).to(device=self.device, dtype=self.config.vae_dtype)
        video[:, indices] = torch.concat([image.transpose(0, 1) for image in images], dim=1).to(
            dtype=self.config.vae_dtype
        )
        y = self.vae.encode([video], device=self.device)[0]
        y = torch.concat([msk, y]).to(dtype=self.dtype)
        return clip_context, y.unsqueeze(0)

    def tensor2video(self, frames):
        frames = rearrange(frames, "C T H W -> T H W C")
        frames = ((frames.float() + 1) * 127.5).clip(0, 255).cpu().numpy().astype(np.uint8)
        frames = [Image.fromarray(frame) for frame in frames]
        return frames

    def encode_video(self, videos: torch.Tensor):
        videos = videos.to(dtype=self.config.vae_dtype, device=self.device)
        latents = self.vae.encode(
            videos,
            device=self.device,
            tiled=self.vae_tiled,
            tile_size=self.vae_tile_size,
            tile_stride=self.vae_tile_stride,
        )
        latents = latents.to(dtype=self.config.model_dtype, device=self.device)
        return latents

    def decode_video(self, latents, progress_callback=None) -> List[torch.Tensor]:
        latents = latents.to(dtype=self.config.vae_dtype, device=self.device)
        videos = self.vae.decode(
            latents,
            device=self.device,
            tiled=self.vae_tiled,
            tile_size=self.vae_tile_size,
            tile_stride=self.vae_tile_stride,
            progress_callback=progress_callback,
        )
        videos = [video.to(dtype=self.config.model_dtype, device=self.device) for video in videos]
        return videos

    def predict_noise_with_cfg(
        self,
        latents: torch.Tensor,
        image_clip_feature: torch.Tensor,
        image_y: torch.Tensor,
        timestep: torch.Tensor,
        positive_prompt_emb: torch.Tensor,
        negative_prompt_emb: torch.Tensor,
        cfg_scale: float,
        batch_cfg: bool,
    ):
        if cfg_scale <= 1.0:
            return self.predict_noise(
                latents=latents,
                image_clip_feature=image_clip_feature,
                image_y=image_y,
                timestep=timestep,
                context=positive_prompt_emb,
            )
        if not batch_cfg:
            # cfg by predict noise one by one
            positive_noise_pred = self.predict_noise(
                latents=latents,
                image_clip_feature=image_clip_feature,
                image_y=image_y,
                timestep=timestep,
                context=positive_prompt_emb,
            )
            negative_noise_pred = self.predict_noise(
                latents=latents,
                image_clip_feature=image_clip_feature,
                image_y=image_y,
                timestep=timestep,
                context=negative_prompt_emb,
            )
            noise_pred = negative_noise_pred + cfg_scale * (positive_noise_pred - negative_noise_pred)
            return noise_pred
        else:
            # cfg by predict noise in one batch
            prompt_emb = torch.cat([positive_prompt_emb, negative_prompt_emb], dim=0)
            latents = torch.cat([latents, latents], dim=0)
            timestep = torch.cat([timestep, timestep], dim=0)
            if image_y is not None:
                image_y = torch.cat([image_y, image_y], dim=0)
            if image_clip_feature is not None:
                image_clip_feature = torch.cat([image_clip_feature, image_clip_feature], dim=0)
            positive_noise_pred, negative_noise_pred = self.predict_noise(
                latents=latents,
                image_clip_feature=image_clip_feature,
                image_y=image_y,
                timestep=timestep,
                context=prompt_emb,
            )
            noise_pred = negative_noise_pred + cfg_scale * (positive_noise_pred - negative_noise_pred)
            return noise_pred

    def predict_noise(self, latents, image_clip_feature, image_y, timestep, context):
        latents = latents.to(dtype=self.config.model_dtype, device=self.device)

        noise_pred = self.dit(
            x=latents,
            timestep=timestep,
            context=context,
            clip_feature=image_clip_feature,
            y=image_y,
        )
        return noise_pred

    def prepare_latents(
        self,
        latents,
        input_video,
        denoising_strength,
        num_inference_steps,
    ):
        if input_video is not None:
            total_steps = num_inference_steps
            sigmas, timesteps = self.noise_scheduler.schedule(total_steps)
            t_start = max(total_steps - int(num_inference_steps * denoising_strength), 1)
            sigma_start, sigmas = sigmas[t_start - 1], sigmas[t_start - 1 :]
            timesteps = timesteps[t_start - 1 :]

            noise = latents
            input_video = self.preprocess_images(input_video)
            input_video = torch.stack(input_video, dim=2)
            latents = self.encode_video(input_video).to(dtype=latents.dtype, device=latents.device)
            init_latents = latents.clone()
            latents = self.sampler.add_noise(latents, noise, sigma_start)
        else:
            sigmas, timesteps = self.noise_scheduler.schedule(num_inference_steps)
            init_latents = latents.clone()

        return init_latents, latents, sigmas, timesteps

    @torch.no_grad()
    def __call__(
        self,
        prompt,
        negative_prompt="",
        input_image: Image.Image | List[Image.Image] | None = None,
        input_video: List[Image.Image] | None = None,
        denoising_strength=1.0,
        seed=None,
        height=480,
        width=832,
        num_frames=81,
        cfg_scale=5.0,
        num_inference_steps=50,
        progress_callback: Optional[Callable] = None,  # def progress_callback(current, total, status)
    ):
        assert height % 16 == 0 and width % 16 == 0, "height and width must be divisible by 16"
        assert (num_frames - 1) % 4 == 0, "num_frames must be 4X+1"

        # Initialize noise
        if dist.is_initialized() and seed is None:
            raise ValueError("must provide a seed when parallelism is enabled")
        noise = self.generate_noise(
            (1, 16, (num_frames - 1) // 4 + 1, height // 8, width // 8), seed=seed, device="cpu", dtype=torch.float32
        ).to(self.device)
        init_latents, latents, sigmas, timesteps = self.prepare_latents(
            noise,
            input_video,
            denoising_strength,
            num_inference_steps,
        )
        self.sampler.initialize(init_latents=init_latents, timesteps=timesteps, sigmas=sigmas)
        # Encode prompts
        self.load_models_to_device(["text_encoder"])
        prompt_emb_posi = self.encode_prompt(prompt)
        prompt_emb_nega = None if cfg_scale <= 1.0 else self.encode_prompt(negative_prompt)

        # Encode image
        if input_image is not None and self.image_encoder is not None:
            self.load_models_to_device(["image_encoder", "vae"])
            image_clip_feature, image_y = self.encode_image(input_image, num_frames, height, width)
        else:
            image_clip_feature, image_y = None, None

        # Denoise
        self.load_models_to_device(["dit"])
        hide_progress = dist.is_initialized() and dist.get_rank() != 0
        for i, timestep in enumerate(tqdm(timesteps, disable=hide_progress)):
            timestep = timestep.unsqueeze(0).to(dtype=self.config.model_dtype, device=self.device)
            # Classifier-free guidance
            noise_pred = self.predict_noise_with_cfg(
                latents=latents,
                timestep=timestep,
                positive_prompt_emb=prompt_emb_posi,
                negative_prompt_emb=prompt_emb_nega,
                image_clip_feature=image_clip_feature,
                image_y=image_y,
                cfg_scale=cfg_scale,
                batch_cfg=self.config.batch_cfg,
            )
            # Scheduler
            latents = self.sampler.step(latents, noise_pred, i)
            if progress_callback is not None:
                progress_callback(i + 1, len(timesteps), "DENOISING")

        # Decode
        self.load_models_to_device(["vae"])
        frames = self.decode_video(latents, progress_callback=progress_callback)
        frames = self.tensor2video(frames[0])
        return frames

    @classmethod
    def from_pretrained(cls, model_path_or_config: WanPipelineConfig) -> "WanVideoPipeline":
        if isinstance(model_path_or_config, str):
            config = WanPipelineConfig(model_path=model_path_or_config)
        else:
            config = model_path_or_config

        if config.t5_path is None:
            config.t5_path = fetch_model("muse/wan2.1-umt5", path="umt5.safetensors")
        if config.vae_path is None:
            config.vae_path = fetch_model("muse/wan2.1-vae", path="vae.safetensors")

        logger.info(f"loading state dict from {config.model_path} ...")
        dit_state_dict = cls.load_model_checkpoint(config.model_path, device="cpu", dtype=config.model_dtype)

        logger.info(f"loading state dict from {config.t5_path} ...")
        t5_state_dict = cls.load_model_checkpoint(config.t5_path, device="cpu", dtype=config.t5_dtype)

        logger.info(f"loading state dict from {config.vae_path} ...")
        vae_state_dict = cls.load_model_checkpoint(config.vae_path, device="cpu", dtype=config.vae_dtype)

        init_device = "cpu" if config.parallelism > 1 or config.offload_mode is not None else config.device
        tokenizer = WanT5Tokenizer(WAN_TOKENIZER_CONF_PATH, seq_len=512, clean="whitespace")
        text_encoder = WanTextEncoder.from_state_dict(t5_state_dict, device=init_device, dtype=config.t5_dtype)
        vae = WanVideoVAE.from_state_dict(vae_state_dict, device=init_device, dtype=config.vae_dtype)

        image_encoder = None
        if config.image_encoder_path is not None:
            logger.info(f"loading state dict from {config.image_encoder_path} ...")
            image_encoder_state_dict = cls.load_model_checkpoint(
                config.image_encoder_path,
                device="cpu",
                dtype=config.image_encoder_dtype,
            )
            image_encoder = WanImageEncoder.from_state_dict(
                image_encoder_state_dict,
                device=init_device,
                dtype=config.image_encoder_dtype,
            )

        # determine wan video model type by dit params
        model_type = None
        if "img_emb.emb_pos" in dit_state_dict:
            model_type = "14b-flf2v"
        elif "img_emb.proj.0.weight" in dit_state_dict:
            model_type = "14b-i2v"
        elif "blocks.39.self_attn.norm_q.weight" in dit_state_dict:
            model_type = "14b-t2v"
        else:
            model_type = "1.3b-t2v"

        # shift for different model_type
        config.shift = SHIFT_FACTORS[model_type] if config.shift is None else config.shift

        with LoRAContext():
            attn_kwargs = {
                "attn_impl": config.dit_attn_impl,
                "sparge_smooth_k": config.sparge_smooth_k,
                "sparge_cdfthreshd": config.sparge_cdfthreshd,
                "sparge_simthreshd1": config.sparge_simthreshd1,
                "sparge_pvthreshd": config.sparge_pvthreshd,
            }
            dit = WanDiT.from_state_dict(
                dit_state_dict,
                model_type=model_type,
                device=init_device,
                dtype=config.model_dtype,
                attn_kwargs=attn_kwargs,
            )
            if config.use_fp8_linear:
                enable_fp8_linear(dit)

        pipe = cls(
            config=config,
            tokenizer=tokenizer,
            text_encoder=text_encoder,
            dit=dit,
            vae=vae,
            image_encoder=image_encoder,
        )
        pipe.eval()

        if config.offload_mode is not None:
            pipe.enable_cpu_offload(config.offload_mode)

        if config.parallelism > 1:
            return ParallelWrapper(
                pipe,
                cfg_degree=config.cfg_degree,
                sp_ulysses_degree=config.sp_ulysses_degree,
                sp_ring_degree=config.sp_ring_degree,
                tp_degree=config.tp_degree,
                use_fsdp=config.use_fsdp,
                device="cuda",
            )
        return pipe
