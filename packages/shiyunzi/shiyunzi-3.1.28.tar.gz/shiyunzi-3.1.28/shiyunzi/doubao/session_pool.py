import os
import json
import random
from pydantic import BaseModel
from shiyunzi.doubao.fetcher import DoubaoAutomator
from shiyunzi.utils.config_util import get_config, set_config
from shiyunzi.utils.log_util import get_logger

logger = get_logger(__name__)

class DoubaoSession(BaseModel):
    """豆包API会话配置"""
    cookie: str
    device_id: str
    tea_uuid: str
    web_id: str
    room_id: str
    x_flow_trace: str
    
    def to_dict(self) -> dict[str, str]:
        """转换为字典"""
        return {
            "cookie": self.cookie,
            "device_id": self.device_id,
            "tea_uuid": self.tea_uuid,
            "web_id": self.web_id,
            "room_id": self.room_id,
            "x_flow_trace": self.x_flow_trace,
        }
    
    @classmethod
    def from_dict(cls, data: dict[str, str]) -> 'DoubaoSession':
        return cls(**data)


class SessionPool:
    """豆包API会话池，管理多个账号配置"""
    def __init__(self, config_file: str = "session.json"):
        # conversation_id -> DoubaoSession
        self.session_map: dict[str, DoubaoSession] = {}
        self.auth_sessions: list[DoubaoSession] = []
        self.guest_sessions: list[DoubaoSession] = [] 
        self.config_file = config_file
        self.load_from_file()
    
    def create_session(
        self,
        guest: bool,
        cookie: str,
        device_id: str,
        tea_uuid: str,
        web_id: str,
        room_id: str,
        x_flow_trace: str
    ) -> DoubaoSession:
        """创建新会话配置"""
        session = DoubaoSession(
            cookie=cookie,
            device_id=device_id,
            tea_uuid=tea_uuid,
            web_id=web_id,
            room_id=room_id,
            x_flow_trace=x_flow_trace
        )
        if guest:
            self.guest_sessions.append(session)
        else:
            self.auth_sessions.append(session)
    
    def get_session(self, conversation_id: str | None = None, guest: bool = False) -> DoubaoSession:
        """获取会话配置，如果不存在则随机"""
        if conversation_id is None:
            if guest:
                return random.choice(self.guest_sessions) if self.guest_sessions else None
            else:
                return random.choice(self.auth_sessions) if self.auth_sessions else None
        else:
            return self.session_map.get(conversation_id)
    
    def set_session(self, conversation_id: str, session: DoubaoSession):
        """将会话与conversation_id关联"""
        self.session_map[conversation_id] = session
    
    def del_session(self, session: DoubaoSession):
        """删除会话"""
        if session.is_logged:
            self.auth_sessions.remove(session)
        else:
            self.guest_sessions.remove(session)
        self.save_to_file()
    
    def save_to_file(self):
        """保存会话配置到"""
        try:
            data = [session.to_dict() for session in (self.auth_sessions + self.guest_sessions)]
            set_config("doubao_cookie", data[0]["cookie"])
            set_config("doubao_device_id", data[0]["device_id"])
            set_config("doubao_tea_uuid", data[0]["tea_uuid"])
            set_config("doubao_web_id", data[0]["web_id"])
            set_config("doubao_room_id", data[0]["room_id"])
            set_config("doubao_x_flow_trace", data[0]["x_flow_trace"])
            logger.debug(f"会话配置已保存到数据库")
        except Exception as e:
            logger.error(f"保存会话配置到数据库失败: {str(e)}")
    
    def load_from_file(self):
        """从数据库加载会话配置"""
        doubao_cookie = get_config("doubao_cookie")
        doubao_device_id = get_config("doubao_device_id")
        doubao_tea_uuid = get_config("doubao_tea_uuid")
        doubao_web_id = get_config("doubao_web_id")
        doubao_room_id = get_config("doubao_room_id")
        doubao_x_flow_trace = get_config("doubao_x_flow_trace")
        
        if doubao_cookie:
            self.create_session(
                guest=False,
                cookie=doubao_cookie,
                device_id=doubao_device_id,
                tea_uuid=doubao_tea_uuid,
                web_id=doubao_web_id,
                room_id=doubao_room_id,
                x_flow_trace=doubao_x_flow_trace
            )
        else:
            logger.warning("未找到豆包API配置，请在设置中配置")

    async def fetch_guest_session(self, num: int):
        for _ in range(num):
            automator = DoubaoAutomator()
            self.create_session(
                guest=True,
                **(await automator.run_automation())
            )


session_pool = SessionPool()
__all__ = [
    "DoubaoSession",
    "SessionPool",
    "session_pool"
] 
