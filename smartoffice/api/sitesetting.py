import frappe

@frappe.whitelist(allow_guest=True)
def get_site_info():
    # ใช้ frappe.db.get_single_value แทน frappe.get_single
    app_logo = frappe.db.get_single_value("Navbar Settings", "app_logo")
    favicon = frappe.db.get_single_value("Website Settings", "favicon")
    app_name = frappe.db.get_single_value("Website Settings", "app_name")
    
    return {
        "logo": app_logo,
        "favicon": favicon,
        "title": app_name
    }
