import json
import os
import urllib3
import re

# Set the Google Chat Webhook URL from environment variable
GOOGLE_CHAT_WEBHOOK_URL = os.getenv('GOOGLE_CHAT_WEBHOOK_URL')

http = urllib3.PoolManager()

def send_google_chat_notify(message):
    """Send a notification to Google Chat via Webhook."""
    if not GOOGLE_CHAT_WEBHOOK_URL:
        print("Error: GOOGLE_CHAT_WEBHOOK_URL is not set.")
        return 500
    
    headers = {
        'Content-Type': 'application/json'
    }
    payload = {
        'text': message
    }
    
    response = http.request(
        'POST',
        GOOGLE_CHAT_WEBHOOK_URL,
        body=json.dumps(payload),
        headers=headers
    )
    
    return response.status

def send_dm_to_bot(message):
    """ส่งข้อความไปยังแชท 1:1 กับบอทผ่าน Chat API โดยใช้ API Key."""
    bot_space_id = 'spaces/89Mip8AAAAE'  # เปลี่ยนตาม space id ของ 1:1 chat กับบอท
    if not bot_space_id:
        print("Error: ไม่พบ Google Chat Bot Space ID.")
        return 500

    if not GOOGLE_CHAT_API_KEY:
        print("Error: GOOGLE_CHAT_API_KEY is not set.")
        return 500

    headers = {
        'Content-Type': 'application/json'
    }
    payload = {
        'text': message
    }

    # เพิ่ม API Key ใน URL
    url = f'https://chat.googleapis.com/v1/spaces/89Mip8AAAAE/messages?key=AIzaSyDxYTrGFaxd-zxdFtQfDowrtAEbI3OwIG8'

    response = http.request(
        'POST',
        url,
        body=json.dumps(payload),
        headers=headers
    )

    return response.status

def format_message(sns_message_data, sns_topic_arn):
    """Format message based on CloudWatch Alarm type."""
    alarm_name = sns_message_data.get('AlarmName', 'No Alarm Name')
    new_state = sns_message_data.get('NewStateValue', 'Unknown State')
    reason = sns_message_data.get('NewStateReason', 'No reason provided')
    
    app_name = get_app_name_from_sns_arn(sns_topic_arn)

    if new_state == "OK":
        message = (
            f"✅ Alarm Resolved ✅\nApp Name: {app_name}\nAlarm: {alarm_name}\nState: {new_state}\nReason: {reason}\n"
        )
    else:
        message = (
            f"🚨 General Alarm 🚨\nApp Name: {app_name}\nAlarm: {alarm_name}\nState: {new_state}\nReason: {reason}\n"
        )
    return message

def get_app_name_from_sns_arn(topic_arn):
    try:
        match = re.search(r'PRD_(\w+?)_', topic_arn)
        if match:
            extracted_text = match.group(1)  
        else:
            print("Pattern not found")
            extracted_text = "UNKNOWN_APP_NAME"
    except Exception as e:
        print(f"An error occurred: {e}")
        extracted_text = "UNKNOWN_APP_NAME"
    
    return extracted_text

def lambda_handler(event, context):
    """Lambda handler triggered by SNS topic."""
    sns_message = event['Records'][0]['Sns']['Message']
    sns_topic_arn = event['Records'][0]['Sns']['TopicArn']
    
    # Log the full SNS message for troubleshooting
    print(f"SNS Message: {sns_message}")
    
    # Parse the SNS message from the CloudWatch Alarm (if applicable)
    sns_message_data = json.loads(sns_message)
    
    # Format the message for Google Chat
    message = format_message(sns_message_data, sns_topic_arn)
    
    # Send the message to Google Chat
    status = send_google_chat_notify(message)
    
    # Log the result
    return {
        'statusCode': status,
        'body': json.dumps(f'Google Chat Notify response: {status}')
    }
