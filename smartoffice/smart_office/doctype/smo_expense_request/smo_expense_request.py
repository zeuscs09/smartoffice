# Copyright (c) 2024, beansx and contributors
# For license information, please see license.txt

import frappe
from frappe.model.document import Document
from frappe.utils import now_datetime, time_diff_in_seconds, format_duration as frappe_format_duration
from datetime import datetime
import calendar


class SMOExpenseRequest(Document):
    def validate(self):
        self.set_period_display()
        if self.total <= 0:
            frappe.throw("No expense amount")
    # Lifecycle Methods
    def before_save(self):
        if self.workflow_state == "Draft":
            self.set_approvers()
            self.reject_reason = None
            self.approve_amount=self.total
           
    def on_submit(self):
        """ไม่ได้ใช้เพราะใช้ Workflow"""
        frappe.errprint("=== on_submit triggered ===")
        for item in self.expense_request_item:
            frappe.db.set_value("SMO Expense Entry", item.expense, "is_request", 1)
        self.update_approver_status()
        
       

    def on_update(self):
        """สำหรับ Draft state"""
        frappe.errprint("=== on_update triggered ===")
        # ไม่ต้องทำอะไรใน Draft
        
        
    
    def on_update_after_submit(self):
        """จัดการทุก state changes จาก Workflow"""
        frappe.errprint("=== on_update_after_submit triggered ===")
        frappe.errprint(f"Current workflow state: {self.workflow_state}")
        self.update_approver_status()
       
        if self.workflow_state == "Rejected":
            self.create_notification(self.owner, f"คำขอเบิกค่าใช้จ่ายของคุณถูกปฏิเสธ: {self.name}")
        elif self.workflow_state == "Approved":
            self.create_notification(self.owner, f"คำขอเบิกค่าใช้จ่ายของคุณได้รับการอนุมัติแล้ว: {self.name}")

    def on_cancel(self):
        if self.workflow_state != "Rejected":
            frappe.throw("สามารถยกเลิกเอกสารได้เฉพาะกรณีที่ถูกปฏิเสธ (Rejected) เท่านั้น")
        for item in self.expense_request_item:
            frappe.db.set_value("SMO Expense Entry", item.expense, "is_request", 0)

    def after_delete(self):
        for item in self.expense_request_item:
            frappe.db.set_value("SMO Expense Entry", item.expense, "is_request", 0)

    # Core Functionality
    def set_approvers(self):
        # เคลียร์ข้อมูลผู้อนุมัติเดิม
        self.approvers = []
        self.max_level = 0
        self.next_action = ""
        self.workflow_description = ""
        finance_user = frappe.get_doc("Smart Office Setting").finance_user
        if not finance_user:
            frappe.throw("Not found finance user")
            
        employee = frappe.db.get_value("Employee", {"user_id": self.request_by}, ["name", "reports_to", "grade"], as_dict=True)
        total_amount = self.total
        approvers = []

        # ดึงค่า Approval Limit ทั้งหมดที่มากกว่าหรือเท่ากับยอดรวม
        approval_limit = frappe.get_all(
            "Approval Limit",
            filters={
                "approval_limit": (">=", total_amount),
                "flow_type": "Expense Request"
            },
            fields=["employee_grade", "approval_limit"],
            order_by="approval_limit asc",
            limit=1
        )
        
        if approval_limit:
            required_grade = approval_limit[0].employee_grade
            current_employee = employee
            approver_level = 1
            found_required_grade = False

            while current_employee.get("reports_to") and not found_required_grade:
                current_employee = frappe.db.get_value("Employee", current_employee.reports_to, 
                    ["name", "user_id", "designation", "grade", "reports_to"], as_dict=True)
                
                # ตรวจสอบว่าผู้อนุมัตินี้ยังไม่ได้ถูกเพิ่มไปแล้ว
                if not any(approver['approver'] == current_employee.name for approver in approvers):
                    approvers.append({
                        "approver": current_employee.name,
                        "user_id": current_employee.user_id,
                        "approver_level": approver_level,
                        "approver_role": current_employee.designation,
                        "comment": "",
                        "status": "Pending"
                    })
                    
                    approver_level += 1
                    
                    # ถ้าเจอ grade ที่ต้องการ ให้หยุดการวนลูป
                    if current_employee.grade == required_grade:
                        found_required_grade = True
                        break

            # ถ้าไม่พบผู้อนุมัติที่มี grade ตรงกันในสายบังคับบัญชา
            if not found_required_grade:
                approver = self.get_approver_by_grade(required_grade)
                if approver and not any(a['approver'] == approver.name for a in approvers):
                    approvers.append({
                        "approver": approver.name,
                        "user_id": approver.user_id,
                        "approver_level": approver_level,
                        "approver_role": approver.designation,
                            "status": "Pending"
                    })

        else:
            # ถ้าไม่มี Approval Limit ที่เหมาะสม ใช้วิธีการเดิม
            current_employee = employee
            approver_level = 1
            while current_employee.get("reports_to"):
                approver = frappe.db.get_value("Employee", current_employee.reports_to, 
                    ["name", "user_id", "designation", "reports_to"], as_dict=True)
                if not any(a['approver'] == approver.name for a in approvers):
                    approvers.append({
                        "approver": approver.name,
                        "user_id": approver.user_id,
                        "approver_level": approver_level,
                        "approver_role": approver.designation,
                        "status": "Pending"
                    })
                    approver_level += 1
                current_employee = approver

        # เพิ่มผู้อนุมัติใหม่
        for approver in approvers:
            self.append("approvers", approver)

        self.append("approvers", {
            "approver": finance_user,
            "user_id": finance_user,
            "approver_level": approver_level,
            "approver_role": "Finance",
            "status": "Pending"
        })

        self.max_level = len(approvers) + 1
        
        # กำหนด next_action เป็น user_id ของ approver คนแรก
        self.next_action = self.get_next_action()

        # สร้าง workflow_description
        workflow_steps = []
        for idx, approver in enumerate(approvers, start=1):
            step = f"{idx}. {approver['approver_role']} ({approver['user_id']})"
            workflow_steps.append(step)
        
        self.workflow_description = "ขั้นตอนการอนุมัติ:\n" + "\n".join(workflow_steps)

    def update_approver_status(self):
        frappe.errprint(f"=== Start update_approver_status ===")
        frappe.errprint(f"workflow_state: {self.workflow_state}")
        frappe.errprint(f"docname: {self.name}")
        
        current_user = frappe.session.user
        current_time = now_datetime()
        last_action_date = None
        current_approver = None
        next_approver = None

        frappe.errprint(f"Current user: {current_user}")
        
        for approver in self.approvers:
            if approver.user_id == current_user:
                frappe.errprint(f"Found current approver: {approver.user_id}")
                approver.action_date = current_time
                approver.status = "Rejected" if self.workflow_state == "Rejected" else "Approved"
                
                if approver.receive_date:
                    duration_seconds = time_diff_in_seconds(approver.action_date, approver.receive_date)
                    approver.duration = duration_seconds
                
                approver.db_update()
                last_action_date = current_time
                current_approver = approver
                
        if current_approver:
            next_approver = next((a for a in self.approvers if a.approver_level > current_approver.approver_level and a.status == "Pending"), None)
        
        if not next_approver:
            next_approver = next((a for a in self.approvers if a.status == "Pending" and a.approver_level == 1), None)
            
        if self.workflow_state != "Rejected":
            if next_approver:
                frappe.errprint(f"Found next approver: {next_approver.user_id}")
                next_approver.receive_date = current_time
                next_approver.db_update()
                self.create_notification(next_approver.user_id)
                self.next_action = next_approver.user_id
                self.db_update()
        
        frappe.errprint(f"=== End update_approver_status ===")

    def start_approval_process(self):
        if self.workflow_state == "Pending Approval" and self.approvers:
            self.approvers[0].receive_date = frappe.utils.now_datetime()
            self.save()

    # Helper Methods
    def get_approver_by_grade(self, grade):
        approver = frappe.db.get_value(
            "Employee",
            {"grade": grade},
            ["name", "user_id", "designation"],
            as_dict=True,
            order_by="grade asc"
        )
        return approver

    def get_next_action(self):
        pending_approver = next((approver for approver in self.approvers if approver.status == "Pending"), None)
        return pending_approver.user_id if pending_approver else ""

    def create_notification(self, user_id, message=None):
        frappe.errprint(f"=== Start create_notification ===")
        frappe.errprint(f"Creating notification for user: {user_id}")
        frappe.errprint(f"Document name: {self.name}")
        frappe.errprint(f"Workflow state: {self.workflow_state}")
        
        notification = frappe.get_doc({
            "doctype": "Notification Log", 
            "subject": message or f"คำขอเบิกค่าใช้จ่ายใหม่รอการอนุมัติ: {self.name}",
            "for_user": user_id,
            "type": "Alert",
            "document_type": self.doctype,
            "document_name": self.name,
            "read": 0,
        })
        notification.insert(ignore_permissions=True)
        frappe.errprint(f"=== End create_notification ===")

    def set_period_display(self):
        # แปลงปีและเดือนเป็น datetime object
       
        date_str = f"{self.year}-{self.month}-01"
        date_obj = datetime.strptime(date_str, "%Y-%B-%d")
        
        # หาวันสุดท้ายของเดือน
        last_day = calendar.monthrange(date_obj.year, date_obj.month)[1]
        # กำหนดรูปแบบการแสดงผลตาม period
        if self.period == "Mid month":
            self.period_display = f"01/{date_obj.strftime('%m')}/{str(date_obj.year)[2:]}-15/{date_obj.strftime('%m')}/{str(date_obj.year)[2:]} รอบที่ 1"
        else:  # End of month
            self.period_display = f"01/{date_obj.strftime('%m')}/{str(date_obj.year)[2:]}-{last_day}/{date_obj.strftime('%m')}/{str(date_obj.year)[2:]} รอบที่ 2"
