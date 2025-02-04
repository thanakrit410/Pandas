import boto3
import logging

rds_client = boto3.client("rds")
logger = logging.getLogger()
logger.setLevel(logging.INFO)

def lambda_handler(event, context):
    try:
        # ดึงข้อมูลของทุก DB instance โดยใช้ pagination
        paginator = rds_client.get_paginator('describe_db_instances')
        for page in paginator.paginate():
            for instance in page["DBInstances"]:
                db_instance_id = instance["DBInstanceIdentifier"]
                status = instance["DBInstanceStatus"]
                arn = instance["DBInstanceArn"]

                # พิมพ์ข้อมูลของ DB Instance
                print(f"DB Instance ID: {db_instance_id}")
                print(f"Status: {status}")
                print(f"ARN: {arn}")

                tags_response = rds_client.list_tags_for_resource(ResourceName=arn)
                tags = {tag["Key"]: tag["Value"] for tag in tags_response["TagList"]}

                # พิมพ์แท็กที่ได้
                print(f"Tags: {tags}")

                if tags.get("Schedule") == "stopped" and status == "available":
                    print(f"กำลังหยุด RDS Instance: {db_instance_id}")
                    rds_client.stop_db_instance(DBInstanceIdentifier=db_instance_id)

        return {"status": "completed"}

    except Exception as e:
        logger.error(f"เกิดข้อผิดพลาด: {str(e)}")
        return {"status": "failed", "error": str(e)}
