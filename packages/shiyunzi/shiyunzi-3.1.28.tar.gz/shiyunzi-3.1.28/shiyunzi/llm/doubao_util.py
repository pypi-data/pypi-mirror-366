from shiyunzi.doubao.doubao_service import chat_completion
from shiyunzi.utils.log_util import get_logger  
import json

logger = get_logger(__name__)

def doubao_image_generate(
    user_prompt,
    resolution="9:16"
):
    text, imgs, conv_id, msg_id, sec_id = chat_completion(
                    prompt="生成一张图片，提示词是：" + user_prompt + "比例「" + resolution + "」",
                    guest=False,
                    conversation_id=None,
                    section_id=None,
                    attachments=[],
                    use_auto_cot=False,
                    use_deep_think=False
                )
    logger.info(f"豆包图片生成结果: {imgs[0]}")
    return imgs[0]