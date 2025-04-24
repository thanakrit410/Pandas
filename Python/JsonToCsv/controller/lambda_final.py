import json
import os
import urllib3
import boto3

GOOGLE_CHAT_WEBHOOK_URL = os.getenv('GOOGLE_CHAT_WEBHOOK_URL')
GOOGLE_SHEET_WEBAPP_URL = "https://script.google.com/macros/s/AKfycbz3SKz-zBHYWQS-brt7ZXkKKs-zZ29C4pTIu5bHCbEM_eaHYJj9z1CaWaiv2XzUtCJmTQ/exec"

http = urllib3.PoolManager()
sns_client = boto3.client('sns')

DEFAULT_APP_NAME = "Unknow"  # Default if no 'Project' tag is found

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

def send_google_chat_notify(message):
    """Send a notification to Google Chat via Webhook."""
    if not GOOGLE_CHAT_WEBHOOK_URL:
        print("Error: GOOGLE_CHAT_WEBHOOK_URL is not set.")
        return 500
    
    headers = {'Content-Type': 'application/json'}
    payload = {'text': message}

    try:
        response = http.request('POST', GOOGLE_CHAT_WEBHOOK_URL, body=json.dumps(payload), headers=headers)
        print(f"Google Chat API Response: {response.status}")
        return response.status
    except Exception as e:
        print(f"Error sending notification: {e}")
        return 500

def get_app_name_from_sns_tag(topic_arn):
    try:
        response = sns_client.list_tags_for_resource(ResourceArn=topic_arn)
        tags = response.get('Tags', [])
        
        # print(f"Fetched SNS Tags: {tags}")

        for tag in tags:
            print(f"Checking Tag -> Key: {tag['Key']}, Value: {tag['Value']}")
            if tag['Key'] == 'Project':  
                print(f"✅ Found Project Tag: {tag['Value']}")
                return tag['Value']

        return DEFAULT_APP_NAME  

    except Exception as e:
        return DEFAULT_APP_NAME


def lambda_handler(event, context):
    """Lambda function to process SNS event and send Google Chat notifications."""
    try:
        record = event.get('Records', [{}])[0].get('Sns', {})
        sns_message = record.get('Message', '{}')
        sns_topic_arn = record.get('TopicArn', 'Unknown ARN')

        print(f"Received SNS Message: {sns_message}")

        sns_message_data = json.loads(sns_message)

        app_name = get_app_name_from_sns_tag(sns_topic_arn)
        alarm_details = {
            "Alarm Name": sns_message_data.get('AlarmName', 'No Alarm Name'),
            "State": sns_message_data.get('NewStateValue', 'Unknown State'),
            "Reason": sns_message_data.get('NewStateReason', 'No reason provided'),
            "Description": sns_message_data.get('AlarmDescription', 'No Alarm Description')
        }

        if alarm_details["State"] == "OK":
            message = f"✅ Alarm Resolved ✅\nApp: {app_name}\nAlarm: {alarm_details['Alarm Name']}\nState: {alarm_details['State']}\nReason: {alarm_details['Reason']}\n"
        elif alarm_details["State"] == "ALARM":
            message = f"🚨 General Alarm 🚨\nApp Name: {app_name}\nAlarm: {alarm_details['Alarm Name']}\nState: {alarm_details['State']}\nReason: {alarm_details['Reason']}\n"
        else:
            message = f"🚫 Insufficient Data Alarm 🚫\nApp Name: {app_name}\nAlarm: {alarm_details['Alarm Name']}\nState: {alarm_details['State']}\nReason: {alarm_details['Reason']}\n"



        sheet_payload = {"text": message , "sender": "AWS-infrabot"}
        sheet_status = send_to_google_sheet(sheet_payload)
        status = send_google_chat_notify(message)


        return {
            'statusCode': 200,
            'body': json.dumps({'google_chat_status': status,'google_sheet_status': sheet_status})
        }
    
    except Exception as e:
        print(f"Error in lambda_handler: {e}")
        return {'statusCode': 500, 'body': json.dumps({'error': str(e)})}
