import json
import io
import urllib3
import pygal
from pygal.style import Style
import boto3
from datetime import datetime, timedelta

# ตั้งค่า
APPS_SCRIPT_URL = "https://script.google.com/macros/s/AKfycby_c5sb7WAxVXapLT_5PJUbKdlskjZr3kE_kcL1InWh8MnpbcTcHOu0oxxPJOMxfAhYRg/exec"
CHAT_WEBHOOK_URL = "https://chat.googleapis.com/v1/spaces/AAAAve9tFZo/messages?key=AIzaSyDdI0hCZtE6vySjMm-WEfRq3CPzqKqqsHI&token=uJWuHGU9TrXJFa8j0xGdSspl4av2wip_MA3nNK37J3g"
S3_BUCKET_NAME = "central-menetment-inventory-list-bucket"
S3_KEY = "alarm-summary-chart.svg"

http = urllib3.PoolManager()

def lambda_handler(event, context):
    # 1. ดึงข้อมูล summary จาก Apps Script
    response = http.request('GET', APPS_SCRIPT_URL)
    data = json.loads(response.data.decode('utf-8'))

    print(f"Data received from Apps Script: {json.dumps(data)}")  # Debug log

    # 2. สร้างกราฟ
    image_data = create_bar_chart(data)

    # 3. อัปโหลดไปยัง S3
    upload_to_s3(image_data)

    # 4. สร้าง presigned URL สำหรับดาวน์โหลด
    presigned_url = generate_presigned_url(S3_BUCKET_NAME, S3_KEY)

    # 5. ส่งไป Google Chat
    send_image_to_chat(presigned_url)

    return {"statusCode": 200, "body": json.dumps("Chart sent to Google Chat")}


def create_bar_chart(summary):
    labels = list(set(summary.get("alarmWithWarning", {}).keys()) | set(summary.get("alarmWithCritical", {}).keys()))
    labels.sort()
    labels.append("Summary")

    warning_counts = [summary.get("alarmWithWarning", {}).get(app, 0) for app in labels]
    critical_counts = [summary.get("alarmWithCritical", {}).get(app, 0) for app in labels]
    total_counts = [w + c for w, c in zip(warning_counts, critical_counts)]

    alarm_counts = [0] * len(labels)
    alarm_counts[-1] = summary.get("alarm", 0)

    custom_style = Style(
        background='transparent',
        plot_background='transparent',
        foreground='#000',
        foreground_strong='#000',
        foreground_subtle='#630',
        opacity='.6',
        opacity_hover='.9',
        transition='400ms ease-in',
        colors=('#90EE90', '#FFA500', '#FF0000', '#0000FF')
    )

    bar_chart = pygal.Bar(
        style=custom_style,
        show_legend=True,
        height=400,
        print_values=True,
        show_y_guides=True,
        show_x_guides=False,
        show_values=True,
        value_formatter=lambda x: '' if x == 0 else str(int(x))
    )

    bar_chart.title = 'Alarm Summary by App'
    bar_chart.x_labels = labels
    bar_chart.add('WARNING', warning_counts, show_values=True)
    bar_chart.add('CRITICAL', critical_counts, show_values=True)
    bar_chart.add('TOTAL', total_counts, show_values=True)
    bar_chart.add('ALARM COUNT', alarm_counts, show_values=True)

    buf = io.BytesIO()
    buf.write(bar_chart.render())
    buf.seek(0)
    return buf


def upload_to_s3(image_data):
    s3 = boto3.client('s3')
    s3.upload_fileobj(image_data, S3_BUCKET_NAME, S3_KEY, ExtraArgs={
        'ContentType': 'image/svg+xml',
    })


def generate_presigned_url(bucket_name, object_key, expiration=3600):
    s3 = boto3.client('s3')
    url = s3.generate_presigned_url(
        ClientMethod='get_object',
        Params={'Bucket': bucket_name, 'Key': object_key},
        ExpiresIn=expiration
    )
    return url


def send_image_to_chat(image_url):
    
    sheet_url = "https://docs.google.com/spreadsheets/d/1X24vrd4FNFOwlFLAoWsP8jlVd-uaRLfr_F6Jpd7XLiw/edit"  

    yesterday = datetime.now() - timedelta(days=1)
    formatted_date = yesterday.strftime("%d/%m/%Y")

    message = {
        "cards": [
            {
                "header": {"title": "📊 Alarm Summary by AWS-infrabot"},
                "sections": [
                    {
                        "widgets": [
                            {
                                "textParagraph": {
                                    "text": f"นำส่งรายงานสรุปยอดสถิติการ Alarm ของวันที่ {formatted_date}"
                                }
                            },
                            {
                                "buttons": [
                                    {
                                        "textButton": {
                                            "text": "Open Google Sheets",  
                                            "onClick": {
                                                "openLink": {
                                                    "url": sheet_url  
                                                }
                                            }
                                        }
                                    },
                                    {
                                        "textButton": {
                                            "text": "Open Chart",  
                                            "onClick": {
                                                "openLink": {
                                                    "url": image_url  
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

    
    http.request(
        'POST',
        CHAT_WEBHOOK_URL,
        body=json.dumps(message).encode('utf-8'),
        headers={'Content-Type': 'application/json'}
    )

