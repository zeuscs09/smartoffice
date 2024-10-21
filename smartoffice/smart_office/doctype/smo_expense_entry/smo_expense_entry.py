# Copyright (c) 2024, beansx and contributors
# For license information, please see license.txt

import frappe
from frappe.model.document import Document
from frappe import _


class SMOExpenseEntry(Document):

	def validate(self):
		
		total_cost = 0
		seen_expense = set()
		for item in self.expense_item:
			# ตรวจสอบรายการซ้ำเฉพาะ expense_type EXP001, EXP002
			if item.expense_type in ["EP001", "EP002"]:
				item_key = (item.expense_type)  # ปรับตามโครงสร้างข้อมูลจริงของคุณ
				if item_key in seen_expense:
					doc_expense_type=frappe.get_doc("SMO Expense Type", item.expense_type)
					frappe.throw(f"Duplicate expense found: {doc_expense_type.description} ")
				seen_expense.add(item_key)
			
			total_cost += item.total_cost
		
		if total_cost != self.total_amount:
			frappe.throw("Total cost is not equal to total amount")
		if self.workflow_state == "Draft":
			self.set_approvers()
	def before_save(self):
		if self.workflow_state != "Draft":
			for item in self.expense_item:
				result = frappe.db.sql("""
					SELECT SUM(1) AS total_count, 
						GROUP_CONCAT(DISTINCT ee.owner SEPARATOR ', ') AS requested_by
					FROM `tabSMO Expense Item` ei
					INNER JOIN `tabSMO Expense Entry` ee 
						ON ei.parent = ee.name
					WHERE ee.docstatus IN (0, 1)
						AND ee.workflow_state NOT IN ('Draft')
						AND ee.service_report = %s
						AND ei.expense_type = %s
						and ee.name !=%s
					GROUP BY ei.expense_type
				""", (self.service_report, item.expense_type, self.name), as_dict=True)
				
				for row in result:
					total_count = row['total_count']  # จำนวนรวม
					requested_by = row['requested_by']  # ายชื่อผู้ขอ (concat แล้ว)
					if not item.system_reminder :
						item.system_reminder = f"This item been entered {int(total_count)} times by {requested_by}."
			
			
	def on_update(self):
		
		if self.workflow_state == "Approval Review":
			self.create_notification(self.approver)
		
	def set_approvers(self):
		# เคลียร์ข้อมูลผู้อนุมัติเดิม
		employee = frappe.db.get_value("Employee", {"user_id": frappe.session.user}, ["name", "grade", "reports_to"], as_dict=True)
		self.approvers = []
		self.max_level = 0
		self.next_action = ""
		self.workflow_description = ""

		approvers = []
		current_employee = employee
		approver_level = 1

		# ตรวจสอบว่า requester มี grade มากกว่าหรือเท่ากับ 600 หรือไม่
		if int(current_employee.grade[:3]) >= 600:
			# หาผู้อนุมัติที่เป็นหัวหน้าของ requester
			if current_employee.reports_to:
					approver = frappe.db.get_value("Employee", current_employee.reports_to, ["name", "user_id", "designation"], as_dict=True)
					approvers.append({
						"approver": approver.name,
						"user_id": approver.user_id,
						"approver_level": approver_level,
						"approver_role": approver.designation,
						"status": "Pending"
					})
			else:
				frappe.throw("ไม่พบผู้อนุมัติสำหรับพนักงานระดับสูง")
		else:
			# หาผู้อนุมัติที่มี grade เท่ากับ 600 โดยใช้ reports_to
			while current_employee and int(current_employee.grade[:3]) < 600:
				if current_employee.reports_to:
					current_employee = frappe.db.get_value("Employee", current_employee.reports_to, ["name", "user_id", "grade", "designation", "reports_to"], as_dict=True)
				else:
					break

			if current_employee and int(current_employee.grade[:3]) >= 600:
				approvers.append({
					"approver": current_employee.name,
					"user_id": current_employee.user_id,
					"approver_level": approver_level,
					"approver_role": current_employee.designation,
					"status": "Pending"
				})
			else:
				frappe.throw("ไม่พบผู้อนุมัติที่มี grade เท่ากับหรือมากกว่า 600 ในสายบังคับบัญชา")


		# กำหนด next_action เป็น user_id ของ approver คนแรก
		self.approver = approvers[0]["user_id"] if approvers else ""
		if not self.approver:
			frappe.throw("Not found approver")

	def create_notification(self, user_id):
		
		notification = frappe.get_doc({
			"doctype": "Notification Log",
			"subject": f"มีคำขอเบิกค่าใช้จ่ายใหม่รอการอนุมัติ: {self.name}",
			"for_user": user_id,
			"type": "Alert",
			"document_type": self.doctype,
			"document_name": self.name,
			"read": 0,
		})
		notification.insert(ignore_permissions=True)

		# ส่งการแจ้งเตือนแบบ realtime
		frappe.publish_realtime(
			event='notification',
			message={
				'type': 'Alert',
				'message': f"มีคำขอเบิกค่าใช้จ่ายใหม่รอการอนุมัติ: {self.name}"
			},
			user=user_id
		)
