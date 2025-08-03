# src/nonebot_plugin_bot_offline/__init__.py
# 插件入口，负责加载配置和注册事件
from nonebot import get_driver

# 让 nonebot 扫描到 handlers 中的 on_notice 装饰器
from . import handlers  # noqa: F401

# （可选）校验配置合法性
driver = get_driver()
config = driver.config
if not all(hasattr(config, k) for k in (
    "smtp_host", "smtp_port", "smtp_user", "smtp_pass", "email_from", "email_to"
)):
    raise RuntimeError("请在全局配置或环境变量中添加 SMTP_HOST/SMTP_USER 等字段")
