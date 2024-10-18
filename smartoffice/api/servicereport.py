import frappe
from frappe import _
from frappe.utils import now_datetime, get_datetime
import hashlib
from frappe.utils import cstr
from frappe import response

@frappe.whitelist(allow_guest=True)
def approve_service_report(name, customer_email, hash, timestamp):
    try:
        if not validate_service_report_access(name, customer_email, hash, timestamp):
            return {"success": False, "message": _("การเข้าถึงไม่ถูกต้อง")}

        workflow_state = frappe.db.get_value("SMO Service Report", name, "workflow_state")
        
        if workflow_state != "Customer Review":
            return {"success": False, "message": _("รายงานบริการนี้ไม่ได้อยู่ในสถานะรอการอนุมัติ")}

        # อัปเดตค่าโดยตรงในฐานข้อมูล
        frappe.db.set_value("SMO Service Report", name, {
            "workflow_state": "Customer Approve",
            "approval_hash": None,
            "approval_salt": None
        })

        # ดึงเอกสารและเรยกใช้ on_submit
        doc = frappe.get_doc("SMO Service Report", name)
        doc.flags.ignore_permissions = True
        doc.submit()

        frappe.db.commit()

        frappe.logger("servicereport").info(f"Service report {name} approved by {customer_email}")

        return {"success": True, "message": _("รายงานบริการได้รับการอนุมัติเรียบร้อยแล้ว")}

    except frappe.DoesNotExistError:
        return {"success": False, "message": _("ไม่พบรายงานบริการ")}
    except Exception as e:
        frappe.log_error(f"Error approving service report: {str(e)}")
        return {"success": False, "message": _("เกิดข้อผิดพลาดขณะอนุมัติรายงานบริการ โปรดลองอีกครั้งในภายหลัง")}

@frappe.whitelist(allow_guest=True)
def reject_service_report(name, customer_email, hash, timestamp, reason=None):
    try:
        if not validate_service_report_access(name, customer_email, hash, timestamp):
            return {"success": False, "message": _("การเข้าถึงไม่ถูกต้อง")}

        workflow_state = frappe.db.get_value("SMO Service Report", name, "workflow_state")
        
        if workflow_state != "Customer Review":
            return {"success": False, "message": _("รายงานบริการนี้ไม่ได้อยู่ในสถานะที่สามารถปฏิเสธได้")}

        frappe.db.set_value("SMO Service Report", name, {
            "workflow_state": "Customer Reject",
            
            "approval_hash": None,
            "approval_salt": None
        })
        frappe.db.commit()
        
        send_rejection_notification(name, reason)

        return {"success": True, "message": _("รายงานบริการถูกปฏิเสธเรียบร้อยแล้ว")}

    except frappe.DoesNotExistError:
        return {"success": False, "message": _("ไม่พบรายงานบริการ")}
    except Exception as e:
        frappe.log_error(f"Error rejecting service report: {str(e)}")
        return {"success": False, "message": _("เกิดข้อผิดพลาดขณะปฏิเสธรายงานบริการ โปรดลองอีกครั้งในภายหลัง")}

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


@frappe.whitelist()
def get_user_service_reports(page, page_size, search=None, status=None, start_date=None, end_date=None, sort_field=None, sort_order=None):
    user = frappe.session.user
    page = int(page)
    page_size = int(page_size)
    offset = (page - 1) * page_size
    
    conditions = ["wt.users LIKE %s"]
    values = [f"%{user}%"]
    
    if search:
        conditions.append("(sr.name LIKE %s OR sr.task_name LIKE %s OR sr.customer_name LIKE %s OR wt.users LIKE %s)")
        values.extend([f"%{search}%"] * 4)
    
    if status:
        conditions.append("sr.workflow_state = %s")
        values.append(status)
    
    if start_date:
        conditions.append("sr.job_start_on >= %s")
        values.append(start_date)
    
    if end_date:
        conditions.append("sr.job_start_on <= %s")
        values.append(end_date)
    
    where_clause = " AND ".join(conditions)
    
    sort_clause = f"ORDER BY sr.{sort_field} {sort_order}" if sort_field and sort_order else "ORDER BY sr.creation DESC"
    
    query = f"""
        SELECT 
            sr.name,
            sr.task,
            sr.workflow_state,
            sr.creation,
            sr.job_start_on ,
            sr.job_finish,
            sr.task_name, 
            sr.customer_name,
            sr.contact_email,
            sr.contact_name,
            COUNT(*) OVER () as ttl_records,
            sr.owner,
            wt.parent,
            wt.users as teams
        FROM `tabSMO Service Report` sr
        INNER JOIN (
            SELECT parent, GROUP_CONCAT(user SEPARATOR ', ') AS users
            FROM `tabSMO Working Team`
            GROUP BY parent
        ) wt ON sr.name = wt.parent
        WHERE {where_clause}
        {sort_clause}
        LIMIT %s OFFSET %s
    """
    
    values.extend([page_size, offset])
    
    service_reports = frappe.db.sql(query, tuple(values), as_dict=1)
    
    total_count = service_reports[0].ttl_records if service_reports else 0
    
    return {
        "data": [
            {k: v for k, v in report.items() if k != 'ttl_records'}
            for report in service_reports
        ],
        "total": total_count,
        "page": page,
        "page_size": page_size,
        "total_pages": -(-total_count // page_size)  # การหารปัดขึ้น
    }
