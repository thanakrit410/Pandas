import pandas as pd
import glob
import re  # ใช้สำหรับแก้ชื่อไฟล์

# 📌 หาไฟล์ Excel ทั้งหมดในโฟลเดอร์
file_paths = glob.glob("../AWS_Inventory/*.xlsx")

output_file = "AWS_Inventory_03042025.xlsx"

with pd.ExcelWriter(output_file, engine="openpyxl") as writer:
    for file in file_paths:
        # ✅ ดึงชื่อไฟล์ (เช่น "report.xlsx" -> "report")
        file_name = file.split("/")[-1].replace(".xlsx", "")  
        file_name = re.sub(r'[\\/*?[\]:]', '_', file_name)  # แทนที่อักขระต้องห้าม

        xls = pd.ExcelFile(file)

        for sheet_name in xls.sheet_names:
            # ✅ ตั้งชื่อ Sheet ใหม่ เช่น "report_Data1"
            safe_sheet_name = re.sub(r'[\\/*?[\]:]', '_', sheet_name)  
            new_sheet_name = f"{file_name}_{safe_sheet_name}"[:31]  # Excel จำกัด 31 ตัวอักษร
          
            df = pd.read_excel(xls, sheet_name=sheet_name)
            df.to_excel(writer, sheet_name=new_sheet_name, index=False)

print(f"✅ รวมไฟล์เสร็จ! ไฟล์ที่ได้: {output_file}")
