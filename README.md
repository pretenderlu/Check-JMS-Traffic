
# JMS流量监控工具

![GitHub license](https://img.shields.io/badge/license-MIT-blue.svg)
![Python Version](https://img.shields.io/badge/python-3.6%2B-blue)

一个适用于青龙面板的JMS流量监控脚本，可实时检查JMS服务的流量使用情况，并通过多种渠道发送提醒通知。

## 📑 功能特点

- 🔍 自动检查JMS服务的流量使用情况
- 📊 计算已用流量、剩余流量及使用百分比
- 📅 显示流量重置日期及剩余天数
- 📱 支持多种通知方式（Server酱、Telegram）
- ⚠️ 当流量使用超过阈值时发出警告
- 🕒 可设置定时自动检查

## 🚀 快速开始

### 在青龙面板中使用

1. 在青龙面板中创建新的Python脚本，命名为`jms_traffic_check.py`
2. 将脚本代码复制到创建的文件中
3. 在"依赖管理"中添加`requests`依赖
4. 在"环境变量"中添加所需的配置信息
5. 设置定时任务（建议每天上午10点运行：`0 10 * * *`）

### 环境变量配置

| 变量名 | 必填 | 说明 |
|-------|------|------|
| `JMS_API_URL` | 是 | JMS API的URL地址 |
| `SERVER_CHAN_KEY` | 否 | Server酱的推送密钥 |
| `TG_BOT_TOKEN` | 否 | Telegram机器人Token |
| `TG_USER_ID` | 否 | Telegram用户ID |

## 📋 使用示例

脚本运行后，将生成类似以下的流量使用报告：

```
## JMS流量使用情况
- 已使用流量: 32.95 GB
- 总流量限制: 931.32 GB
- 剩余流量: 898.37 GB
- 使用比例: 3.54%
- 下次重置日: 2025-05-03 (还有19天)
- 检查时间: 2025-04-14 10:00:05
```

当流量使用超过80%或95%时，将发送特别警告：

- 使用超过80%: "⚠️ JMS流量使用超过80%，请注意"
- 使用超过95%: "🚨 JMS流量使用超过95%，请立即处理"

## 🔧 API数据结构

脚本处理的API返回数据结构如下：

```json
{
  "monthly_bw_limit_b": 1000000000000,  // 月度流量限制(字节)
  "bw_counter_b": 35426454830,         // 已使用流量(字节)
  "bw_reset_day_of_month": 3           // 流量重置日(每月几号)
}
```

## 📲 通知说明

### Server酱通知

1. 访问 [Server酱官网](https://sct.ftqq.com/) 注册并获取推送密钥
2. 将密钥添加到环境变量 `SERVER_CHAN_KEY` 中

### Telegram通知

1. 通过 [BotFather](https://t.me/botfather) 创建一个Telegram机器人并获取Token
2. 获取您的Telegram用户ID（可通过 [@userinfobot](https://t.me/userinfobot) 获取）
3. 将Token和用户ID分别添加到环境变量 `TG_BOT_TOKEN` 和 `TG_USER_ID` 中

## 🔄 从GitHub Actions迁移

本脚本是从GitHub Actions工作流迁移到青龙面板的版本。如果您之前使用的是GitHub Actions版本，主要变化如下：

1. 环境变量名称调整：
   - `TELEGRAM_BOT_TOKEN` → `TG_BOT_TOKEN`
   - `TELEGRAM_CHAT_ID` → `TG_USER_ID`

2. 添加了青龙面板特有的注释格式：
   ```
   cron: 0 10 * * *
   new Env('JMS流量检查');
   ```

## 📝 注意事项

- 请确保青龙面板中的Python版本为3.6或以上
- 至少需要设置`JMS_API_URL`环境变量，通知功能是可选的
- 如果API返回的数据结构有变化，请相应调整脚本中的数据处理逻辑

## 📄 许可证

本项目采用MIT许可证 - 详情请参阅 [LICENSE](LICENSE) 文件
