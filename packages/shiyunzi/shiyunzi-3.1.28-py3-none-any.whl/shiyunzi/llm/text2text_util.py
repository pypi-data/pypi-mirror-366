import json
import re
from openai import OpenAI
from shiyunzi.utils.log_util import get_logger
from shiyunzi.utils.config_util import get_config
from pydantic import BaseModel
from shiyunzi.doubao.doubao_service import chat_completion

class ImagePrompt(BaseModel):
    image_prompt_Y: str
    image_prompt_N: str

logger = get_logger(__name__)

RUNWAY_IMAGE_PROMPT="""
根据用户提供的主题，创建文生图提示词，用于Runway AI平台创作高质量内容。并严格按照以下JSON格式输出：

{
  "image_prompt_Y": "",
  
  "image_prompt_N": ""
}

特别注意：
1. 我要提示词，不要代码
2. 需要全部是英文
3. 提示词需控制在30个单词之内
4. 不要出现换行操作，直接输出json格式
5. json内部的字符串也不要出现换行
"""

STABLE_DIFFUSION_IMAGE_PROMPT="""
根据用户提供的主题，创建文生图提示词，用于Stable Diffusion平台创作高质量内容。并严格按照以下JSON格式输出：

{
  "image_prompt_Y": "使用以下格式构建提示词：(主体描述), (场景环境), (光线氛围), (构图视角), (艺术风格), (画质提升), (medium shot:1.2), (masterpiece:1.4), (best quality:1.3), (ultra detailed:1.2), (sharp focus:1.1), (high resolution:1.2), (HDR:1.1), (8K:1.1)",
  
  "image_prompt_N": "包含以下基础排除项：(worst quality:2), (low quality:2), (normal quality:2), (bad anatomy:1.5), (bad hands:1.4), (mutated hands:1.3), (poorly drawn hands:1.2), (missing fingers:1.2), (extra digit:1.2), (fewer digits:1.2), (bad feet:1.3), (poorly drawn face:1.3), (mutation:1.3), (deformed:1.3), (ugly:1.3), (blurry:1.3), (bad proportions:1.3), (gross proportions:1.3), (text:1.3), (error:1.3), (missing arms:1.3), (missing legs:1.3), (extra arms:1.3), (extra legs:1.3), (unclear eyes:1.2), (poorly drawn:1.2), (out of frame:1.2), (disfigured:1.3), (watermark:1.2), (signature:1.2), (username:1.2), (artist name:1.2), (trademark:1.2), (title:1.2), (multiple views:1.2), (reference sheet:1.2), (long neck:1.3), (jpeg artifacts:1.2), (lowres:1.2), (duplicate:1.2), (cropped:1.2), (multiple bodies:1.2), (extra limbs:1.2), (malformed limbs:1.2), (fused fingers:1.2), (twisted fingers:1.2), (anatomical nonsense:1.2), (disconnected limbs:1.2), (floating limbs:1.2), (disconnected joints:1.2), (misshapen body:1.2), (extra breasts:1.2), (missing breasts:1.2), (huge breasts:1.2), (deformed breasts:1.2), (liquid breasts:1.2), (heavy breasts:1.2), (floating breasts:1.2), (disconnected breasts:1.2), (poorly drawn breasts:1.2), (extra nipples:1.2), (missing nipples:1.2), (different nipples:1.2), (bad nipples:1.2), (poorly drawn nipples:1.2), (bad shadows:1.2), (unnatural shadows:1.2), (bad lighting:1.2), (unnatural lighting:1.2), (nsfw:1.5)"
}

特别注意：
1. 正向提示词需要包含权重设置，使用:1.1到:1.4之间的数值
2. 负向提示词同样包含权重设置，使用:1.2到:2.0之间的数值
3. 需要全部是英文，不要代码
5. 不要出现换行操作，直接输出json格式
6. json内部的字符串也不要出现换行
"""

DOUBAO_IMAGE_PAOMPT="""
根据用户提供的主题，创建文生图提示词，用于豆包AI平台创作高质量内容。并严格按照以下JSON格式输出：

{
  "image_prompt_Y": "",
  
  "image_prompt_N": ""
}
"""


def extract_first_code_block(text):
    """
    从文本中提取第一个被三个反引号包裹的代码块
    如果没有找到代码块，则返回整个文本内容

    参数:
    text (str): 包含代码块或纯文本的内容

    返回:
    str: 提取到的代码块内容或整个文本
    """
    # 匹配任何被```包裹的代码块，可能包含language标识
    pattern = r"```(?:\w*\s*)?\n?([\s\S]*?)\n?```"

    match = re.search(pattern, text)
    if match:
        return match.group(1).strip()
    else:
        # 如果没有找到代码块，返回整个文本
        return text.strip()


def chat_with_llm(
    image_model,
    user_prompt,
    return_json: bool = False,
    temperature: float = 0.7,
    max_tokens: int = 4096,
):
    try:
        logger.info(f"开始调用LLM,模型:{image_model},提示词:{user_prompt}")
        
        if image_model == "runway":
            system_prompt = RUNWAY_IMAGE_PROMPT
            logger.info("使用Runway提示词模板")
        elif image_model == "sd":
            system_prompt = STABLE_DIFFUSION_IMAGE_PROMPT
            logger.info("使用StableDiffusion提示词模板")
        elif image_model == "doubao":
            system_prompt = DOUBAO_IMAGE_PAOMPT
            logger.info("使用豆包提示词模板")
        
        api_key = get_config("aicvw_apikey")
        base_url = "https://aicvw.com/v1"
        model = get_config("aicvw_model")
        logger.info(f"使用模型:{model}")
        
        client = OpenAI(api_key=api_key, base_url=base_url)

        messages = [
            {"role": "system", "content": system_prompt},
            {"role": "user", "content": user_prompt},
        ]
        logger.info("发送请求到LLM")
        
        response = client.chat.completions.create(
            model=model,
            messages=messages,
            temperature=temperature,
            max_tokens=max_tokens,
            stream=False,
        )

        # 使用正则表达式提取JSON字符串
        result = response.choices[0].message.content
        logger.info("收到LLM响应")
        if result is None or result == "":
            return "FAILED"

        if return_json:
            # 提取```json```之间的内容
            result = extract_first_code_block(result)
            logger.info(f"处理之后result: {result}")
            result = json.loads(result)
            logger.info("JSON解析完成")
        return result
    except Exception as e:
        logger.error(f"调用LLM出错: {str(e)}")
        return None

def doubao_chat_with_llm(
    image_model,
    user_prompt,
    return_json: bool = False,
):
    if image_model == "doubao":
        system_prompt = DOUBAO_IMAGE_PAOMPT
        logger.info("使用豆包提示词模板")
    elif image_model == "runway":
        system_prompt = RUNWAY_IMAGE_PROMPT
        logger.info("使用Runway提示词模板")
    elif image_model == "sd":
        system_prompt = STABLE_DIFFUSION_IMAGE_PROMPT
        logger.info("使用StableDiffusion提示词模板")
    
    try:
        text, imgs, conv_id, msg_id, sec_id = chat_completion(
                    prompt=system_prompt + "\n用户提供的提示词是\n" + user_prompt,
                    guest=False,
                    conversation_id=None,
                    section_id=None,
                    attachments=[],
                    use_auto_cot=False,
                    use_deep_think=False
                )
        if return_json:
            # 提取```json```之间的内容
            text = extract_first_code_block(text)
            logger.info(f"处理之后result: {text}")
            text = json.loads(text)
            logger.info("JSON解析完成")
        return text
    except Exception as e:
        logger.error(f"调用豆包API出错: {str(e)}")
        return None