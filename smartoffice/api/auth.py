import frappe

@frappe.whitelist()
def get_user_permissions():
    user = frappe.session.user
    roles = frappe.get_roles(user)
    
    # ตรวจสอบสิทธิ์จากเมนูปกติ
    permissions = {
        "serviceReport": True,
        "expenseEntry": True,
        "expenseRequest": True,
        "advanceRequest": True,
    }
    
    # ตรวจสอบสิทธิ์จาก DocType
    try:
        # ตรวจสอบสิทธิ์ Manhour Report จาก SMO Task
        smo_task = frappe.get_doc("DocType", "SMO Task")
        permissions["manhourReport"] = smo_task.has_permission("report")
        
        # ตรวจสอบสิทธิ์ Expense Report จาก SMO Expense Entry
        smo_expense = frappe.get_doc("DocType", "SMO Expense Entry")
        permissions["expenseReport"] = smo_expense.has_permission("report")
    except frappe.DoesNotExistError:
        # ถ้าไม่พบ DocType ให้กำหนดเป็น False
        permissions["manhourReport"] = False
        permissions["expenseReport"] = False
    except Exception as e:
        frappe.log_error(f"Error checking report permissions: {str(e)}")
        permissions["manhourReport"] = False
        permissions["expenseReport"] = False
    
    return permissions 