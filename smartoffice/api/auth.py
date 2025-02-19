import frappe

@frappe.whitelist()
def get_user_permissions():
    user = frappe.session.user
    roles = frappe.get_roles(user)
    
    try:
        def check_permission(doctype, perm_type='read'):
            # ตรวจสอบจาก Custom DocPerm ก่อน
            custom_permission = frappe.db.get_value(
                'Custom DocPerm',
                {
                    'parent': doctype,
                    'role': ['in', roles],
                    perm_type: 1
                },
                perm_type
            )
            
            if custom_permission:
                return True
                
            # ถ้าไม่พบใน Custom DocPerm ให้ตรวจสอบใน DocPerm
            standard_permission = frappe.db.get_value(
                'DocPerm',
                {
                    'parent': doctype,
                    'role': ['in', roles],
                    perm_type: 1
                },
                perm_type
            )
            
            return bool(standard_permission)

        # ตรวจสอบสิทธิ์จาก DocType
        permissions = {
            "serviceReport": check_permission('SMO Service Report', 'read'),
            "expenseEntry": check_permission('SMO Expense Entry', 'read'),
            "expenseRequest": check_permission('SMO Expense Request', 'read'),
            "advanceRequest": check_permission('SMO Advance Entry', 'read'),
            "manhourReport": check_permission('SMO Task', 'report'),
            "expenseReport": check_permission('SMO Expense Entry', 'report'),
            # เพิ่มสิทธิ์สำหรับ Employee
            "employeeList": check_permission('Employee', 'report'),
            "employeeDetail": check_permission('Employee', 'report')
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
            "expenseReport": False,
            # เพิ่มสิทธิ์สำหรับ Employee
            "employeeList": False,
            "employeeDetail": False
        }
    
    return permissions 