<div align="center">
  <a href="https://v2.nonebot.dev/store"><img src="https://github.com/A-kirami/nonebot-plugin-template/blob/resources/nbp_logo.png" width="180" height="180" alt="NoneBotPluginLogo"></a>
  <br>
  <p><img src="https://github.com/A-kirami/nonebot-plugin-template/blob/resources/NoneBotPlugin.svg" width="240" alt="NoneBotPluginText"></p>
</div>

<div align="center">

# nonebot-plugin-botoffline-email

_✨ QQ bot掉线后使用SMTP发送邮件提醒 ✨_


<a href="./LICENSE">
    <img src="https://img.shields.io/github/license/owner/nonebot-plugin-botoffline-email.svg" alt="license">
</a>
<a href="https://pypi.python.org/pypi/nonebot-plugin-botoffline-email">
    <img src="https://img.shields.io/pypi/v/nonebot-plugin-botoffline-email.svg" alt="pypi">
</a>
<img src="https://img.shields.io/badge/python-3.9+-blue.svg" alt="python">

</div>

## 📖 介绍

QQ bot掉线后使用SMTP发送邮件提醒，可自定义配置任意SMTP服务器以及接受邮箱

## 💿 安装

<details open>
<summary>使用 nb-cli 安装</summary>
在 nonebot2 项目的根目录下打开命令行, 输入以下指令即可安装

    nb plugin install nonebot-plugin-botoffline-email

</details>

<details>
<summary>使用包管理器安装</summary>
在 nonebot2 项目的插件目录下, 打开命令行, 根据你使用的包管理器, 输入相应的安装命令

<details>
<summary>pip</summary>

    pip install nonebot-plugin-botoffline-email
</details>
<details>
<summary>pdm</summary>

    pdm add nonebot-plugin-botoffline-email
</details>
<details>
<summary>poetry</summary>

    poetry add nonebot-plugin-botoffline-email
</details>
<details>
<summary>conda</summary>

    conda install nonebot-plugin-botoffline-email
</details>

打开 nonebot2 项目根目录下的 `pyproject.toml` 文件, 在 `[tool.nonebot]` 部分追加写入

    plugins = ["nonebot-plugin-botoffline-email"]

</details>

## ⚙️ 配置

在 nonebot2 项目的`.env`文件中添加下表中的必填配置

| 配置项 | 必填 | 默认值 | 说明 |
|:-----:|:----:|:----:|:----:|
| smtp_host | 是 | 无 | smtp的发送邮件服务器 |
| smtp_port | 否 | 587 | smtp的发送邮件服务器端口 |
| smtp_user | 是 | 无 | smtp的发送邮箱 |
| smtp_pass | 是 | 无 | smtp的发送邮箱密码 |
| email_from | 是 | 无 | 发出邮箱 |
| email_to | 是 | 无 | 接收邮箱 |
