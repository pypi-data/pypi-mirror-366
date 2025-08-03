# src/nonebot_plugin_botoffline_email/config.py

from pydantic_settings import BaseSettings, SettingsConfigDict
from pydantic import Field

class PluginConfig(BaseSettings):
    smtp_host: str = Field(..., env="SMTP_HOST")
    smtp_port: int = Field(..., env="SMTP_PORT")
    smtp_user: str = Field(..., env="SMTP_USER")
    smtp_pass: str = Field(..., env="SMTP_PASS")
    email_from: str = Field(..., env="EMAIL_FROM")
    email_to: str = Field(..., env="EMAIL_TO")

    # --- 关键改动：忽略 .env 里所有“非 smtp_*”的多余字段 ---
    model_config = SettingsConfigDict(
        env_file = ".env",
        env_file_encoding = "utf-8",
        extra = "ignore",           # 忽略所有多余字段
    )

# 直接从 .env / 环境变量里读取，不用再手动 load_dotenv
cfg = PluginConfig()
