#!/usr/bin/env python3  
# -*- coding: utf-8 -*-  

"""  
cron: 0 10 * * *  
new Env('JMS流量检查');  
"""  

import os  
import json  
import requests  
from datetime import datetime  

# 从青龙环境变量中获取配置信息  
JMS_API_URL = os.environ.get('JMS_API_URL', '')  
SERVER_CHAN_KEY = os.environ.get('SERVER_CHAN_KEY', '')  
TG_BOT_TOKEN = os.environ.get('TG_BOT_TOKEN', '')  
TG_USER_ID = os.environ.get('TG_USER_ID', '')  

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

def send_server_chan(title, desp):  
    """通过Server酱发送通知"""  
    if not SERVER_CHAN_KEY:  
        print("未设置SERVER_CHAN_KEY，跳过Server酱通知")  
        return False  
        
    try:  
        server_url = f"https://sctapi.ftqq.com/{SERVER_CHAN_KEY}.send"  
        params = {  
            'title': title,  
            'desp': desp  
        }  
        response = requests.post(server_url, data=params)  
        if response.status_code == 200:  
            print("Server酱通知发送成功")  
            return True  
        else:  
            print(f"Server酱通知发送失败: {response.text}")  
            return False  
    except Exception as e:  
        print(f"Server酱通知发送错误: {str(e)}")  
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
    
    # 检查流量  
    data = check_traffic()  
    if not data:  
        message_title = "JMS流量检查失败"  
        message_content = "无法获取JMS流量数据，请检查API地址是否正确。"  
    else:  
        # 根据实际API返回的字段进行处理  
        try:  
            # API返回的字段:  
            # monthly_bw_limit_b: 月度流量限制(字节)  
            # bw_counter_b: 已使用流量(字节)  
            # bw_reset_day_of_month: 流量重置日(每月几号)  
            
            monthly_limit_bytes = data.get('monthly_bw_limit_b', 0)  
            used_bytes = data.get('bw_counter_b', 0)  
            reset_day = data.get('bw_reset_day_of_month', 1)  
            
            # 转换为GB以便于阅读  
            monthly_limit_gb = bytes_to_gb(monthly_limit_bytes)  
            used_gb = bytes_to_gb(used_bytes)  
            
            # 计算使用百分比  
            percentage = (used_bytes / monthly_limit_bytes * 100) if monthly_limit_bytes > 0 else 0  
            
            # 计算剩余流量  
            remaining_gb = monthly_limit_gb - used_gb  
            
            # 获取当前日期  
            today = datetime.now()  
            current_day = today.day  
            current_month = today.month  
            current_year = today.year  
            
            # 计算下次重置日期  
            if current_day < reset_day:  
                reset_date = datetime(current_year, current_month, reset_day)  
            else:  
                # 如果当前日期已过重置日，则下次重置在下个月  
                if current_month == 12:  
                    reset_date = datetime(current_year + 1, 1, reset_day)  
                else:  
                    reset_date = datetime(current_year, current_month + 1, reset_day)  
            
            days_until_reset = (reset_date - today).days  
            
            message_title = "JMS流量使用情况"  
            message_content = f"""  
## JMS流量使用情况  
- 已使用流量: {used_gb} GB  
- 总流量限制: {monthly_limit_gb} GB  
- 剩余流量: {remaining_gb} GB  
- 使用比例: {percentage:.2f}%  
- 下次重置日: {reset_date.strftime('%Y-%m-%d')} (还有{days_until_reset}天)  
- 检查时间: {today.strftime('%Y-%m-%d %H:%M:%S')}  
            """  
            
            # 根据使用比例设置不同的通知标题  
            if percentage > 80:  
                message_title = "⚠️ JMS流量使用超过80%，请注意"  
            if percentage > 95:  
                message_title = "🚨 JMS流量使用超过95%，请立即处理"  
                
        except Exception as e:  
            message_title = "JMS流量数据处理错误"  
            message_content = f"在处理返回的流量数据时出错: {str(e)}\n原始数据: {json.dumps(data)}"  
    
    # 输出结果  
    print(message_title)  
    print(message_content)  
    
    # 发送通知  
    send_server_chan(message_title, message_content)  
    send_telegram(f"*{message_title}*\n\n{message_content}")  

if __name__ == "__main__":  
    main()