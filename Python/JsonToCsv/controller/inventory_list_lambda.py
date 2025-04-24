import boto3
import zipfile
import os
import requests
from datetime import datetime

s3 = boto3.client("s3")

# Config
source_files = [
    {
        "bucket": "atlas-workloads-dev-sit-inventory-list-bucket",
        "key": "ATLAS Workloads dev-sit.xlsx",
        "filename": "ATLAS Workloads dev-sit.xlsx",
    },
    {
        "bucket": "atlas-workloads-prd-inventory-list-bucket",
        "key": "ATLAS Workloads PRD.xlsx",
        "filename": "ATLAS Workloads PRD.xlsx",
    },
    {
        "bucket": "atlas-workloads-uat-inventory-list-bucket",
        "key": "ATLAS Workloads uat.xlsx",
        "filename": "ATLAS Workloads uat.xlsx",
    },
    {
        "bucket": "autobacs-workloads-dev-sit-inventory-list-bucket",
        "key": "AUTOBACS Workloads dev-sit.xlsx",
        "filename": "AUTOBACS Workloads dev-sit.xlsx",
    },
    {
        "bucket": "autobacs-workloads-prd-inventory-list-bucket",
        "key": "AUTOBACS Workloads PRD.xlsx",
        "filename": "AUTOBACS Workloads PRD.xlsx",
    },
    {
        "bucket": "autobacs-workloads-uat-inventory-list-bucket",
        "key": "AUTOBACS Workloads uat-qas.xlsx",
        "filename": "AUTOBACS Workloads uat-qas.xlsx",
    },
    {
        "bucket": "maxme-workloads-dev-sit-inventory-list-bucket",
        "key": "MAXME Workloads dev-sit.xlsx",
        "filename": "MAXME Workloads dev-sit.xlsx",
    },
    {
        "bucket": "maxme-workloads-prd-inventory-list-bucket",
        "key": "MAXME Workloads PRD.xlsx",
        "filename": "MAXME Workloads PRD.xlsx",
    },
    {
        "bucket": "maxme-workloads-uat-inventory-list-bucket",
        "key": "MAXME Workloads uat-qas.xlsx",
        "filename": "MAXME Workloads uat-qas.xlsx",
    },
    {
        "bucket": "maxventures-workloads-dev-sit-inventory-list-bucket",
        "key": "MAXVENTURES Workloads dev-sit.xlsx",
        "filename": "MAXVENTURES Workloads dev-sit.xlsx",
    },
    {
        "bucket": "maxventures-workloads-prd-inventory-list-bucket",
        "key": "MAXVENTURES Workloads PRD.xlsx",
        "filename": "MAXVENTURES Workloads PRD.xlsx",
    },
    {
        "bucket": "maxventures-workloads-uat-inventory-list-bucket",
        "key": "MAXVENTURES Workloads uat-qas.xlsx",
        "filename": "ATLAS Workloads dev-sit.xlsx",
    },
    {
        "bucket": "ptc-workloads-dev-sit-inventory-list-bucket",
        "key": "PTC Workloads dev-sit.xlsx",
        "filename": "PTC Workloads dev-sit.xlsx",
    },
    {
        "bucket": "ptc-workloads-prd-inventory-list-bucket",
        "key": "PTC Workloads PRD.xlsx",
        "filename": "PTC Workloads PRD.xlsx",
    },
    {
        "bucket": "ptc-workloads-uat-inventory-list-bucket",
        "key": "PTC Workloads uat-qas.xlsx",
        "filename": "PTC Workloads uat-qas.xlsx",
    },
    {
        "bucket": "ptg-workloads-dev-sit-inventory-list-bucket",
        "key": "PTG Workloads dev-sit.xlsx",
        "filename": "PTG Workloads dev-sit.xlsx",
    },
    {
        "bucket": "ptg-workloads-prd-inventory-list-bucket",
        "key": "PTG Workloads PRD.xlsx",
        "filename": "PTG Workloads PRD.xlsx",
    },
    {
        "bucket": "ptg-workloads-uat-inventory-list-bucket",
        "key": "PTG Workloads uat-qas.xlsx",
        "filename": "PTG Workloads uat-qas.xlsx",
    },
    {
        "bucket": "retails-workloads-dev-sit-inventory-list-bucket",
        "key": "RETAILS Workloads dev-sit.xlsx",
        "filename": "RETAILS Workloads dev-sit.xlsx",
    },
    {
        "bucket": "retails-workloads-prd-inventory-list-bucket",
        "key": "RETAILS Workloads PRD.xlsx",
        "filename": "RETAILS Workloads PRD.xlsx",
    },
    {
        "bucket": "retails-workloads-uat-inventory-list-bucket",
        "key": "RETAILS Workloads uat-qas.xlsx",
        "filename": "RETAILS Workloads uat-qas.xlsx",
    },
    {
        "bucket": "data-management-dev-sit-inventory-list-bucket",
        "key": "DATA Management dev-sit.xlsx",
        "filename": "DATA Management dev-sit.xlsx",
    },
    {
        "bucket": "data-management-prd-inventory-list-bucket",
        "key": "DATA Management PRD.xlsx",
        "filename": "DATA Management PRD.xlsx",
    },
    {
        "bucket": "data-management-uat-inventory-list-bucket",
        "key": "DATA Management uat-qas.xlsx",
        "filename": "DATA Management uat-qas.xlsx",
    }
]

target_bucket = "central-menetment-inventory-list-bucket"
target_zip_key = "aws_inventory_list.zip"
google_chat_webhook = "https://chat.googleapis.com/v1/spaces/AAAAve9tFZo/messages?key=AIzaSyDdI0hCZtE6vySjMm-WEfRq3CPzqKqqsHI&token=uJWuHGU9TrXJFa8j0xGdSspl4av2wip_MA3nNK37J3g"


import os
import zipfile
import boto3
import requests
from datetime import datetime

s3 = boto3.client("s3")

def lambda_handler(event, context):
    tmp_dir = "/tmp"
    today = datetime.now().strftime("%d/%m/%Y")
    zip_filename = f"aws_inventory_list.zip"
    zip_path = os.path.join(tmp_dir, zip_filename)


    with zipfile.ZipFile(zip_path, "w") as zipf:
        for file in source_files:
            local_file_path = os.path.join(tmp_dir, file["filename"])
            s3.download_file(file["bucket"].strip(), file["key"].strip(), local_file_path)
            zipf.write(local_file_path, arcname=file["filename"])

    s3.upload_file(zip_path, target_bucket, zip_filename)


    presigned_url = s3.generate_presigned_url(
        "get_object",
        Params={"Bucket": target_bucket, "Key": zip_filename},
        ExpiresIn=604800,  # 7 วัน
    )





    card = {
        "cards": [
            {
                "header": {
                    "title": f"Inventory List AWS ประจำวันที่ {today}",
                    "subtitle": "ดาวน์โหลดไฟล์ Inventory List",
                },
                "sections": [
                    {
                        "widgets": [
                            {
                                "buttons": [
                                    {
                                        "textButton": {
                                            "text": "คลิกที่นี่เพื่อดาวน์โหลด",
                                            "onClick": {
                                                "openLink": {
                                                    "url": presigned_url
                                                }
                                            }
                                        }
                                    }
                                ]
                            }
                        ]
                    }
                ]
            }
        ]
    }
    requests.post(google_chat_webhook, json=card)

    return {"statusCode": 200, "body": f"Zip created ({zip_filename}) and shared successfully."}

