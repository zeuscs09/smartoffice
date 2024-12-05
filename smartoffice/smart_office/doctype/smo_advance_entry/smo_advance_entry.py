# Copyright (c) 2024, beansx and contributors
# For license information, please see license.txt

import frappe
from frappe.model.document import Document


class SMOAdvanceEntry(Document):
	def validate(self):
		if self.workflow_state == "Rejected" and not self.reject_reason:
			frappe.throw(_("กรุณาระบุเหตุผลในการ Reject"))
		
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

		for item in self.expense_item:
			item.paid_by="เงินทดรอง"
			item.ref_code=self.reference_code_finance
		if self.workflow_state == "Draft":
			self.reject_reason = None

	def on_update(self):
		"""สำหรับ Draft และ Approval Review"""
		# frappe.logger().debug(f"on_update triggered: {self.workflow_state}")
		if self.workflow_state == "Approval Review":
			self.create_notification(
				self.approver, 
				f"มีคำขอเบิกเงินทดรองใหม่รอการอนุมัติ: {self.name}"
			)

	def on_update_after_submit(self):
		"""สำหรับการเปลี่ยนแปลงหลัง submit"""
		# frappe.logger().debug(f"on_update_after_submit triggered: {self.workflow_state}")
		if self.workflow_state == "Rejected":
			reject_message = f"คำขอเบิกเงินทดรองของคุณถูกปฏิเสธ: {self.name}"
			if self.reject_reason:
				reject_message += f"\nเหตุผล: {self.reject_reason}"
			self.create_notification(self.owner, reject_message)
		elif self.workflow_state == "Approved":
			self.create_notification(
				self.owner,
				f"คำขอเบิกเงินทดรองของคุณได้รับการอนุมัติแล้ว: {self.name}"
			)

	def on_submit(self):
		"""เมื่อ submit เอกสาร"""
		frappe.logger().debug(f"on_submit triggered: {self.workflow_state}")
		if self.workflow_state == "Approved":
			self.create_notification(
				self.owner,
				f"คำขอเบิกเงินทดรองของคุณได้รับการอนุมัติและบันทึกแล้ว: {self.name}"
			)

	def create_notification(self, user_id, message):
		"""Create notification log entry and send realtime notification"""
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

		# ส่ง realtime notification พร้อมระบุ user
		frappe.publish_realtime(
			event='notification',
			message={
				'type': 'Alert',
				'message': message,
				'user': user_id  # เพิ่ม user_id เข้าไปใน message
			},
			user=user_id  # ระบุ user ที่จะรับ notification
		)
		frappe.msgprint("Notification sent to user: " + user_id)