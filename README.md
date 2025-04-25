
# 流量与余额监控工具

![GitHub license](https://img.shields.io/badge/license-MIT-blue.svg)
![Python Version](https://img.shields.io/badge/python-3.6%2B-blue)

一个适用于青龙面板的流量与余额监控工具，可以实时检查JMS服务的流量使用情况，并通过多种渠道发送通知，同时查询DeepSeek的用户账户余额。

## 📑 功能特点

- 🔍 自动检查JMS流量使用情况
- 📊 计算已用流量、剩余流量及使用百分比
- 💵 查询DeepSeek账户余额和充值情况
- 📅 显示流量重置日期及剩余天数
- 📱 支持多种通知方式（Server酱³、Telegram）
- ⚠️ 当流量使用超过阈值时发出警告
- 🕒 可设置定时自动检查

## 🚀 快速开始

### 在青龙面板中使用

1. 在青龙面板中创建新的Python脚本，命名为 `traffic_and_balance_monitor.py`。
2. 将以下代码复制到创建的文件中（请使用最新代码）。
3. 在“依赖管理”中添加 `requests` 依赖。
4. 在“环境变量”中添加所需的配置信息。
5. 设置定时任务（建议每天上午10点运行：`0 10 * * *`）。

### 环境变量配置

在青龙面板的"环境变量"中添加以下变量：

| 变量名 | 必填 | 说明 |
|-------|------|------|
| `JMS_API_URL` | 是 | JMS API的URL地址 |
| `SC_UID` | 否 | Server酱³的UID |
| `SC_SENDKEY` | 否 | Server酱³的SendKey |
| `TG_BOT_TOKEN` | 否 | Telegram机器人Token |
| `TG_USER_ID` | 否 | Telegram用户ID |
| `DEEPSEEK_API_KEY` | 否 | DeepSeek的API密钥 |

## 🔄 更新日志

### 2025-04-25
- 完成项目重命名为流量与余额监控工具，并实现新的功能。
- 更新通知格式，清晰分为“JMS流量使用情况”和“DeepSeek账户余额”。

### 初始版本
- 从GitHub Actions工作流迁移到青龙面板。

## 📝 注意事项

1. 请确保青龙面板中的Python版本为3.6或以上。
2. 至少需要设置`JMS_API_URL`环境变量，通知功能是可选的。
3. 如果API返回的数据结构有变化，请相应调整脚本中的数据处理逻辑。
4. 当使用Server酱³时，需要同时设置`SC_UID`和`SC_SENDKEY`两个环境变量。

## 📄 许可证

本项目采用MIT许可证 - 详情请参阅 [LICENSE](LICENSE) 文件。

