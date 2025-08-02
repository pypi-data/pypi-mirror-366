import re
from cakegeminiapi import video2txt

PROMPT = """
你是一名短视频复刻专家，精通文生图和图生视频技术。观察我提供的视频内容后，请提供精确的提示词以复刻该视频。

分析要求：
1. 视频叙事分析
   - 场景转换和情节推进
   - 故事结构和发展脉络
   - 核心主题和表达意图

2. 技术手法分析
   - 镜头语言和运动规律
   - 场景衔接和转场技巧
   - 色彩运用和氛围营造

3. 专业术语运用
   - 镜头调度
   - 场景过渡
   - 动作连贯性
   - 视觉节奏

注意事项：
- 全程使用动态视频分析视角
- 避免使用静态描述词（如"图片"、"照片"）
- 重点突出画面流动性和连续性

格式要求:
您的分析必须严格按照以下格式提供：
<data>
您的视频分析内容
</data>

请只在这两个标记之间提供您的分析，不要添加任何额外的解释、前言或结语。
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
    
def google_video2text(
    base_url="http://jeniya.top/v1beta",
    api_key="sk-iTSmEu5aYPEPn8u9LGXvzTQILOtukTTWiozpmniYLKnEg5XV",
    system_prompt=PROMPT,
    video_path: str = None):
    
    txt = video2txt(
        base_url=base_url,
        api_key=api_key,
        video_path=video_path,
        prompt_text=system_prompt
    )
    print("llm result", txt)
    if "<data>" in txt and "</data>" in txt:
        analysis = re.search(r'<data>(.*?)</data>', txt, re.DOTALL).group(1).strip()
        return analysis
    else:
        analysis = extract_first_code_block(txt)
        return analysis
