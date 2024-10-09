import frappe
from frappe import _
from frappe.utils import now_datetime, get_datetime
import hashlib

@frappe.whitelist(allow_guest=True)
def approve_service_report(name, customer_email, hash, timestamp):
    try:
        # ตรวจสอบความถูกต้องของข้อมูลที่ส่งมา
        if not validate_service_report_access(name, customer_email, hash, timestamp):
            frappe.throw(_("Invalid access attempt"))

        # ใช้ frappe.db.get_value แทน frappe.get_doc
        workflow_state = frappe.db.get_value("SMO Service Report", name, "workflow_state")
        
        # ตรวจสอบสถานะปัจจุบันของรายงาน
        if workflow_state != "Customer Review":
            return {
                "success": False,
                "message": _("This service report is not pending approval.")
            }

        # ดำเนินการอนุมัติ
        frappe.db.set_value("SMO Service Report", name, {
            "workflow_state": "Customer Approve",
           
        })
        frappe.db.commit()

        frappe.logger("servicereport").info(f"Service report {name} approved by {customer_email}")

        return {
            "success": True,
            "message": _("Service report approved successfully.")
        }

    except frappe.DoesNotExistError:
        return {
            "success": False,
            "message": _("Service report not found.")
        }
    except Exception as e:
        frappe.log_error(f"Error approving service report: {str(e)}")
        return {
            "success": False,
            "message": _("An error occurred while approving the service report. Please try again later.")
        }

@frappe.whitelist(allow_guest=True)
def reject_service_report(name, customer_email, hash, timestamp, reason=None):
    try:
        if not validate_service_report_access(name, customer_email, hash, timestamp):
            frappe.throw(_("Invalid access attempt"))

        # ใช้ frappe.db.get_value แทน frappe.get_doc
        workflow_state = frappe.db.get_value("SMO Service Report", name, "workflow_state")
        
        if workflow_state != "Customer Review":
            return {
                "success": False,
                "message": _("This service report is not in a state that can be rejected.")
            }

        # ดำเนินการปฏิเสธ
        frappe.db.set_value("SMO Service Report", name, {
            "workflow_state": "Customer Reject",
            "rejected_by": customer_email,
            "rejected_at": frappe.utils.now(),
            "rejection_reason": reason,
            "approval_hash": None,
            "approval_salt": None
        })
        frappe.db.commit()
        
        # ส่งการแจ้งเตือนการปฏิเสธ
        send_rejection_notification(name, reason)

        return {
            "success": True,
            "message": _("Service report rejected successfully.")
        }

    except frappe.DoesNotExistError:
        return {
            "success": False,
            "message": _("Service report not found.")
        }
    except Exception as e:
        frappe.log_error(f"Error rejecting service report: {str(e)}")
        return {
            "success": False,
            "message": _("An error occurred while rejecting the service report. Please try again later.")
        }

# แก้ไขฟังก์ชัน validate_service_report_access เพื่อใช้ frappe.db
def validate_service_report_access(name, customer_email, hash, timestamp):
    # ใช้ frappe.db.get_value แทน frappe.get_doc
    approval_salt, approval_hash, contact_email = frappe.db.get_value("SMO Service Report", name, 
        ["approval_salt", "approval_hash", "contact_email"])
    
    # ตรวจสอบ hash
    hash_string = f"{name}|{customer_email}|{timestamp}|{approval_salt}"
    hash_object = hashlib.sha256(hash_string.encode())
    calculated_hash = hash_object.hexdigest()
    
    if calculated_hash != hash or approval_hash != hash:
        return False
    
    # ตรวจสอบการหมดอายุของลิงก์
    link_timestamp = get_datetime(timestamp)
    if (now_datetime() - link_timestamp).total_seconds() > 86400:  # 24 ชั่วโมง
        return False
    
    # ตรวจสอบอีเมลของลูกค้า
    if contact_email != customer_email:
        return False
    
    return True

# แก้ไขฟังก์ชัน send_rejection_notification เพื่อใช้ frappe.db
def send_rejection_notification(name, reason):
    try:
        # ดึงข้อมูลที่จำเป็นจาก database
        doc = frappe.db.get_value("SMO Service Report", name, 
            ["name", "owner", "rejection_reason"], as_dict=True)
        
        # ดึงอีเมลของทีมงาน
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

# เพิ่มฟังก์ชันอื่นๆ ที่เกี่ยวข้องกับ API ของ Service Report ตามต้องการ