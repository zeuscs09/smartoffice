import frappe

@frappe.whitelist()
def get_user_permissions():
    user = frappe.session.user
    roles = frappe.get_roles(user)
    
    try:
        # ตรวจสอบสิทธิ์จาก DocType โดยใช้ frappe.db
        permissions = {
            # ตรวจสอบสิทธิ์ Service Report
            "serviceReport": bool(frappe.db.get_value(
                'DocPerm',
                {
                    'parent': 'SMO Service Report',
                    'role': ['in', roles],
                    'read': 1
                },
                'read'
            )),
            
            # ตรวจสอบสิทธิ์ Expense Entry
            "expenseEntry": bool(frappe.db.get_value(
                'DocPerm',
                {
                    'parent': 'SMO Expense Entry',
                    'role': ['in', roles],
                    'read': 1
                },
                'read'
            )),
            
            # ตรวจสอบสิทธิ์ Expense Request
            "expenseRequest": bool(frappe.db.get_value(
                'DocPerm',
                {
                    'parent': 'SMO Expense Request',
                    'role': ['in', roles],
                    'read': 1
                },
                'read'
            )),
            
            # ตรวจสอบสิทธิ์ Advance Entry
            "advanceRequest": bool(frappe.db.get_value(
                'DocPerm',
                {
                    'parent': 'SMO Advance Entry',
                    'role': ['in', roles],
                    'read': 1
                },
                'read'
            )),
            
            # ตรวจสอบสิทธิ์ Manhour Report (จาก SMO Task)
            "manhourReport": bool(frappe.db.get_value(
                'DocPerm',
                {
                    'parent': 'SMO Task',
                    'role': ['in', roles],
                    'report': 1
                },
                'report'
            )),
            
            # ตรวจสอบสิทธิ์ Expense Report (จาก SMO Expense Entry)
            "expenseReport": bool(frappe.db.get_value(
                'DocPerm',
                {
                    'parent': 'SMO Expense Entry',
                    'role': ['in', roles],
                    'report': 1
                },
                'report'
            ))
        }
        
    except Exception as e:
        frappe.log_error(f"Error checking permissions: {str(e)}")
        # กรณีเกิดข้อผิดพลาด ให้กำหนดทุกสิทธิ์เป็น False
        permissions = {
            "serviceReport": False,
            "expenseEntry": False,
            "expenseRequest": False,
            "advanceRequest": False,
            "manhourReport": False,
            "expenseReport": False
        }
    
    return permissions 