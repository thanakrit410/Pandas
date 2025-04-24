import boto3
import json
import os

# สร้าง ECS client
ecs_client = boto3.client('ecs', region_name='ap-southeast-1')

# ฟังก์ชันดึงข้อมูลรายละเอียดของ task
def get_task_details(task_arn):
    try:
        # เรียกใช้ API เพื่อดึงรายละเอียดของ task
        response = ecs_client.describe_tasks(
            cluster=task_arn.split('/')[1],  # Extract cluster name from ARN
            tasks=[task_arn]
        )
        task = response['tasks'][0]  # ข้อมูล task แรก
        # ดึงข้อมูลที่จำเป็น
        task_details = {
            'TaskARN': task_arn,  # เพิ่ม TaskARN
            'Cluster': task_arn.split('/')[1],
            'Service': task['group'],  # Group แสดงชื่อ Service
            'CPU': task['cpu'],
            'Memory': task['memory']
        }
        return task_details
    except Exception as e:
        print(f"Error fetching details for {task_arn}: {e}")
        return None

# โฟลเดอร์ที่เก็บไฟล์ input และ output
input_folder_path = '../Json-input'
output_folder_path = '../Json-output'

# ฟังก์ชันอ่านข้อมูลจากไฟล์ JSON
def read_json_file(file_path):
    try:
        with open(file_path, 'r') as file:
            return json.load(file)
    except Exception as e:
        print(f"Error reading file {file_path}: {e}")
        return None

# Loop ผ่านไฟล์ในโฟลเดอร์ input
for filename in os.listdir(input_folder_path):
    file_path = os.path.join(input_folder_path, filename)
    if filename.endswith('.json'):  # ตรวจสอบว่าเป็นไฟล์ JSON
        data = read_json_file(file_path)
        if data:
            tasks_details = []
            # ดึง ARN จากไฟล์ JSON และเรียกใช้ฟังก์ชัน get_task_details
            for task_arn in data.get("task_arns", []):  # คาดว่าในไฟล์มีคีย์ "task_arns"
                task_details = get_task_details(task_arn)
                if task_details:
                    tasks_details.append(task_details)

            # กำหนดชื่อไฟล์ output ตามชื่อไฟล์ input และบันทึกลงในโฟลเดอร์ output
            output_filename = f"{os.path.splitext(filename)[0]}_tasks_details.json"
            output_file_path = os.path.join(output_folder_path, output_filename)

            # ตรวจสอบว่าโฟลเดอร์ output มีอยู่แล้วหรือไม่ ถ้ายังไม่มีให้สร้าง
            os.makedirs(output_folder_path, exist_ok=True)

            with open(output_file_path, 'w') as json_file:
                json.dump(tasks_details, json_file, indent=4)

            print(f"Data has been written to {output_file_path}")
