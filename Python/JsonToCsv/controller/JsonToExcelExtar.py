import json
import os
from openpyxl import Workbook
from openpyxl.styles import Border, Side

# กำหนดพาธของโฟลเดอร์ที่เก็บไฟล์ JSON และโฟลเดอร์สำหรับเก็บไฟล์ Excel
json_folder_path = "../data"  # ปรับพาธที่เก็บไฟล์ JSON
excel_output_folder = "../csv"  # ปรับพาธที่เก็บไฟล์ Excel

# สร้างโฟลเดอร์สำหรับเก็บไฟล์ Excel ถ้าไม่มี
os.makedirs(excel_output_folder, exist_ok=True)

# กำหนดการจัดกรอบ (เส้นขอบ) สำหรับแต่ละเซลล์
border = Border(
    left=Side(border_style="thin"),
    right=Side(border_style="thin"),
    top=Side(border_style="thin"),
    bottom=Side(border_style="thin")
)

# วนลูปในไฟล์ทั้งหมดในโฟลเดอร์ JSON
for filename in os.listdir(json_folder_path):
    # ตรวจสอบว่าไฟล์เป็นไฟล์ JSON
    if filename.endswith(".json"):
        file_path = os.path.join(json_folder_path, filename)

        # อ่านข้อมูลจากไฟล์ JSON
        with open(file_path, "r") as json_file:
            data = json.load(json_file)

            # สร้างไฟล์ Excel
            wb = Workbook()
            ws = wb.active
            ws.title = "Resources and Tags"

            # เขียนหัวข้อในแถวแรก
            ws.append(["Service", "ResourceARN", "Tags"])

            # เตรียมข้อมูลที่จะเก็บในตาราง
            all_rows = []
            for resource in data.get("ResourceTagMappingList", []):
                resource_arn = resource["ResourceARN"]
                
                # แยก Service จาก ARN
                service_name = resource_arn.split(":")[2]  # ตำแหน่งที่ 2 คือชื่อของ Service (เช่น s3, ec2)
                
                tags = resource.get("Tags", [])
                
                # รวบรวมแท็กทั้งหมด
                if tags:
                    tag_str = ", ".join([f"{tag['Key']}: {tag['Value']}" for tag in tags])
                else:
                    tag_str = "No Tag"
                
                # เก็บข้อมูลในแถว
                all_rows.append([service_name, resource_arn, tag_str])

            # เขียนข้อมูลลงในแถว
            for row in all_rows:
                ws.append(row)

            # ใส่กรอบให้กับแต่ละเซลล์
            for row in ws.iter_rows(min_row=2, max_row=len(all_rows) + 1, min_col=1, max_col=3):
                for cell in row:
                    cell.border = border

            # สร้างชื่อไฟล์ Excel ตามชื่อไฟล์ JSON
            excel_filename = f"{os.path.splitext(filename)[0]}.xlsx"
            excel_file_path = os.path.join(excel_output_folder, excel_filename)

            # บันทึกไฟล์ Excel
            wb.save(excel_file_path)

            print(f"Data from {filename} has been written to {excel_filename}")

