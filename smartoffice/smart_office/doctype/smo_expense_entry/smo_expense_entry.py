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
				if item.cal_taxi_depart_distance != item.taxi_depart_distance:
					item.w_edit_depart = f"Edit Distance from {format(float(item.cal_taxi_depart_distance), '.2f')} to {format(float(item.taxi_depart_distance), '.2f')}"
				else:
					item.w_edit_depart = ""
     
				if item.cal_taxi_return_distance != item.taxi_return_distance:
					item.w_edit_return = f"Edit Distance from {format(float(item.cal_taxi_return_distance), '.2f')} to {format(float(item.taxi_return_distance), '.2f')}"
				else:
					item.w_edit_return = ""
     
				item_key = (item.expense_type)  # ปรับตามโครงสร้างข้อมูลจริงของคุณ
				if item_key in seen_expense:
						doc_expense_type=frappe.get_doc("SMO Expense Type", item.expense_type)
						frappe.throw(f"Duplicate expense found: {doc_expense_type.description} ")
				seen_expense.add(item_key)
			# สร้าง reminder string จากค่าที่มีอยู่เท่านั้น
			reminder_parts = []
			if item.system_reminder:
				reminder_parts.append(item.system_reminder)
			if item.w_edit_depart:
				reminder_parts.append(item.w_edit_depart)
			if item.w_edit_return:
				reminder_parts.append(item.w_edit_return)
			
			item.reminder = " ".join(reminder_parts)
			total_cost += item.total_cost
		
		if total_cost != self.total_amount:
			frappe.throw("Total cost is not equal to total amount")
		# frappe.throw(self.workflow_state)
		if self.workflow_state == "Draft":
			self.set_approvers()
			self.reject_reason = None
			# self.check_service_report_status()
		if self.workflow_state == "Approval Review":
			self.check_service_report_status()
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
						item.system_reminder = f"This expense item has already been recorded {int(total_count)} time(s) by {requested_by}"
			
			
	def on_update(self):
		"""สำหรับ Draft และ Approval Review"""
		if self.workflow_state == "Approval Review":
			self.create_notification(
				self.approver, 
				f"มีคำขอเบิกค่าใช้จ่ายใหม่รอการอนุมัติ: {self.name}"
			)

	def on_update_after_submit(self):
		"""สำหรับการเปลี่ยนแปลงหลัง submit"""
		if self.workflow_state == "Rejected":
			reject_message = f"คำขอเบิกค่าใช้จ่ายของคุณถูกปฏิเสธ: {self.name}"
			if self.reject_reason:
				reject_message += f"\nเหตุผล: {self.reject_reason}"
			self.create_notification(self.owner, reject_message)
		elif self.workflow_state == "Approved":
			self.create_notification(
				self.owner,
				f"คำขอเบิกค่าใช้จ่ายของคุณได้รับการอนุมัติแล้ว: {self.name}"
			)

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

	def create_notification(self, user_id, custom_message=None):
		message = custom_message or f"มีคำขอเบิกค่าใช้จ่ายใหม่รอการอนุมัติ: {self.name}"
		
		notification = frappe.get_doc({
			"doctype": "Notification Log",
			"subject": message,
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
				'message': message
			},
			user=user_id
		)

	def check_service_report_status(self):
		if self.service_report:
			service_report_status = frappe.db.get_value("SMO Service Report", self.service_report, "workflow_state")
			if service_report_status != "Customer Approve":
				frappe.throw(_("ไม่สามารถส่งรายการค่าใช้จ่ายได้ เนื่องจากลูกค้ายังไม่อนุมัติ Service Report"))

	def before_cancel(self):
		if self.workflow_state != "Rejected":
			frappe.throw("สามารถยกเลิกเอกสารได้เฉพาะกรณีที่ถูกปฏิเสธ (Rejected) เท่านั้น")
