import frappe
from frappe import _
import jwt
from datetime import datetime

@frappe.whitelist(allow_guest=True)
def hello():
    return "Hello, World!"

@frappe.whitelist(allow_guest=True)
def check_auth_and_get_reports():
    try:
        # frappe.log_error(message="Starting check_auth_and_get_reports", title="Debug 1")  # Debug log 1
        
        # รรวจสอบว่ามี Authorization header หรือไม่
        if not frappe.request:
            # frappe.log_error(message="No request object", title="Debug 2")  # Debug log 2
            return {
                "status": "error",
                "message": "Invalid request",
                "is_authenticated": False
            }
            
        # frappe.log_error(message=f"Request headers: {frappe.request.headers}", title="Debug 3")  # Debug log 3
        
        auth_header = frappe.request.headers.get('x-authen-code')
        if not auth_header or auth_header == "":
            # frappe.log_error(message="Invalid auth header", title="Debug 4")  # Debug log 4
            return {
                "status": "error",
                "message": "Invalid Authorization header",
                "is_authenticated": False
            }
        
        # ตรวจสอบ token
        token = auth_header.replace('Bearer ', '')
        # frappe.log_error(message=f"Token: {token[:10]}...", title="Debug 5")  # Debug log 5
        
        email = verify_customer_token(token)
        if not email:
            # frappe.log_error(message="Token verification failed", title="Debug 6")  # Debug log 6
            return {
                "status": "error",
                "message": "Invalid or expired token",
                "is_authenticated": False
            }
            
        # frappe.log_error(message=f"Authenticated email: {email}", title="Debug 7")  # Debug log 7
        
        # ดึง service reports ที่ยังไม่ได้ approve
        reports = frappe.db.sql("""
            SELECT 
                name, 
                project_code, 
                project_name, 
                start_date_input, 
                duration, 
                owner, 
                creation, 
                modified
            FROM `tabSMO Service Report`
            WHERE 
                contact_email = %(email)s 
                AND workflow_state = 'Customer Review'
            ORDER BY creation DESC
        """, {"email": email}, as_dict=True)
        
        # แปลง datetime เป็น string และ duration เป็นชั่วโมง
        for report in reports:
            report.start_date_input = report.start_date_input.strftime("%Y-%m-%d") if report.start_date_input else None
            report.creation = report.creation.strftime("%Y-%m-%d %H:%M:%S")
            report.modified = report.modified.strftime("%Y-%m-%d %H:%M:%S")
            # แปลงวินาทีเป็นชั่วโมงและนาที
            if report.duration:
                total_minutes = report.duration / 60  # แปลงวินาทีเป็นนาที
                hours = int(total_minutes // 60)  # หาจำนวนชั่วโมงเต็ม
                minutes = int(total_minutes % 60)  # หานาทีที่เหลือ
                
                if minutes == 0:
                    report.duration = f"{hours} Hours"
                else:
                    report.duration = f"{hours} Hours {minutes} Minutes"
            else:
                report.duration = None
        
        return {
            "status": "success",
            "is_authenticated": True,
            "email": email,
            "data": reports
        }
        
    except Exception as e:
        frappe.log_error(message=f"Error in check_auth_and_get_reports: {str(e)}\n{frappe.get_traceback()}", title="Customer Portal Error")
        return {
            "status": "error",
            "message": str(e),
            "is_authenticated": False
        }

def verify_customer_token(token):
    try:
        # ใช้ SECRET_KEY เดียวกับที่ใช้สร้าง token
        #SECRET_KEY = frappe.get_doc("Smart Office Setting").get_password("jwt_secret_key")
        SECRET_KEY="tps_smartoffice"
        payload = jwt.decode(token, SECRET_KEY, algorithms=["HS256"])
        email = payload.get('email')
        exp = payload.get('exp')
        
        # เช็คว่า token หมดอายุหรือยัง
        if datetime.fromtimestamp(exp) < datetime.now():
            return None
            
        return email
    except:
        return None

@frappe.whitelist(allow_guest=True)
def approve_service_report(report_name):
    try:
        # Check token from header
        token = frappe.get_request_header('Authorization')
        if not token:
            return {
                "status": "error",
                "message": "Not authenticated"
            }
            
        # Verify token
        token = token.replace('Bearer ', '')
        email = verify_customer_token(token)
        if not email:
            return {
                "status": "error",
                "message": "Invalid or expired token"
            }

        # Check report status and contact email
        result = frappe.db.get_value("SMO Service Report", report_name, 
            ["workflow_state", "contact_email"], as_dict=1)
            
        if not result:
            return {
                "status": "error",
                "message": "Service report not found"
            }
            
        workflow_state = result.workflow_state
       
        if workflow_state != "Customer Review":
            return {
                "status": "error",
                "message": "This service report is not in review status"
            }

        # Update status using db.set_value
        frappe.db.set_value("SMO Service Report", report_name, "workflow_state", "Customer Approved")
        frappe.db.commit()

        return {
            "status": "success", 
            "message": "Service report approved successfully"
        }

    except Exception as e:
        frappe.log_error(frappe.get_traceback(), "Customer Portal - Approve Error")
        return {
            "status": "error",
            "message": str(e)
        }

@frappe.whitelist(allow_guest=True)
def reject_service_report(report_name, reason=None):
    try:
        # Check token from header
        token = frappe.get_request_header('Authorization')
        if not token:
            return {
                "status": "error",
                "message": "Not authenticated"
            }
            
        # Verify token
        token = token.replace('Bearer ', '')
        email = verify_customer_token(token)
        if not email:
            return {
                "status": "error",
                "message": "Invalid or expired token"
            }

        # Check report status
        workflow_state = frappe.db.get_value("SMO Service Report", report_name, "workflow_state")
        
        if workflow_state != "Customer Review":
            return {
                "status": "error",
                "message": "This service report cannot be rejected in its current status"
            }

        # Update status
        frappe.db.set_value("SMO Service Report", report_name, {
            "workflow_state": "Customer Reject",
            "reject_reason": reason
        })
        frappe.db.commit()

        # Send notification
        send_rejection_notification(report_name, reason)

        return {
            "status": "success",
            "message": "Service report rejected successfully"
        }

    except Exception as e:
        frappe.log_error(frappe.get_traceback(), "Customer Portal - Reject Error")
        return {
            "status": "error",
            "message": str(e)
        }

def send_rejection_notification(name, reason):
    try:
        doc = frappe.db.get_value("SMO Service Report", name, 
            ["name", "owner"], as_dict=True)
        
        team_emails = frappe.db.sql("""
            SELECT email FROM `tabSMO Service Report Team`
            WHERE parent = %s
        """, (name,), as_dict=True)
        
        recipients = [d.email for d in team_emails] + [doc.owner]
        frappe.sendmail(
            recipients=recipients,
            subject=f"Service Report {doc.name} Rejected",
            message=f"The service report {doc.name} has been rejected by the customer. Reason: {reason or 'No reason provided'}",
            reference_doctype="SMO Service Report",
            reference_name=doc.name
        )
    except Exception as e:
        frappe.log_error(f"Error sending rejection notification: {str(e)}")
