import frappe
from frappe import _
from frappe.utils.backups import backup

@frappe.whitelist()
def get_avartar(name):
    user_info = frappe.get_value("User", name, "user_image",as_dict=True)    
    return user_info

@frappe.whitelist()
def backup_site():
    backup(with_files=True)

@frappe.whitelist()
def get_comments(name,comment_type,reference_doctype):
    comments = frappe.db.sql("""
        SELECT comment_email action_by,content,creation  FROM `tabComment` 
        WHERE `reference_doctype` = %s 
        AND `reference_name` = %s 
        AND `comment_type` = %s
        ORDER BY creation asc
    """, (reference_doctype, name, comment_type) ,as_dict=True)
    return comments
