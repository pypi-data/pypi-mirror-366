from shiyunzi.utils.models import Config
from shiyunzi.utils.log_util import get_logger

logger = get_logger(__name__)

# 设置配置
def set_config(key, value):
    config = Config.get_or_none(Config.key == key)
    if config:
        config.value = value
        config.save()
    else:
        Config.create(key=key, value=value)

# 获取配置
def get_config(key):
    config = Config.get_or_none(Config.key == key)
    if config:
        return config.value
    return None