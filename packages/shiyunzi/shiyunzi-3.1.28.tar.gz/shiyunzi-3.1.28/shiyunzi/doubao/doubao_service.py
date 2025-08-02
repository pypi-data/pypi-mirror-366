from shiyunzi.doubao.session_pool import session_pool
from requests_aws4auth import AWS4Auth
from fastapi import HTTPException
import requests
import httpx
import json
import uuid
import hashlib
import binascii
import os
from shiyunzi.utils.log_util import get_logger

logger = get_logger(__name__)


def chat_completion(
    prompt: str, 
    guest: bool,
    section_id: str = None, 
    conversation_id: str = None, 
    attachments: list[dict] = [], 
    use_auto_cot: bool = False, 
    use_deep_think: bool = False
):
    # 获取会话配置
    session = session_pool.get_session(conversation_id, guest)
    if not session:
        raise Exception("会话配置不存在,请检查 session.config 文件")
    
    # ------ PARAMS -------
    params = "&".join([
        "aid=497858",
        f"device_id={session.device_id}",
        "device_platform=web",
        "language=zh",
        "pc_version=2.23.2",
        "pkg_type=release_version",
        "real_aid=497858",
        "region=CN",
        "samantha_web=1",
        "sys_region=CN",
        f"tea_uuid={session.tea_uuid}",
        "use-olympus-account=1",
        "version_code=20800",
        f"web_id={session.web_id}"
    ])
    
    # ------ URL -------
    url = "https://www.doubao.com/samantha/chat/completion?" + params
    
    # ------ BODY -------
    body = {
        "completion_option": {
            "is_regen": False,
            "with_suggest": False,
            "need_create_conversation": conversation_id is None,
            "launch_stage": 1,
            "use_auto_cot": use_auto_cot,
            "use_deep_think": use_deep_think
        },
        "conversation_id": "0" if conversation_id is None else conversation_id,
        "messages": [
            {
                "content": json.dumps({"text": prompt}),
                "content_type": 2001,
                "attachments": attachments,
                "references": []
            }
        ]
    }
    
    if section_id is not None:
        body["section_id"] = section_id
    
    # 如果是未登录账户，则不需要 local 字段
    if not guest:
        body["local_conversation_id"] = f"local_{int(uuid.uuid4().int % 10000000000000000)}" 
        body["local_message_id"] = str(uuid.uuid4())
    
    # ------ HEADERS -------
    headers = {
        'content-type': 'application/json',
        'accept': 'text/event-stream',
        'agw-js-conv': 'str',
        'cookie': session.cookie,
        'origin': "https://www.doubao.com",
        'referer': f"https://www.doubao.com/chat/{session.room_id}",
        'user-agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/137.0.0.0 Safari/537.36 Edg/137.0.0.0',
        "x-flow-trace": session.x_flow_trace
    }
    try:
        with requests.Session() as req_session:
            response = req_session.post(url=url, headers=headers, json=body, stream=True)
            if response.status_code != 200:
                error_text = response.text
                raise Exception(f"豆包API对话补全失败: {response.status_code}, 详情: {error_text}")
            try:
                # 下一次会话需要同一个session
                text, image_urls, conversation_id, message_id, section_id = handle_sse(response)
                print(f"conversation_id: {conversation_id}")
                session_pool.set_session(conversation_id, session)
                return text, image_urls, conversation_id, message_id, section_id
            except LimitedException:
                session_pool.del_session(session)
                raise HTTPException(status_code=500, detail=f"游客限制5次会话已用完，请重使用新Session")
    except Exception as e:
        import traceback
        traceback.print_exc()


def handle_sse(response):
    """处理SSE流响应"""
    buffer = ""
    conversation_id = ""
    message_id = ""
    section_id = ""
    texts = []
    image_urls = []
    
    for chunk in response.iter_content(chunk_size=1024):
        if chunk:
            buffer += chunk.decode('utf-8', errors='replace')
            
            # 游客限制判断
            if "tourist conversation reach limited" in buffer:
                raise LimitedException()
            
            if 'event: gateway-error' in buffer:
                error_match = buffer.find('data: {')
                if error_match != -1:
                    try:
                        error_data = json.loads(buffer[error_match + 6:].split('\n')[0])
                        raise Exception(f"服务器返回网关错误: {error_data.get('code')} - {error_data.get('message')}")
                    except Exception as e:
                        raise Exception(f"服务器返回网关错误: {buffer}")
            
            events = buffer.split('\n\n')
            buffer = events.pop()
            
            for evt in events:
                lines = evt.strip().split('\n')
                data_line = next((l for l in lines if l.startswith('data: ')), None)
                if not data_line:
                    continue
                    
                try:
                    evt_obj = json.loads(data_line[6:])
                    event_type = evt_obj.get('event_type')
                    event_data = json.loads(evt_obj.get('event_data', '{}'))
                    if event_type == 2001:
                        # 流消息                      
                        if not (msg := event_data.get('message')): continue
                        
                        content_type = msg.get('content_type')
                        if content_type in [10000, 2001, 2008]:
                            # 文字消息
                            text = json.loads(msg.get('content', '{}')).get('text', )
                            if text:
                                texts.append(text)
                        elif content_type == 2074:
                            # 图片消息
                            creations = json.loads(msg.get('content', '{}')).get('creations', [])
                            for creation in creations:
                                image_info = creation.get('image', {})
                                # 只处理status为2的完成图片
                                if image_info.get('status') == 2:
                                    url = (image_info.get('image_raw', {}).get('url') or 
                                            image_info.get('image_thumb', {}).get('url') or
                                            image_info.get('image_ori', {}).get('url'))
                                    
                                    if url and url not in image_urls:
                                        image_urls.append(url)
                        else:
                            pass
                    elif event_type == 2002:
                        # 流开始
                        conversation_id = event_data.get("conversation_id")
                        message_id = event_data.get("message_id")
                        section_id = event_data.get("section_id")
                    elif event_type == 2003:
                        # 流结束
                        text = "".join(texts)
                        text = text.lstrip('\n').rstrip("\n")
                        return text, image_urls, conversation_id, message_id, section_id
                    else:
                        pass
                except Exception as e:
                    raise Exception(f"解析SSE失败: {str(e)}")


def upload_file(file_type: int, file_name: str, file_data: bytes):
    """
    上传文件到豆包服务器，返回附件信息
    总体流程为：
    1. 通过 prepare-upload 拿到 AWS 凭证
    2. 通过 apply-upload 提交文件元信息
    3. 通过 upload 上传文件数据
    4. 通过 commit-upload 确认上传
    """
    # 生成文件与用户无关，随机挑一个session
    session = session_pool.get_session()
    logger.info(f"开始上传文件: {file_name}, 类型: {file_type}, 大小: {len(file_data)} 字节")
    # ------ HEADERS -------
    DEFAULT_HEADERS = {
        'content-type': 'application/json',
        'cookie': session.cookie,
        'origin': "www.doubao.com",
        'referer': "https://www.doubao.com/chat/",
        'user-agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/136.0.0.0 Safari/537.36'
    }
    # ------ PARAMS -------
    params = "&".join([
        "aid=497858",
        f"device_id={session.device_id}",
        "device_platform=web",
        "language=zh",
        "pc_version=2.20.0",
        "pkg_type=release_version",
        "real_aid=497858",
        "region=CN",
        "samantha_web=1",
        "sys_region=CN",
        f"tea_uuid={session.tea_uuid}",
        "use-olympus-account=1",
        "version_code=20800",
    ])
    
    # PREPARE UPLOAD
    prepare_url = "https://www.doubao.com/alice/resource/prepare_upload?" + params
    prepare_payload = {
        "resource_type": file_type,  # 文档类型 1;图片类型 2; 
        "scene_id": "5",
        "tenant_id": "5"
    }
    resp = requests.post(url=prepare_url, headers=DEFAULT_HEADERS, json=prepare_payload)
    prepare_data = resp.json()
    upload_info = prepare_data.get("data", {})
    
    # APPLY UPLOAD
    service_id = upload_info.get("service_id")
    session_token = upload_info.get("upload_auth_token", {}).get("session_token")
    access_key = upload_info.get("upload_auth_token", {}).get("access_key")
    secret_key = upload_info.get("upload_auth_token", {}).get("secret_key")
    file_size = len(file_data)
    if not '.' in file_name:
        raise HTTPException(status_code=500, detail="文件名格式错误，注意附带后缀名")
    file_ext = os.path.splitext(file_name)[1]
    apply_url = f"https://imagex.bytedanceapi.com/?Action=ApplyImageUpload&Version=2018-08-01&ServiceId={service_id}&NeedFallback=true&FileSize={file_size}&FileExtension={file_ext}"
    
    # 构建 AWS4Auth
    auth = AWS4Auth(access_key, secret_key, 'cn-north-1', "imagex", session_token=session_token)
    headers = {
        "origin": "https://www.doubao.com",
        "reference": "https://www.doubao.com",
        "user-agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/136.0.0.0 Safari/537.36",
    }
    resp = requests.get(apply_url, headers=headers, auth=auth)
    data = resp.json()
    upload_address = data.get("Result", {}).get("UploadAddress", {})
    if not (infos := upload_address.get("StoreInfos", [])):
        raise HTTPException(status_code=500, detail="Apply Upload 返回 StoreInfos列表为空")
    store_info = infos[0]
    store_url = store_info.get("StoreUri")
    store_auth = store_info.get("Auth")
    session_key = upload_address.get("SessionKey")
    
    # UPLOAD
    upload_url = f"https://tos-d-x-hl.snssdk.com/upload/v1/{store_url}"
    crc32 = format(binascii.crc32(file_data) & 0xFFFFFFFF, '08x')
    upload_headers = {
        "authorization": store_auth,
        "origin": "https://www.doubao.com",
        "reference": "https://www.doubao.com",
        "host": "tos-d-x-hl.snssdk.com",
        "content-type": "application/octet-stream",
        "content-disposition": 'attachment; filename="undefined"',
        "content-crc32": crc32
    }
    resp = requests.post(upload_url, data=file_data, headers=upload_headers)
    data = resp.json()
    if not (msg := data.get("message")) == "Success":
        raise HTTPException(status_code=500, detail=f"上传消息失败 {msg}")
    
    # COMMIT UPLOAD
    commit_url = f"https://imagex.bytedanceapi.com/?Action=CommitImageUpload&Version=2018-08-01&ServiceId={service_id}"
    commit_payload = {"SessionKey": session_key}
    commit_headers = {
        "origin": "https://www.doubao.com",
        "referer": "https://www.doubao.com/",
        "user-agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/136.0.0.0 Safari/537.36",
    }
    
    resp = requests.post(commit_url, headers=commit_headers, json=commit_payload, auth=auth)
    data = resp.json()
    if not (results := data.get("Result", {}).get("PluginResult", [])):
        raise HTTPException(status_code=500, detail="Commit Upload 返回 PluginResult 为空")
    result = results[0]
    
    # 返回结果
    from shiyunzi.doubao.response import FileResponse, ImageResponse
    if file_type == 1:
        return FileResponse(
            key=result.get("ImageUri"),
            name=file_name,
            md5=result.get("ImageMd5") or hashlib.md5(file_data).hexdigest(),
            size=result.get("ImageSize")
        )
    elif file_type == 2:
        return ImageResponse(
            key=result.get("ImageUri"),
            name=file_name,
            option={
                "height": result.get("ImageHeight"),
                "width": result.get("ImageWidth")
            }
        )


def delete_conversation(conversation_id: str) -> tuple[bool, str]:
    # 获取会话配置
    session = session_pool.get_session(conversation_id)
    if not session:
        raise HTTPException(status_code=404, detail=f"会话配置不存在:, 会话ID: {conversation_id}")
    
    # ------ URL -------
    params = "&".join([
        "aid=497858",
        f"device_id={session.device_id}",
        "device_platform=web",
        "language=zh",
        "pc_version=2.20.0",
        "pkg_type=release_version",
        "real_aid=497858",
        "region=CN",
        "samantha_web=1",
        "sys_region=CN",
        f"tea_uuid={session.tea_uuid}",
        "use-olympus-account=1",
        "version_code=20800",
        f"web_id={session.web_id}",
    ])
    url = "https://www.doubao.com/samantha/thread/delete?" + params
    
    # ------ BODY -------
    body = {"conversation_id": conversation_id}
    
    # ------ HEADERS -------
    headers = {
        "cookie": session.cookie,
        "origin": "https://www.doubao.com",
        "referer": "https://www.doubao.com/chat/" + conversation_id,
        "user-agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/137.0.0.0 Safari/537.36 Edg/137.0.0.0"
    }
    
    try:
        response = requests.post(url, headers=headers, json=body)
        if response.status_code != 200:
            return False, f"请求状态错误: {response.status_code}"
        return True, ""
    except Exception as e:
        return False, f"请求失败: {str(e)}"


class LimitedException(Exception):
    pass


__all__ = [
    "chat_completion",
    "upload_file",
    "delete_conversation"
] 