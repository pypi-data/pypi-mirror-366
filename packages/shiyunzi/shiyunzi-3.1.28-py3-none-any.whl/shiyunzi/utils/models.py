from peewee import *
from datetime import datetime
import sys
import os
from shiyunzi.utils.log_util import get_logger
import uuid

logger = get_logger(__name__)

# 获取数据库目录
if sys.platform == "darwin":  # macOS
    base_path = os.path.expanduser("~/Library/Logs")
elif sys.platform == "win32":  # Windows
    base_path = os.path.expandvars("%LOCALAPPDATA%")
else:  # Fallback for other platforms
    base_path = os.path.expanduser("~/.logs")

db_path = os.path.join(base_path, "shiyunzi", "database")

os.makedirs(db_path, exist_ok=True) # 创建数据库目录

db = SqliteDatabase(os.path.join(db_path, "shiyunzi.db")) # 创建数据库文件

class BaseModel(Model):
    class Meta:
        database = db

# 配置信息表
class Config(BaseModel):
    key = CharField(primary_key=True)
    value = CharField()
    created_at = DateTimeField(default=datetime.now)
    updated_at = DateTimeField(default=datetime.now)
    
    class Meta:
        table_name = "config"

# Runway账号信息表
class RunwayAccount(BaseModel):
    name = CharField()
    token = CharField()
    team_id = CharField()
    type = CharField() # shared共享, exclusive独享
    status = IntegerField() # 0: 正常, 1: 异常
    used = IntegerField() # 已使用次数
    created_at = DateTimeField(default=datetime.now)
    updated_at = DateTimeField(default=datetime.now)
    
    class Meta:
        table_name = "runway_account"

class StableDiffusion(BaseModel):
    name = CharField()
    model = CharField()
    lora = CharField()
    steps = IntegerField()
    cfg = FloatField()
    scheduler = CharField()
    sampler = CharField()
    seed = IntegerField()
    width = IntegerField()
    height = IntegerField()
    created_at = DateTimeField(default=datetime.now)
    updated_at = DateTimeField(default=datetime.now)
    
    class Meta:
        table_name = "stable_diffusion"

class Task(BaseModel):
    type = CharField(null=True) # text2image, image2video, text2video
    status = CharField(null=True) # pending, running, completed, stopped, deleted
    text2image = CharField(null=True) # runway, sd, flux
    image2video = CharField(null=True) # runway
    music_dir = CharField(null=True) # 音乐文件夹路径
    resolution = CharField(null=True) # 16:9, 9:16
    created_at = DateTimeField(default=datetime.now)
    updated_at = DateTimeField(default=datetime.now)
    
    class Meta:
        table_name = "task"

class Work(BaseModel):
    task = ForeignKeyField(Task, backref='works', null=True)
    super_prompt = CharField(null=True) # 可空
    stable_diffusion = ForeignKeyField(StableDiffusion, backref='works', null=True) # 可空
    text2image_prompt = CharField(null=True) # 可空
    text2image_negative_prompt = CharField(null=True) # 可空
    image2video_prompt = CharField(null=True) # 可空
    image_path = CharField(null=True) # 可空
    video_path = CharField(null=True) # 可空
    second = IntegerField(null=True)
    status = CharField(null=True) # pending, running, completed
    created_at = DateTimeField(default=datetime.now)
    updated_at = DateTimeField(default=datetime.now)
    
    class Meta:
        table_name = "work"

def init_db():
    """初始化数据库"""
    try:
        logger.info("开始初始化数据库...")
        db.connect()
        
        # 获取所有表
        tables = [Config, RunwayAccount, StableDiffusion, Task, Work]
        
        # 检查每个表是否存在,不存在则创建
        for table in tables:
            if not db.table_exists(table._meta.table_name):
                logger.info(f"创建表 {table._meta.table_name}")
                db.create_tables([table])
            else:
                logger.info(f"表 {table._meta.table_name} 已存在")
                
        logger.info("数据库初始化完成")

        logger.info("初始化配置数据")
        # 查看配置表中database_version是否存在，不存在则创建
        if not Config.select().where(Config.key == "database_version").exists():
            logger.info("创建数据库版本配置")
            Config.create(key="database_version", value="1.0.0")
            Config.create(key="aicvw_proxy", value="https://aicvw.com")
        else:
            logger.info("数据库版本配置已存在")
        # 如果runway_model不存在，则创建
        if not Config.select().where(Config.key == "runway_model").exists():
            logger.info("创建runway_model配置")
            Config.create(key="runway_model", value="gen3")
        # 如果llm_model不存在，则创建
        if not Config.select().where(Config.key == "llm_model").exists():
            logger.info("创建llm_model配置")
            Config.create(key="llm_model", value="aurora")
        # 如果device_id不存在，则创建
        if not Config.select().where(Config.key == "device_id").exists():
            logger.info("创建device_id配置")
            Config.create(key="device_id", value=str(uuid.uuid4()))
            
    except Exception as e:
        logger.error(f"数据库初始化失败: {str(e)}")
        raise
    finally:
        if not db.is_closed():
            db.close()

# 在模块加载时初始化数据库
init_db()
