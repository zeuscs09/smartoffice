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

