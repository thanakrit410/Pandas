import json
import os
import urllib3
import re
import jwt
import time

http = urllib3.PoolManager()

# ====== SETUP ======
# Load Service Account JSON from environment variable
SERVICE_ACCOUNT_JSON = os.getenv("GOOGLE_SERVICE_ACCOUNT_JSON")
SERVICE_ACCOUNT_INFO = json.loads(SERVICE_ACCOUNT_JSON)

# Webhook URL from environment variable
GOOGLE_CHAT_WEBHOOK_URL = os.getenv('GOOGLE_CHAT_WEBHOOK_URL')

# Space ID for 1:1 chat (DM)
BOT_DM_SPACE_ID = os.getenv("BOT_DM_SPACE_ID")  # Example: 'spaces/AAAAB3NzaC1yc2EAAAADAQABAAABAQ...'

# ====== FUNCTIONS ======

def get_access_token_from_service_account():
    """Request access token using JWT and Service Account"""
    now = int(time.time())
    payload = {
        "iss": SERVICE_ACCOUNT_INFO["client_email"],
        "scope": "https://www.googleapis.com/auth/chat.bot",
        "aud": "https://oauth2.googleapis.com/token",
        "iat": now,
        "exp": now + 3600
    }
    additional_headers = {
        "kid": SERVICE_ACCOUNT_INFO.get("private_key_id")
    }
    signed_jwt = jwt.encode(
        payload,
        SERVICE_ACCOUNT_INFO["private_key"],
        algorithm="RS256",
        headers=additional_headers
    )
    token_url = "https://oauth2.googleapis.com/token"
    token_req_body = {
        "grant_type": "urn:ietf:params:oauth:grant-type:jwt-bearer",
        "assertion": signed_jwt
    }
    response = http.request(
        "POST",
        token_url,
        headers={"Content-Type": "application/x-www-form-urlencoded"},
        body=urllib3.request.urlencode(token_req_body)
    )
    result = json.loads(response.data.decode("utf-8"))
    return result.get("access_token")

def send_google_chat_notify(message):
    if not GOOGLE_CHAT_WEBHOOK_URL:
        print("Error: GOOGLE_CHAT_WEBHOOK_URL is not set.")
        return 500

    headers = { 'Content-Type': 'application/json' }
    payload = { 'text': message }

    response = http.request(
        'POST',
        GOOGLE_CHAT_WEBHOOK_URL,
        body=json.dumps(payload),
        headers=headers
    )
    return response.status

def send_dm_to_bot(message, access_token, space_id):
    url = f"https://chat.googleapis.com/v1/{space_id}/messages"
    headers = {
        "Authorization": f"Bearer {access_token}",
        "Content-Type": "application/json"
    }
    payload = {
        "text": message
    }
    response = http.request("POST", url, headers=headers, body=json.dumps(payload))
    print("DM Response:", response.status, response.data.decode("utf-8"))
    return response.status

def format_message(sns_message_data, sns_topic_arn):
    alarm_name = sns_message_data.get('AlarmName', 'No Alarm Name')
    new_state = sns_message_data.get('NewStateValue', 'Unknown State')
    reason = sns_message_data.get('NewStateReason', 'No reason provided')
    app_name = get_app_name_from_sns_arn(sns_topic_arn)
    if new_state == "OK":
        return f"✅ Alarm Resolved ✅\nApp Name: {app_name}\nAlarm: {alarm_name}\nState: {new_state}\nReason: {reason}\n"
    else:
        return f"🚨 General Alarm 🚨\nApp Name: {app_name}\nAlarm: {alarm_name}\nState: {new_state}\nReason: {reason}\n"

def get_app_name_from_sns_arn(topic_arn):
    try:
        match = re.search(r'PRD_(\w+?)_', topic_arn)
        return match.group(1) if match else "UNKNOWN_APP_NAME"
    except Exception as e:
        print(f"ARN parse error: {e}")
        return "UNKNOWN_APP_NAME"

def lambda_handler(event, context):
    sns_message = event['Records'][0]['Sns']['Message']
    sns_topic_arn = event['Records'][0]['Sns']['TopicArn']
    print(f"SNS Message: {sns_message}")
    sns_message_data = json.loads(sns_message)
    message = format_message(sns_message_data, sns_topic_arn)

    webhook_status = send_google_chat_notify(message)

    # Request access token and send DM
    access_token = get_access_token_from_service_account()
    dm_status = send_dm_to_bot(message, access_token, BOT_DM_SPACE_ID)

    return {
        'statusCode': 200,
        'body': json.dumps(f'Webhook: {webhook_status}, DM: {dm_status}')
    }
