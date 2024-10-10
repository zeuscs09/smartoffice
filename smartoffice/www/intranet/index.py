import frappe

def get_context(context):
    context.logo_url =' get_app_logo()'
    # เพิ่มข้อมูลอื่นๆ ที่ต้องการส่งไปยัง template ที่นี่

def get_app_logo():
    # ดึง app_logo จาก Navbar Settings
    navbar_settings = frappe.get_single("Navbar Settings")
    if navbar_settings.app_logo:
        return navbar_settings.app_logo
    return None
