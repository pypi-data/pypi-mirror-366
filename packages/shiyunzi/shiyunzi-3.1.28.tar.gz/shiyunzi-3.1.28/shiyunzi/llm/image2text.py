import json
import re
from openai import OpenAI
from shiyunzi.utils.log_util import get_logger
from shiyunzi.utils.config_util import get_config
from pydantic import BaseModel
from shiyunzi.doubao.doubao_service import chat_completion, upload_file
import os

class VideoPrompt(BaseModel):
    video_prompt: str

logger = get_logger(__name__)

RUNWAY_VIDEO_PROMPT="""
根据用户提供的主题和图片，创建视频提示词，用于Runway AI平台创作视频。并严格按照以下JSON格式输出：

{
  "video_prompt": ""
}

特别注意：
1. 需要全部使用英文描述
2. 不要代码，只要提示词
3. 不要出现换行操作，直接输出json格式
4. json内部的字符串也不要出现换行
5. 视频提示词需要保持简洁，尽量控制在30个单词以内
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

def image2text_prompt(
    video_model,
    user_prompt,
    image_path,
    return_json: bool = False,
    temperature: float = 0.7,
    max_tokens: int = 4096,
):
    try:
        logger.info(f"开始调用LLM,模型:{video_model},提示词:{user_prompt}")
        
        if video_model == "runway":
            system_prompt = RUNWAY_VIDEO_PROMPT
            logger.info("使用Runway提示词模板")
        
        api_key = get_config("aicvw_apikey")
        base_url = "https://aicvw.com/v1"
        model = get_config("aicvw_model")
        logger.info(f"使用模型:{model}")
        
        client = OpenAI(api_key=api_key, base_url=base_url)

        # 读取图片文件并转换为base64
        with open(image_path, "rb") as image_file:
            import base64
            image_base64 = base64.b64encode(image_file.read()).decode('utf-8')

        # 如果用户提示词为空，使用默认提示词
        if not user_prompt:
            user_prompt = "根据图片内容生成视频提示词"
            
        messages = [
            {"role": "system", "content": system_prompt},
            {
                "role": "user", 
                "content": [
                    {"type": "text", "text": user_prompt},
                    {
                        "type": "image_url",
                        "image_url": {
                            "url": f"data:image/jpeg;base64,{image_base64}"
                        }
                    }
                ]
            }
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

def doubao_image2text_prompt(
    video_model,
    user_prompt,
    image_path,
    return_json: bool = False,
):
    if video_model == "runway":
        system_prompt = RUNWAY_VIDEO_PROMPT
        logger.info("使用Runway提示词模板")

    try:
        # 读取图片文件数据
        with open(image_path, "rb") as f:
            file_data = f.read()
            
        # 获取文件名
        file_name = os.path.basename(image_path)
        
        # 上传图片文件,类型为2表示图片
        image_info = upload_file(2, file_name, file_data)
        if not image_info:
            raise Exception("上传图片失败")
            
        logger.info(f"图片上传成功: {image_info}")
        text, imgs, conv_id, msg_id, sec_id = chat_completion(
                    prompt=system_prompt + "\n用户提供的提示词是\n" + user_prompt,
                    guest=False,
                    conversation_id=None,
                    section_id=None,
                    attachments=[{
                        "key": image_info.key,
                        "name": image_info.name,
                        "option": image_info.option,
                        "type": image_info.type,
                        "file_review_state": image_info.file_review_state,
                        "file_parse_state": image_info.file_parse_state,
                        "identifier": image_info.identifier
                    }],
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
        # 输出堆栈
        import traceback
        traceback.print_exc()
        return None