import frappe

def get_approval_chain(total_amount: float, request_by: str, flow_type: str = "Expense Request"):
    """
    สร้าง approval chain ตาม flow type และจำนวนเงิน
    
    Args:
        total_amount: จำนวนเงินรวมที่ต้องการอนุมัติ
        request_by: user id ของผู้ขออนุมัติ
        flow_type: ประเภทของ flow (default: "Expense Request")
        
    Returns:
        tuple: (approvers_list, max_level, next_user)
    """
    employee = frappe.db.get_value("Employee", {"user_id": request_by}, 
                                 ["name", "reports_to", "grade"], as_dict=True)

    # ดึงค่า Approval Limit
    approval_limit = frappe.get_all(
        "Approval Limit",
        filters={
            "approval_limit": (">", total_amount),
            "flow_type": flow_type
        },
        fields=["employee_grade", "approval_limit"],
        order_by="approval_limit asc",
        limit=1
    )

    approvers_data = []
    if approval_limit:
        required_grade = approval_limit[0].employee_grade
        approvers_data = _build_approval_chain_by_grade(employee, required_grade)
    else:
        approvers_data = _build_default_approval_chain(employee)

    # สร้าง Workflow Approver objects
    approvers = []
    for data in approvers_data:
        workflow_approver = frappe.new_doc("Workflow Approver")
        workflow_approver.approver = data["approver"]
        workflow_approver.user_id = data["user_id"]
        workflow_approver.status = data["status"]
        workflow_approver.approver_level = data["approver_level"]
        workflow_approver.approver_role = data["approver_role"]
        approvers.append(workflow_approver)

    max_level = len(approvers)
    next_user, next_level, is_last = get_next_action(approvers)

    return approvers, max_level, next_user

def _build_approval_chain_by_grade(employee, required_grade):
    """สร้าง approval chain ตาม grade ที่กำหนด"""
    approvers = []
    current_employee = employee
    approver_level = 1
    found_required_grade = False

    while current_employee.get("reports_to") and not found_required_grade:
        current_employee = frappe.db.get_value("Employee", current_employee.reports_to, 
            ["name", "user_id", "designation", "grade", "reports_to"], as_dict=True)
        
        if not any(approver["approver"] == current_employee.name for approver in approvers):
            approvers.append({
                "approver": current_employee.name,
                "user_id": current_employee.user_id,
                "status": "",
                "approver_level": approver_level,
                "approver_role": current_employee.designation
            })
            approver_level += 1
            
            # เปรียบเทียบเฉพาะ 3 หลักแรกของ grade
            current_grade = str(current_employee.grade)[:3]
            required_grade_3_digit = str(required_grade)[:3]
            
            if current_grade >= required_grade_3_digit:
                found_required_grade = True
                break

    if not found_required_grade:
        approver = _get_approver_by_grade(required_grade)
        if approver and not any(a["approver"] == approver.name for a in approvers):
            approvers.append({
                "approver": approver.name,
                "user_id": approver.user_id,
                "status": "",
                "approver_level": approver_level,
                "approver_role": approver.designation
            })

    return approvers

def _build_default_approval_chain(employee):
    """สร้าง approval chain แบบ default (ตามบังคับบัญชา)"""
    approvers = []
    current_employee = employee
    approver_level = 1

    while current_employee.get("reports_to"):
        approver = frappe.db.get_value("Employee", current_employee.reports_to, 
            ["name", "user_id", "designation", "reports_to"], as_dict=True)
        if not any(a["approver"] == approver.name for a in approvers):
            approvers.append({
                "approver": approver.name,
                "user_id": approver.user_id,
                "status": "Pending",
                "approver_level": approver_level,
                "approver_role": approver.designation
            })
            approver_level += 1
        current_employee = approver

    return approvers

def _get_approver_by_grade(grade):
    """ดึงข้อมูลผู้อนุมัติตาม grade"""
    return frappe.db.get_value(
        "Employee",
        {"grade": grade},
        ["name", "user_id", "designation"],
        as_dict=True,
        order_by="grade asc"
    )

def _create_approver_dict(employee, level):
    """สร้าง dictionary สำหรับข้อมูลผู้อนุมัติ"""
    return {
        "approver": employee.name,
        "user_id": employee.user_id,
        "approver_level": level,
        "approver_role": employee.designation,
        "comment": "",
        "status": "Pending"
    }

def _create_workflow_description(approvers):
    """สร้างคอธิบาย workflow"""
    workflow_steps = [
        f"{idx}. {approver['approver_role']} ({approver['user_id']})"
        for idx, approver in enumerate(approvers, start=1)
    ]
    return "ขั้นตอนการอนุมัติ:\n" + "\n".join(workflow_steps)

def get_next_action(approvers: list) -> tuple:
    """
    หา next action จาก approvers list
    
    Args:
        approvers: list ของ Workflow Approver objects
        
    Returns:
        tuple: (next_user_id, next_level, is_last)
    """
    if not approvers:
        return None, None, False
        
    pending_approvers = [
        a for a in approvers 
        if  not a.receive_date
    ]
    
    if not pending_approvers:
        return None, None, False
        
    next_approver = pending_approvers[0]
    is_last = len(pending_approvers) == 1
    
    next_approver.receive_date = frappe.utils.now_datetime()
    
    return next_approver.user_id, next_approver.approver_level, is_last