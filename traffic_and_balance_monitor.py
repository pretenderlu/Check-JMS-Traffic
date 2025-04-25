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
    """Server酱³发送通知"""  
    if not SC_UID or not SC_SENDKEY:  
        print("未设置SC_UID或SC_SENDKEY，跳过Server酱通知")  
        return False  
        
    try:  
        # Server酱³ API URL  
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
                print("Server酱³通知发送成功")  
                return True  
            else:  
                print(f"Server酱³通知发送失败: {response_json.get('message')}")  
                return False  
        else:  
            print(f"Server酱³通知发送失败，状态码: {response.status_code}")  
            return False  
    except Exception as e:  
        print(f"Server酱³通知发送错误: {str(e)}")  
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
    print("开始检查项目使用情况...")  
    
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
