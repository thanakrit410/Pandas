import boto3

dynamodb = boto3.resource('dynamodb')
table = dynamodb.Table('InstanceScheduler-StateTable-GHV0HVFPBUOS')

def lambda_handler(event, context):
    response = table.scan()
    for item in response['Items']:
        print("Item before update:", item)  # พิมพ์ข้อมูลก่อนการอัปเดต
        if isinstance(item, dict) and 'service' in item:
            print("aom")
            if item['service'] == 'rds':
                for key, value in item.items():
                    print(f"Checking key: {key}, value: {value}")
                    if isinstance(value, str) and value == 'stopped':
                        print(f"Item {key} is stopped, updating to running...")
                        update_response = table.update_item(
                            Key={
                                'service': item['service'],  # คีย์หลัก
                                'account-region': item['account-region']  # คีย์ที่สอง (ถ้ามี)
                            },
                            UpdateExpression="SET #key = :val",  # ใช้ #key สำหรับการอัปเดต
                            ExpressionAttributeNames={
                                "#key": key  # ใช้ชื่อฟิลด์ที่ต้องการอัปเดต
                            },
                            ExpressionAttributeValues={
                                ":val": "running"  # ค่าใหม่ที่ต้องการอัปเดต
                            }
                        )
                        # print(f"Update response: {update_response}")

    return {"message": "Update completed for rds"}







