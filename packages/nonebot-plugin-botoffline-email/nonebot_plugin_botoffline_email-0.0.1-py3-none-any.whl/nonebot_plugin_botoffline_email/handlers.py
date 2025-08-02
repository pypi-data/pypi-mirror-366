# src/nonebot_plugin_bot_offline/handlers.py
import smtplib
import datetime
from email.mime.text import MIMEText
from email.header import Header

from nonebot import on_notice
from nonebot.adapters.onebot.v11 import Bot, NoticeEvent
from nonebot.typing import T_State

from .config import cfg

# 只匹配 notice_type 为 bot_offline 的 notice
bot_offline = on_notice(
    rule=lambda event: event.notice_type == "bot_offline",
    priority=5
)

@bot_offline.handle()
async def _(bot: Bot, event: NoticeEvent, state: T_State):
    dt = datetime.datetime.fromtimestamp(event.time)
    time_str = dt.strftime("%Y-%m-%d %H:%M:%S")

    # 2. 构造精简邮件正文
    body = (
        f"检测到 Bot 下线通知：\n"
        f"时间：{time_str}\n"
        f"QQ 号：{event.user_id}\n"
        f"请及时重新登录。"
    )

    try:
        _send_email("【警告】Bot 已下线", body)
    except Exception as e:
        bot.logger.error(f"发送下线提醒邮件失败：{e}")

def _send_email(subject: str, body: str):
    """使用 smtplib 发送纯文本邮件"""
    msg = MIMEText(body, "plain", "utf-8")
    msg["Subject"] = Header(subject, "utf-8")
    msg["From"] = cfg.email_from
    msg["To"] = cfg.email_to

    with smtplib.SMTP(cfg.smtp_host, cfg.smtp_port) as smtp:
        smtp.starttls()  # 如果 SMTP 服务支持 STARTTLS
        smtp.login(cfg.smtp_user, cfg.smtp_pass)
        smtp.sendmail(cfg.email_from, [cfg.email_to], msg.as_string())
