import json
import os
import urllib3
import jwt
import time

http = urllib3.PoolManager()

# ====== SETUP ======
# Load Service Account JSON from environment variable
SERVICE_ACCOUNT_JSON = os.getenv("GOOGLE_SERVICE_ACCOUNT_JSON")
SERVICE_ACCOUNT_INFO = json.loads(SERVICE_ACCOUNT_JSON)

# Space ID for the Bot DM (1:1 conversation ID)
BOT_DM_SPACE_ID = os.getenv("BOT_DM_SPACE_ID")  # Example: spaces/AAAAB3Nza...

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

def send_message_to_bot(message, access_token, space_id):
    """Send message to Google Chat Bot (1:1 DM)"""
    url = f"https://chat.googleapis.com/v1/{space_id}/messages"
    headers = {
        "Authorization": f"Bearer {access_token}",
        "Content-Type": "application/json"
    }
    payload = {
        "text": message
    }
    response = http.request("POST", url, headers=headers, body=json.dumps(payload))
    print("Bot DM Response:", response.status, response.data.decode("utf-8"))
    return response.status

def lambda_handler(event, context):
    # Sample test message to send
    test_message = "Hello, this is a test message sent to the bot in 1:1 chat!"

    # Request access token
    access_token = get_access_token_from_service_account()

    # Send DM to Bot via 1:1 chat using space ID
    dm_status = send_message_to_bot(test_message, access_token, BOT_DM_SPACE_ID)

    return {
        'statusCode': 200,
        'body': json.dumps(f'DM sent to Bot with status: {dm_status}')
    }
