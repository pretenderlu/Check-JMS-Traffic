
# 流量与余额监控工具

![GitHub license](https://img.shields.io/badge/license-MIT-blue.svg)
![Python Version](https://img.shields.io/badge/python-3.6%2B-blue)

一个适用于青龙面板的流量与余额监控工具，可以实时检查JMS服务的流量使用情况，并通过多种渠道发送通知，同时查询DeepSeek的用户账户余额。

## 📑 功能特点

- 🔍 自动检查JMS流量使用情况
- 📊 计算已用流量、剩余流量及使用百分比
- 💵 查询DeepSeek账户余额和充值情况
- 📅 显示流量重置日期及剩余天数
- 📱 支持多种通知方式（Server酱3、Telegram）
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
| `SC_UID` | 否 | Server酱3的UID |
| `SC_SENDKEY` | 否 | Server酱3的SendKey |
| `TG_BOT_TOKEN` | 否 | Telegram机器人Token |
| `TG_USER_ID` | 否 | Telegram用户ID |
| `DEEPSEEK_API_KEY` | 否 | DeepSeek的API密钥 |

## 📋 脚本示例

```python
#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
cron: 0 10 * * *
new Env('流量与余额监控');
"""

import os
import json
import requests
from datetime import datetime

# 从青龙环境变量中获取配置信息
JMS_API_URL = os.environ.get('JMS_API_URL', '')
SC_UID = os.environ.get('SC_UID', '')
SC_SENDKEY = os.environ.get('SC_SENDKEY', '')
TG_BOT_TOKEN = os.environ.get('TG_BOT_TOKEN', '')
TG_USER_ID = os.environ.get('TG_USER_ID', '')
DEEPSEEK_API_KEY = os.environ.get('DEEPSEEK_API_KEY', '')

def check_traffic():
    """检查JMS流量使用情况"""
    try:
        response = requests.get(JMS_API_URL, timeout=10)
        if response.status_code == 200:
            data = response.json()
            return data
        else:
            print(f"API请求失败，状态码: {response.status_code}")
            return None
    except Exception as e:
        print(f"请求发生错误: {str(e)}")
        return None

def get_deepseek_balance():
    """查询DeepSeek API用户余额"""
    if not DEEPSEEK_API_KEY:
        print("未设置DEEPSEEK_API_KEY，无法查询余额")
        return None

    try:
        url = "https://api.deepseek.com/v1/user/balance"
        headers = {
            "Authorization": f"Bearer {DEEPSEEK_API_KEY}"
        }
        response = requests.get(url, headers=headers)
        if response.status_code == 200:
            balance_info = response.json()
            if balance_info.get('is_available') and balance_info.get('balance_infos'):
                # 提取余额信息
                balance_details = balance_info['balance_infos'][0]
                total_balance = balance_details.get('total_balance', '0.00')
                granted_balance = balance_details.get('granted_balance', '0.00')
                topped_up_balance = balance_details.get('topped_up_balance', '0.00')
                return {
                    'total_balance': total_balance,
                    'granted_balance': granted_balance,
                    'topped_up_balance': topped_up_balance
                }
            else:
                print("余额信息不可用或返回格式错误")
                return None
        else:
            print(f"DeepSeek余额查询失败，状态码: {response.status_code}")
            return None
    except Exception as e:
        print(f"余额查询发生错误: {str(e)}")
        return None

def send_server_chan3(title, content, tags=None, short=None):
    """通过Server酱3发送通知"""
    if not SC_UID or not SC_SENDKEY:
        print("未设置SC_UID或SC_SENDKEY，跳过Server酱通知")
        return False
        
    try:
        # Server酱3 API URL
        server_url = f"https://{SC_UID}.push.ft07.com/send/{SC_SENDKEY}.send"
        
        # 准备发送的数据
        params = {
            'title': title,      # 推送标题
            'desp': content      # 推送内容，支持markdown
        }
        
        # 如果有标签和简短描述，添加到参数中
        if tags:
            params['tags'] = tags
        if short:
            params['short'] = short
        
        # 发送POST请求
        response = requests.post(server_url, data=params)
        
        # 检查响应
        if response.status_code == 200:
            response_json = response.json()
            if response_json.get('code') == 0:
                print("Server酱3通知发送成功")
                return True
            else:
                print(f"Server酱3通知发送失败: {response_json.get('message')}")
                return False
        else:
            print(f"Server酱3通知发送失败，状态码: {response.status_code}")
            return False
    except Exception as e:
        print(f"Server酱3通知发送错误: {str(e)}")
        return False

def send_telegram(message):
    """通过Telegram发送通知"""
    if not TG_BOT_TOKEN or not TG_USER_ID:
        print("未设置TG_BOT_TOKEN或TG_USER_ID，跳过Telegram通知")
        return False
        
    try:
        telegram_url = f"https://api.telegram.org/bot{TG_BOT_TOKEN}/sendMessage"
        params = {
            'chat_id': TG_USER_ID,
            'text': message,
            'parse_mode': 'Markdown'
        }
        response = requests.post(telegram_url, data=params)
        if response.status_code == 200:
            print("Telegram通知发送成功")
            return True
        else:
            print(f"Telegram通知发送失败: {response.text}")
            return False
    except Exception as e:
        print(f"Telegram通知发送错误: {str(e)}")
        return False

def bytes_to_gb(bytes_value):
    """将字节转换为GB，保留2位小数"""
    return round(bytes_value / (1024 ** 3), 2)

def main():
    print("开始检查JMS流量使用情况...")
    
    # 检查配置
    if not JMS_API_URL:
        print("错误: 未设置JMS_API_URL环境变量")
        return
    
    # 查询流量
    data = check_traffic()
    if not data:
        message_title = "JMS流量检查失败"
        message_content = "无法获取JMS流量数据，请检查API地址是否正确。"
    else:
        # 根据实际API返回的字段进行处理
        try:
            monthly_limit_bytes = data.get('monthly_bw_limit_b', 0)
            used_bytes = data.get('bw_counter_b', 0)
            reset_day = data.get('bw_reset_day_of_month', 1)
            
            # 转换为GB以便于阅读
            monthly_limit_gb = bytes_to_gb(monthly_limit_bytes)
            used_gb = bytes_to_gb(used_bytes)
            remaining_gb = monthly_limit_gb - used_gb
            
            # 获取当前日期
            today = datetime.now()
            
            # 计算下次重置日期
            reset_date = today.replace(day=reset_day) if today.day < reset_day else today.replace(month=today.month % 12 + 1, day=reset_day)
            
            message_title = "流量与余额监控报告"
            message_content = f"""
## JMS流量使用情况
- 已使用流量: **{used_gb} GB**
- 总流量限制: **{monthly_limit_gb} GB**
- 剩余流量: **{remaining_gb} GB**
- 下次重置日: **{reset_date.strftime('%Y-%m-%d')}**
- 检查时间: **{today.strftime('%Y-%m-%d %H:%M:%S')}**
            """
            
            # 检查DeepSeek余额
            deepseek_balance_info = get_deepseek_balance()
            if deepseek_balance_info is not None:
                total_balance = deepseek_balance_info['total_balance']
                granted_balance = deepseek_balance_info['granted_balance']
                topped_up_balance = deepseek_balance_info['topped_up_balance']
                message_content += f"""
## DeepSeek账户余额
- 账户总余额: **{total_balance} CNY**
- 授予余额: **{granted_balance} CNY**
- 充值余额: **{topped_up_balance} CNY**
                """

            # 根据流量使用情况设置通知标题
            percentage = (used_bytes / monthly_limit_bytes * 100) if monthly_limit_bytes > 0 else 0
            if percentage > 80:
                message_title = "⚠️ 流量使用超过80%，请注意"
            elif percentage > 95:
                message_title = "🚨 流量使用超过95%，请立即处理"

        except Exception as e:
            message_title = "流量数据处理错误"
            message_content = f"在处理返回的流量数据时出错: {str(e)}\n原始数据: {json.dumps(data)}"
    
    # 输出结果
    print(message_title)
    print(message_content)
    
    # 发送通知
    send_server_chan3(message_title, message_content)
    send_telegram(f"*{message_title}*\n\n{message_content}")

if __name__ == "__main__":
    main()
```

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
4. 当使用Server酱3时，需要同时设置`SC_UID`和`SC_SENDKEY`两个环境变量。

## 📄 许可证

本项目采用MIT许可证 - 详情请参阅 [LICENSE](LICENSE) 文件。

