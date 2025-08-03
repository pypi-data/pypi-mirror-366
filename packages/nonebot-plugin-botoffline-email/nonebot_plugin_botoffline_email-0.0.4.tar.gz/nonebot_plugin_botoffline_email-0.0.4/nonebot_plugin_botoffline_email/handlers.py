# src/nonebot_plugin_bot_offline/handlers.py
import smtplib
import datetime
from email.mime.text import MIMEText
from email.header import Header

from nonebot import on_notice
from nonebot import get_bots
from nonebot_plugin_apscheduler import scheduler
from nonebot.log import logger
from nonebot.adapters.onebot.v11 import Bot, NoticeEvent
from nonebot.typing import T_State

from .config import cfg

_failure_count = 0
_email_sent = False

# 只匹配 notice_type 为 bot_offline 的 notice
bot_offline = on_notice(
    rule=lambda event: event.notice_type == "bot_offline",
    priority=5
)

@bot_offline.handle()
async def _(bot: Bot, event: NoticeEvent, state: T_State):
    global _email_sent
    dt = datetime.datetime.fromtimestamp(event.time)
    time_str = dt.strftime("%Y-%m-%d %H:%M:%S")

    # 2. 构造精简邮件正文
    body = (
        f"检测到 Bot 下线通知：\n"
        f"时间：{time_str}\n"
        f"QQ 号：{event.user_id}\n"
        f"请及时重新登录"
    )

    try:
        _send_email("【警告】Bot 已下线", body)
        _email_sent = True
    except Exception as e:
        logger.error(f"发送下线提醒邮件失败：{e}")

def _send_email(subject: str, body: str):
    """使用 smtplib 发送纯文本邮件"""
    msg = MIMEText(body, "plain", "utf-8")
    msg["Subject"] = Header(subject, "utf-8")
    msg["From"] = cfg.email_from
    msg["To"] = cfg.email_to

    with smtplib.SMTP(cfg.smtp_host, cfg.smtp_port) as smtp:
        smtp = smtplib.SMTP(cfg.smtp_host, cfg.smtp_port, timeout=10)
        try:
            smtp.starttls()  # 如果 SMTP 服务支持 STARTTLS
            smtp.login(cfg.smtp_user, cfg.smtp_pass)
            smtp.sendmail(cfg.email_from, [cfg.email_to], msg.as_string())
        finally:
            smtp.close()

# 每 90 秒执行一次
@scheduler.scheduled_job("interval", seconds=90, id="bot_offline_silent_check")
async def _check_bot_silent_offline():
    global _failure_count, _email_sent
    bots = get_bots()
    if not bots:
        logger.warning("没有可用的 Bot 实例，跳过静默掉线检测")
        return
    bot = next(iter(bots.values()))

    try:
        await bot.call_api(
            "send_private_msg",
            user_id=bot.self_id,
            message="Bot静默掉线检测"
        )
    except Exception as e:
        _failure_count += 1
        logger.warning(f"第 {_failure_count} 次静默检测失败: {e!r}")
        if not _email_sent and _failure_count >= 3:
            now = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
            subject = "【警告】Bot 静默掉线"
            body = (
                f"检测到 Bot 静默掉线：\n"
                f"时间：{now}\n"
                f"QQ 号：{bot.self_id}\n"
                f"连续三次调用API返回失败\n"
                f"请及时检查Bot状态"
            )
            _send_email(subject, body)
            _email_sent = True
            logger.error("已发送静默掉线邮件提醒")
    else:
        logger.info("静默检测正常")
        _failure_count = 0
        _email_sent = False
