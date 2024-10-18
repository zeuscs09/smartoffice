import frappe
from frappe import _

@frappe.whitelist()
def get_avartar(name):
    user_info = frappe.get_value("User", name, "user_image",as_dict=True)    
    return user_info