import webuiapi
import os
from shiyunzi.utils.config_util import get_config
from shiyunzi.utils.path_util import get_task_image_dir
from shiyunzi.utils.models import StableDiffusion, Work
import json
import random
from shiyunzi.utils.log_util import get_logger
import time 
import traceback

logger = get_logger(__name__)

def stable_deffusion_txt2img(
    work: Work
):
    try:
        sd_server = get_config("sd_server")
        if not sd_server:
            logger.error("未填写StableDiffusion服务地址")
            return None
        api = webuiapi.WebUIApi(
            host=sd_server, port=443, use_https=True
        )
        # 查询StableDiffusion模型
        stable_diffusion =StableDiffusion.select().where(StableDiffusion.id == work.stable_diffusion).first()
        if not stable_diffusion:
            return None
        base_model = stable_diffusion.model
        lora_models = json.loads(stable_diffusion.lora)
        sampler = stable_diffusion.sampler
        scheduler = stable_diffusion.scheduler
        steps = stable_diffusion.steps
        cfg_scale = stable_diffusion.cfg
        prompt = work.text2image_prompt
        negative_prompt = work.text2image_negative_prompt
        width = stable_diffusion.width
        height = stable_diffusion.height
        
        # 主模型设置
        api.set_options({"sd_model_checkpoint": base_model}) 
        # VAE设置
        api.set_options(
            {"sd_vae": "ae.safetensors,clip_l.safetensors,t5xxl_fp8_e4m3fn.safetensors"}
        )
        api.set_options(
        {
            "forge_additional_modules": [
                "/root/stable-diffusion-webui/models/VAE/FLUX/ae.safetensors",
                "/root/stable-diffusion-webui/models/text_encoder/clip_l.safetensors",
                "/root/stable-diffusion-webui/models/text_encoder/t5xxl_fp8_e4m3fn.safetensors",
                ]
            }
        )

        output_dir = get_task_image_dir(work.task.id)

        # 添加lora模型到提示词
        for lora_model in lora_models: 
            prompt += f",<lora:{lora_model}:1>"
        # 以下选项可以通过代码中增加的【==== 可用于txt2img API调用的JSON ====】日志获取
        result1 = api.txt2img(
            prompt= prompt,
            negative_prompt=negative_prompt,
            styles=[],
            seed=random.randint(1, 9999999),
            subseed=-1,
            subseed_strength=0,
            seed_resize_from_h=-1,
            seed_resize_from_w=-1,
            sampler_name=sampler,
            scheduler=scheduler,
            batch_size=1,
            n_iter=1,
            steps=steps,
            cfg_scale=1.0,
            width=width,
            height=height,
            enable_hr=False,
            hr_scale=2,
            hr_upscaler="Latent",
            hr_second_pass_steps=0,
            hr_resize_x=0,
            hr_resize_y=0,
            denoising_strength=0.7,
        )
        # 只会生成一张图片，使用时间戳命名
        if result1.images:
            timestamp = int(time.time())
            img_path = f"{output_dir}/generated_image_{timestamp}.png"
            result1.images[0].save(img_path)
            logger.info(f"图片已保存到: {img_path}")
            return img_path
    except Exception as e:
        logger.error(f"生成图片时发生错误: {str(e)}")
        logger.error(f"调用栈信息: {traceback.format_exc()}")
        return None