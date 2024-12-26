import frappe
from frappe import _
import random
import string
from frappe.utils import now_datetime, add_to_date, get_datetime
import jwt
import json
import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from frappe.core.doctype.user.user import generate_keys  # เพิ่ม import ที่ด้านบน
from datetime import datetime, timedelta


def create_jwt_token(user, api_key, api_secret):
    SECRET_KEY = "your-secret-key"  # ควรย้ายไปเก็บใน configuration
    
    # สร้าง payload จากข้อมูล api key/secret
    payload = {
        'user': user.name,
        'api_key': api_key,
        'api_secret': api_secret,
        'exp': datetime.utcnow() + timedelta(days=1),
        'iat': datetime.utcnow()
    }
    
    # สร้าง JWT token
    token = jwt.encode(payload, SECRET_KEY, algorithm='HS256')
    return token

@frappe.whitelist()
def login(username, password):
    try:
        original_user = frappe.session.user
        
        if "System Manager" in frappe.get_roles(original_user):
            auth = frappe.auth.LoginManager()
            auth.authenticate(username, password)
            
            frappe.set_user(original_user)
            generate_keys(username)
            
            user = frappe.get_doc("User", username)
            api_key = user.api_key
            api_secret = user.get_password('api_secret')
            
            # สร้าง JWT token จากข้อมูล api key/secret
            jwt_token = create_jwt_token(user, api_key, api_secret)
            
            return {
                "message": "Login successful",
                "status": "success",
                "token": jwt_token,
                "token_type": "Bearer"
            }
        else:
            return {
                "message": f"Original user '{original_user}' does not have System Manager role",
                "status": "error"
            }
                
    except Exception as e:
        return {
            "message": str(e),
            "status": "error"
        }

@frappe.whitelist(allow_guest=True)
def request_customer_otp():
    try:
        # รับ email จาก frappe.call
        email = frappe.form_dict.get('email')
        
        # ถ้าไม่มี email จาก form_dict ลองเช็คจาก request.data (สำหรับ REST API)
        if not email and frappe.request.data:
            try:
                data = json.loads(frappe.request.data)
                email = data.get('email')
            except json.JSONDecodeError:
                pass
        
        if not email:
            frappe.throw(_("Email is required"))
            
        if not frappe.db.exists("SMO Service Report", {"contact_email": email}):
            frappe.throw(_("Email not found in our system"))
            
        # สร้าง OTP และ Reference Code
        otp = ''.join(random.choices(string.digits, k=6))
        reference_code = ''.join(random.choices(string.ascii_uppercase + string.digits, k=8))
        expiry = add_to_date(now_datetime(), minutes=10)
        
        # บันทึก OTP
        doc = frappe.get_doc({
            "doctype": "SMO Customer OTP",
            "email": email,
            "otp": otp,
            "reference_code": reference_code,
            "expiry": expiry,
            "is_used": 0
        })
        doc.insert(ignore_permissions=True)
        
        # ส่ง OTP และ Reference Code ทางอีเมล์
        send_otp_email(email, otp, reference_code)
        
        return {
            "message": "OTP sent successfully", 
            "status": "success",
            "reference_code": reference_code
        }
        
    except Exception as e:
        frappe.log_error(frappe.get_traceback(), "Customer OTP Request Error")
        return {"message": str(e), "status": "error"}

@frappe.whitelist(allow_guest=True)
def verify_customer_otp():
    try:
        # รับข้อมูลจาก frappe.call
        email = frappe.form_dict.get('email')
        otp = frappe.form_dict.get('otp')
        reference_code = frappe.form_dict.get('reference_code')
        
        # ถ้าไม่มีข้อมูลจาก form_dict ลองเช็คจาก request.data (สำหรับ REST API)
        if not (email and otp) and frappe.request.data:
            try:
                data = json.loads(frappe.request.data)
                email = data.get('email')
                otp = data.get('otp')
                reference_code = data.get('reference_code')
            except json.JSONDecodeError:
                pass
        
        if not email or not otp:
            frappe.throw(_("Email and OTP are required"))
            
        if not reference_code:
            # ถ้าไม่มี reference_code ให้หาจาก OTP ล่าสุดของ email นี้
            latest_otp = frappe.get_all(
                "SMO Customer OTP",
                filters={
                    "email": email,
                    "is_used": 0,
                    "expiry": [">", now_datetime()]
                },
                order_by="creation desc",
                limit=1
            )
            if latest_otp:
                otp_doc = frappe.get_doc("SMO Customer OTP", latest_otp[0].name)
                reference_code = otp_doc.reference_code
        
        # ตรวจสอบ OTP และ Reference Code
        valid_otp = frappe.get_all(
            "SMO Customer OTP",
            filters={
                "email": email,
                "otp": otp,
                "reference_code": reference_code,
                "expiry": [">", now_datetime()],
                "is_used": 0
            },
            limit=1
        )
        
        if not valid_otp:
            frappe.throw(_("Invalid or expired OTP"))
            
        # สร้าง token และอัพเดทสถานะ
        token = generate_customer_token(email)
        otp_doc = frappe.get_doc("SMO Customer OTP", valid_otp[0].name)
        otp_doc.is_used = 1
        otp_doc.save(ignore_permissions=True)
        
        return {
            "message": "OTP verified successfully",
            "status": "success",
            "token": token
        }
        
    except Exception as e:
        frappe.log_error(frappe.get_traceback(), "Customer OTP Verification Error")
        return {"message": str(e), "status": "error"}

def generate_customer_token(email):
    SECRET_KEY = frappe.get_doc("Smart Office Setting").get_password("jwt_secret_key")
    payload = {
        "email": email,
        "exp": add_to_date(now_datetime(), minutes=60 * 24)  # token หมดอายุใน 24 ชั่วโมง
    }
    return jwt.encode(payload, SECRET_KEY, algorithm="HS256")

def send_otp_email(email, otp, reference_code):
    try:
        template = frappe.db.get_single_value("Smart Office Setting", "customer_otp_template")
        if not template:
            frappe.throw(_("Email template not configured"))
            
        args = {
            "otp": otp,
            "email": email,
            "reference_code": reference_code
        }
        
        email_template = frappe.get_doc("Email Template", template)
        subject = frappe.render_template(email_template.subject, args)
        message = frappe.render_template(email_template.response, args)
        
        # ใช้ frappe.sendmail แทนการส่งผ่าน SMTP โดยตรง
        frappe.sendmail(
            recipients=[email],
            subject=subject,
            message=message,
            delayed=False  # ส่งทันทีไม่ต้องรอคิว
        )
            
    except Exception as e:
        frappe.log_error(frappe.get_traceback(), "OTP Email Sending Error")
        frappe.throw(_("Failed to send OTP email: {0}").format(str(e)))