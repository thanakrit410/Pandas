import json
import os
import urllib3
import re

# Set the Google Chat Webhook URL from environment variable
GOOGLE_CHAT_WEBHOOK_URL = os.getenv('GOOGLE_CHAT_WEBHOOK_URL')
GOOGLE_SHEET_WEBAPP_URL = "https://script.google.com/macros/s/AKfycbyNSEQqkf_zEE8i6DCcnfqeh2Qz7dgFHyHTqL1cUUrMLfNc09dFp5Vjm_t6KWIzI2HL7g/exec"

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


def send_to_google_sheet(data):
    """Send message to Google Sheets via Apps Script Web App"""
    if not GOOGLE_SHEET_WEBAPP_URL:
        print("Error: GOOGLE_SHEET_WEBAPP_URL is not set.")
        return 500

    headers = {'Content-Type': 'application/json'}

    response = http.request(
        'POST',
        GOOGLE_SHEET_WEBAPP_URL,
        body=json.dumps(data),
        headers=headers
    )

    print(f"Google Sheets Response: {response.status}")
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


    sheet_payload = {"message": message , "sender": "AWS-infrabot"}
    sheet_status = send_to_google_sheet(sheet_payload)

    
    
    # Log the result
    return {
        'statusCode': 200,
        'body': json.dumps({
            'google_chat_status': status,
            'google_sheet_status': sheet_status
        })
    }
