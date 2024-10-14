# Copyright (c) 2024, beansx and contributors
# For license information, please see license.txt

import frappe
from frappe.model.document import Document
from frappe.utils import now_datetime, time_diff_in_seconds, format_duration as frappe_format_duration


class SMOExpenseRequest(Document):
	def before_save(self):
		if self.workflow_state == "Draft":
			self.set_approvers()
	def on_cancel(self):
		for item in self.expense_request_item:
				frappe.db.set_value("SMO Expense Entry", item.expense, "is_request", 0)
	def after_delete(self):
		for item in self.expense_request_item:
				frappe.db.set_value("SMO Expense Entry", item.expense, "is_request", 0)

	def set_approvers(self):
		# เคลียร์ข้อมูลผู้อนุมัติเดิม
		self.approvers = []
		self.max_level = 0
		self.next_action = ""
		self.workflow_description = ""

		employee = frappe.get_doc("Employee", {"user_id": self.request_by})
		total_amount = self.total
		approvers = []

		# ดึงค่า Approval Limit ทั้งหมดที่มากกว่าหรือเท่ากับยอดรวม
		approval_limit = frappe.get_all(
			"Approval Limit",
			filters={
				"approval_limit": (">=", total_amount)
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

			while current_employee.reports_to and not found_required_grade:
				current_employee = frappe.get_doc("Employee", current_employee.reports_to)
				
				# ตรวจสอบว่าผู้อนุมัตินี้ยังไม่ได้ถูกเพิ่มไปแล้ว
				if not any(approver['approver'] == current_employee.name for approver in approvers):
					approvers.append({
						"approver": current_employee.name,
						"user_id": current_employee.user_id,
						"approver_level": approver_level,
						"approver_role": current_employee.designation,
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
			while current_employee.reports_to:
				approver = frappe.get_doc("Employee", current_employee.reports_to)
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

		self.max_level = len(approvers)
		
		# กำหนด next_action เป็น user_id ของ approver คนแรก
		self.next_action = self.get_next_action()

		# สร้าง workflow_description
		workflow_steps = []
		for idx, approver in enumerate(approvers, start=1):
			step = f"{idx}. {approver['approver_role']} ({approver['approver']})"
			workflow_steps.append(step)
		
		self.workflow_description = "ขั้นตอนการอนุมัติ:\n" + "\n".join(workflow_steps)

	def on_submit(self):
		self.update_approver_status()
		self.create_initial_notification()

	def on_update_after_submit(self):
		self.update_approver_status()

	def update_approver_status(self):
		current_user = frappe.session.user
		current_time = now_datetime()
		last_action_date = None
		current_approver = None
		next_approver = None
  
		for approver in self.approvers:
			if approver.user_id == current_user:
				approver.action_date = current_time
				approver.status = "Rejected" if self.workflow_state == "Rejected" else "Approved"
				
				# คำนวณ duration
				if approver.receive_date:
					duration_seconds = time_diff_in_seconds(approver.action_date, approver.receive_date)
					approver.duration = duration_seconds
				
				approver.db_update()
				last_action_date = current_time
				current_approver = approver
				# ดึง next_approver
				
			
		if current_approver:
			next_approver = next((a for a in self.approvers if a.approver_level > current_approver.approver_level and a.status == "Pending"), None)
		
		if not next_approver:
			next_approver = next((a for a in self.approvers if a.status == "Pending" and a.approver_level == 1), None)
   
		frappe.errprint(next_approver)
		if next_approver:
			next_approver.receive_date = current_time
			next_approver.db_update()
			self.create_notification(next_approver.user_id)
			self.next_action = next_approver.user_id
			self.db_update()

	def create_notification(self, user_id):
		notification = frappe.get_doc({
			"doctype": "Notification Log",
			"subject": f"คำขอเบิกค่าใช้จ่ายใหม่รอการอนุมัติ: {self.name}",
			"for_user": user_id,
			"type": "Alert",
			"document_type": self.doctype,
			"document_name": self.name,
			"read": 0,
		})
		notification.insert(ignore_permissions=True)

	def get_approver_by_grade(self, grade):
		approver = frappe.get_all(
				"Employee",
				filters={
					"grade": grade
					},
				fields=["name", "user_id", "designation"],
				order_by="grade asc",
				limit=1
			)
		return frappe.get_doc("Employee", approver[0].name) if approver else None

	# เพิ่มฟักชันใหม่สำหรับการเริ่มกระบวนการอนุมัติ
	def start_approval_process(self):
		if self.workflow_state == "Pending Approval" and self.approvers:
			self.approvers[0].receive_date = frappe.utils.now_datetime()
			self.save()

	def on_update(self):
		self.update_approver_status()

	def get_next_action(self):
		pending_approver = next((approver for approver in self.approvers if approver.status == "Pending"), None)
		return pending_approver.user_id if pending_approver else ""

	def create_initial_notification(self):
		first_approver = next((a for a in self.approvers if a.status == "Pending"), None)
		if first_approver:
			self.create_notification(first_approver.user_id)
