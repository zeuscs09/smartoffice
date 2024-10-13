# Copyright (c) 2024, beansx and contributors
# For license information, please see license.txt

import frappe
from frappe.model.document import Document


class SMOExpenseRequest(Document):
	def before_save(self):
		if self.workflow_state != "Draft":
			self.set_approvers()
			self.update_workflow_state()
	def on_submit(self):
		self.create_todo_and_send_email()
	def on_cancel(self):
		self.update_expense_entries(is_request=0)
	def after_delete(self):
		self.update_expense_entries(is_request=0)
	def set_approvers(self):
		self.approvers = []
		amount = self.total_amount
		employee = frappe.get_value("Employee", {"user_id": self.request_by}, "name")
		if not employee:
			frappe.throw("ไม่พบข้อมูลพนักงานสำหรับผู้ใช้นี้")
		approvers = self.get_approvers(employee, amount)
		for level, approver in enumerate(approvers, start=1):
			self.append("approvers", {
					"approver": approver,
					"status": "Pending",
					"approver_level": level
				})
	def get_approvers(self, employee, amount):
		approvers = []
		current_employee = frappe.get_doc("Employee", employee)
		
		while current_employee.reports_to:
			approver = frappe.get_doc("Employee", current_employee.reports_to)
			approvers.append(approver.user_id)
			
			approval_limit = frappe.get_value("Approval Limit", 
											  {"employee_grade": approver.grade}, 
											  "approval_limit")
			
			if approval_limit and amount <= approval_limit:
				break
			
			current_employee = approver
		
		if not approvers or amount > approval_limit:
			ceo = frappe.get_all("Employee", filters=[["grade", "like", "999%"]], fields=["user_id"], limit=1)
			if ceo:
				approvers.append(ceo[0].user_id)
		
		return approvers
	def update_workflow_state(self):
		pending_approvers = [a.approver for a in self.approvers if a.status == "Pending"]
		if pending_approvers:
			self.workflow_state = "Pending Approval"
			self.workflow_description = f"รออนุมัติจาก {', '.join(pending_approvers)}"
		elif all(a.status == "Approved" for a in self.approvers):
			self.workflow_state = "Approved"
			self.workflow_description = "อนุมัติแล้ว"
		else:
			self.workflow_state = "Rejected"
			self.workflow_description = "ถูกปฏิเสธ"
	def create_todo_and_send_email(self):
		for approver in self.approvers:
			if approver.status == "Pending":
				self.create_todo(approver.approver)
				self.send_email_notification(approver.approver)
	def create_todo(self, approver):
		frappe.get_doc({
			"doctype": "ToDo",
			"allocated_to": approver,
			"assigned_by": self.request_by,
			"reference_type": self.doctype,
			"reference_name": self.name,
			"description": f"อนุมัติ {self.doctype} {self.name}",
			"status": "Open"
			}).insert(ignore_permissions=True)
	def send_email_notification(self, approver):
		subject = f"ขออนุมัติ {self.doctype} {self.name}"
		message = f"กรุณาอนุมัติ {self.doctype} {self.name}\n\nรายละเอียด: {self.description}\nจำนวนเงิน: {self.total_amount}"
		frappe.sendmail(
			recipients=[approver],
			subject=subject,
			message=message
			)
	def update_expense_entries(self, is_request):
		for item in self.expense_request_item:
			frappe.db.set_value("SMO Expense Entry", item.expense, "is_request", is_request)

	@frappe.whitelist()
	def approve_expense(self):
		if not frappe.has_permission("SMO Expense Request", "write"):
			frappe.throw("คุณไม่มีสิทธิ์อนุมัติเอกสารนี้")

		if self.workflow_state not in ["Pending Approval"]:
			frappe.throw("เอกสารนี้ไม่อยู่ในสถานะที่สามารถอนุมัติได้")

		current_user = frappe.session.user
		approver_found = False

		try:
			for approver in self.approvers:
				if approver.approver == current_user and approver.status == "Pending":
					approver.status = "Approved"
					frappe.db.set_value("Workflow Approver", approver.name, "status", "Approved")
					approver_found = True
					break
			
			if not approver_found:
				frappe.throw("คุณไม่ใช่ผู้อนุมัติที่กำลังรอการอนุมัติสำหรับเอกสารนี้")
			
			self.update_workflow_state()
			
			if self.workflow_state == "Pending Approval":
				self.create_todo_and_send_email()
			
			self.add_comment("Workflow", f"อนุมัติโดย {frappe.session.user}")
			self.save(ignore_permissions=True)
			return self.workflow_state
		except Exception as e:
			frappe.log_error(f"เกิดข้อผิดพลาดในการอนุมัติ: {str(e)}")
			frappe.throw("เกิดข้อผิดพลาดในการอนุมัติ กรุณาลองใหม่อีกครั้ง")

@frappe.whitelist()
def approve_expense(doc_name):
	doc = frappe.get_doc("SMO Expense Request", doc_name)
	return doc.approve_expense()
