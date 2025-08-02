import requests
from shiyunzi.utils.config_util import get_config
def check_sd_available():
    """检查Stable Diffusion API是否可用"""
    sd_server = get_config("sd_server")
    if not sd_server:
        return False
    
    try:
        response = requests.get(f"https://{sd_server}/healthcheck", timeout=5)
        return response.status_code == 200
    except:
        return False

def get_sd_models():
    """获取Stable Diffusion模型列表"""
    sd_server = get_config("sd_server")
    if not sd_server:
        return []
    
    try:
        response = requests.get(f"https://{sd_server}/sdapi/v1/sd-models")
        if response.status_code == 200:
            models_data = response.json()
            return [model["title"] for model in models_data]
        else:
            print(f"获取SD模型列表失败: {response.status_code}")
            return []
    except Exception as e:
        print(f"获取SD模型列表出错: {str(e)}")
        return []

def get_sd_loras():
    """获取Stable Diffusion Lora列表"""
    sd_server = get_config("sd_server")
    if not sd_server:
        return []
    
    try:
        response = requests.get(f"https://{sd_server}/sdapi/v1/loras")
        if response.status_code == 200:
            loras_data = response.json()
            return ["无"] + [lora["name"] for lora in loras_data]
        else:
            print(f"获取SD Lora列表失败: {response.status_code}")
            return ["无"]
    except Exception as e:
        print(f"获取SD Lora列表出错: {str(e)}")
        return ["无"]

def get_sd_samplers():
    """获取Stable Diffusion采样器列表"""
    sd_server = get_config("sd_server")
    if not sd_server:
        return []
    
    try:
        response = requests.get(f"https://{sd_server}/sdapi/v1/samplers")
        if response.status_code == 200:
            samplers_data = response.json()
            return [sampler["name"] for sampler in samplers_data]
        else:
            print(f"获取SD采样器列表失败: {response.status_code}")
            return []
    except Exception as e:
        print(f"获取SD采样器列表出错: {str(e)}")
        return []

def get_sd_schedulers():
    """获取Stable Diffusion scheduler列表"""
    sd_server = get_config("sd_server")
    if not sd_server:
        return []
    
    try:
        response = requests.get(f"https://{sd_server}/sdapi/v1/schedulers")
        if response.status_code == 200:
            schedulers_data = response.json()
            return [scheduler["name"] for scheduler in schedulers_data]
        else:
            print(f"获取SD scheduler列表失败: {response.status_code}")
            return ["DPM++ 2M Karras"]  # 返回默认值
    except Exception as e:
        print(f"获取SD scheduler列表出错: {str(e)}")
        return ["DPM++ 2M Karras"]  # 返回默认值
