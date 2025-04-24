import requests

WEBHOOK_URL = "https://script.google.com/macros/s/AKfycbyNSEQqkf_zEE8i6DCcnfqeh2Qz7dgFHyHTqL1cUUrMLfNc09dFp5Vjm_t6KWIzI2HL7g/exec"

data = {
    "text": "Hello from Python!",
    "sender": "Python Bot"
}

response = requests.post(WEBHOOK_URL, json=data)
print(f"Webhook Response: {response.status_code} - {response.text}")
