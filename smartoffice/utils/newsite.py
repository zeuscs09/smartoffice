import frappe
from frappe import _
import json
import os

def get_child_tables(doctype):
    """
    อ่าน child tables จาก schema ของ DocType
    """
    try:
        # หา path ของไฟล์ .json
        app_path = frappe.get_app_path('smartoffice')
        json_path = os.path.join(app_path, 'smart_office', 'doctype', 
                               doctype.lower().replace(' ', '_'), 
                               f"{doctype.lower().replace(' ', '_')}.json")
        
        # อ่านไฟล์ json
        with open(json_path, 'r') as f:
            schema = json.load(f)
            
        child_tables = []
        
        # ค้นหา fields ที่เป็น Table type
        for field in schema.get('fields', []):
            if field.get('fieldtype') == 'Table':
                child_tables.append(field.get('options'))
                
        return child_tables
    except Exception as e:
        print(f"Error reading schema for {doctype}: {str(e)}")
        return []

def truncate_all_transaction_tables():
    """
    ล้างข้อมูลในตาราง transaction และ child tables ทั้งหมด
    """
    # รายชื่อ parent tables (ไม่รวม Workflow Approver เพราะอาจเป็น child table)
    parent_tables = [
        "SMO Advance Entry",
        "SMO Expense Entry", 
        "SMO Expense Request",
        "SMO Service Report",
        "SMO Task",
        "SMO Working Team"
    ]
    
    try:
        # Disable foreign key checks ชั่วคราว
        frappe.db.sql("SET FOREIGN_KEY_CHECKS = 0")
        
        # เก็บ set ของ child tables ทั้งหมดเพื่อป้องกันการลบซ้ำ
        all_child_tables = set()
        tables_structure = {}
        
        # สร้าง dictionary เก็บ child tables ของแต่ละ parent
        for parent in parent_tables:
            child_tables = get_child_tables(parent)
            tables_structure[parent] = child_tables
            all_child_tables.update(child_tables)
            print(f"Found child tables for {parent}: {child_tables}")
        
        # Truncate child tables (ลบแต่ละ child table เพียงครั้งเดียว)
        for child_table in all_child_tables:
            try:
                frappe.db.sql(f"DELETE FROM `tab{child_table}`")
                frappe.db.commit()
                print(f"Cleared child table: {child_table}")
            except Exception as e:
                print(f"Error clearing {child_table}: {str(e)}")
                    
        # Truncate parent tables
        for parent_table in parent_tables:
            try:
                # ไม่ต้องใส่ tab เพราะ frappe.db.truncate จะเพิ่มให้อัตโนมัติ
                frappe.db.truncate(parent_table)
                frappe.db.commit()
                print(f"Truncated parent table: {parent_table}")
            except Exception as e:
                print(f"Error truncating {parent_table}: {str(e)}")
        
        # ล้าง notification logs ที่เกี่ยวข้อง
        frappe.db.sql("""
            DELETE FROM `tabNotification Log` 
            WHERE document_type IN (
                'SMO Advance Entry',
                'SMO Expense Entry',
                'SMO Expense Request',
                'SMO Service Report',
                'SMO Task'
            )
        """)
        frappe.db.commit()
        
        # Enable foreign key checks กลับ
        frappe.db.sql("SET FOREIGN_KEY_CHECKS = 1")
        
        return {
            "status": "success", 
            "message": _("ล้างข้อมูล Transaction และ Child Tables ทั้งหมดเรียบร้อยแล้ว")
        }
        
    except Exception as e:
        frappe.db.rollback()
        # Enable foreign key checks กลับในกรณีเกิด error
        frappe.db.sql("SET FOREIGN_KEY_CHECKS = 1")
        
        error_msg = f"Error truncating tables: {str(e)}"
        frappe.log_error(error_msg)
        return {
            "status": "error", 
            "message": _("เกิดข้อผิดพลาด: {0}").format(str(e))
        }

@frappe.whitelist()
def execute_truncate():
    """
    API endpoint สำหรับเรียกใช้ truncate tables
    เฉพาะ System Manager เท่านั้นที่สามารถเรียกใช้ได้
    """
    if not frappe.has_permission("System Manager"):
        frappe.throw(_("ไม่มีสิทธิ์ในการดำเนินการนี้"))
        
    result = truncate_all_transaction_tables()
    
    if result["status"] == "success":
        frappe.msgprint(result["message"])
    else:
        frappe.throw(result["message"])
