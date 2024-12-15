# Copyright (c) 2024, beansx and contributors
# For license information, please see license.txt

import frappe
from frappe.model.document import Document
from frappe import _
from smartoffice.utils.approval_utils import get_approval_chain, get_next_action


class SMOAdvanceEntry(Document):
	def validate(self):
		if self.workflow_state == "Draft":
			self.set_approvers()
			self.reject_reason = None
			
		if self.workflow_state == "Rejected" and not self.reject_reason:
			frappe.throw(_("กรุณาระบุเหตุผลในการ Reject"))
		
		total_cost = 0
		seen_expense = set()
		for item in self.expense_item:
			# ตรวจสอบรายการซ้ำเฉพาะ expense_type EXP001, EXP002
			if item.expense_type in ["EP001", "EP002"]:
				item_key = (item.expense_type)
				if item_key in seen_expense:
					doc_expense_type = frappe.get_doc("SMO Expense Type", item.expense_type)
					frappe.throw(f"Duplicate expense found: {doc_expense_type.description}")
				seen_expense.add(item_key)
			
			total_cost += item.total_cost
		
		if total_cost != self.total_amount:
			frappe.throw("Total cost is not equal to total amount")

		for item in self.expense_item:
			item.paid_by = "เงินทดรอง"
			item.ref_code = self.reference_code_finance

	def set_approvers(self):
		# เคลียร์ข้อมูลผู้อนุมัติเดิม
		self.approvers = []
		self.max_level = 0
		self.next_action = ""
		
		# ตั้งค่า admin user ก่อน
		finance_user = frappe.get_doc("Smart Office Setting").finance_user
		if not finance_user:
			frappe.throw("Not found finance user")

		# เรียกใช้ approval_utils เพื่อสร้าง approval chain
		approvers, max_level, next_user = get_approval_chain(
			total_amount=self.total_amount,
			request_by=frappe.session.user,
			flow_type="Advance Entry"
		)

		

		# ปรับ level ของ approvers ที่เหลือให้เริ่มจาก 2
		for approver_data in approvers:
			self.append("approvers", {
				"approver": approver_data.approver,
				"user_id": approver_data.user_id,
				"approver_level": approver_data.approver_level,
				"approver_role": approver_data.approver_role,
				"status": approver_data.status
			})
		# เพิ่ม Finance user เป็นคนสุดท้าย
		self.append("approvers", {
			"approver": finance_user,
			"user_id": finance_user,
			"approver_level": max_level + 1,
			"approver_role": "Finance",
			"status": ""
		})
		self.max_level = max_level + 1
	

	def on_submit(self):
		first_approver = next((a for a in self.approvers if a.approver_level == 1), None)
		if first_approver:
			first_approver.receive_date = frappe.utils.now()
			first_approver.status = "Pending"
			first_approver.db_update()
			self.next_action = first_approver.user_id
			self.db_update();
			self.create_notification(
				first_approver.user_id,
				f"มีคำขอเบิกเงินทดรองใหม่รอการตรวจสอบ: {self.name}"
			)

	def on_update_after_submit(self):
		self.set_approver_status()

	def set_approver_status(self):
		current_approver = next((a for a in self.approvers if a.user_id == frappe.session.user), None)
		
		if current_approver:
			if self.workflow_state in ["Pending Approval", "Approved", "Rejected"]:
				current_approver.action_date = frappe.utils.now()
				current_approver.status = "Rejected" if self.workflow_state == "Rejected" else "Approved"
				
				if current_approver.receive_date:
					duration = frappe.utils.time_diff_in_seconds(
						current_approver.action_date,
						current_approver.receive_date
					)
					current_approver.duration = duration
				
				if self.workflow_state == "Pending Approval":
					next_user, next_level, is_last = get_next_action(self.approvers)
				
					if next_user:
						next_approver = next((a for a in self.approvers if a.user_id == next_user), None)
						if next_approver:
							next_approver.receive_date = frappe.utils.now()
							next_approver.status = "Pending"
							next_approver.db_update()
							self.next_action = next_user
							self.create_notification(
								next_user,
								f"มีคำขอเบิกเงินทดรองรอการอนุมัติ: {self.name}"
							)
					elif is_last:
						self.next_action = ""
						self.create_notification(
							self.owner,
							f"คำขอเบิกเงินทดรองของคุณได้รับการอนุมัติแล้ว: {self.name}"
						)
				elif self.workflow_state == "Approved":
					self.next_action = ""
					self.create_notification(
						self.owner,
						f"คำขอเบิกเงินทดรองของคุณได้รับการอนุมัติแล้ว: {self.name}"
					)
				elif self.workflow_state == "Rejected":
					self.next_action = ""
					current_approver.comment = self.reject_reason
					reject_message = f"คำขอเบิกเงินทดรองของคุณถูกปฏิเสธ: {self.name}"
					if self.reject_reason:
						reject_message += f"\nเหตุผล: {self.reject_reason}"
					self.create_notification(self.owner, reject_message)
				
				current_approver.db_update()
				self.db_update()

	def on_update(self):
		"""สำหรับ Draft และ Approval Review"""
		# frappe.logger().debug(f"on_update triggered: {self.workflow_state}")
		if self.workflow_state == "Approval Review":
			self.create_notification(
				self.approver, 
				f"มีคำขอเบิกเงินทดรองใหม่รอการอนุมัติ: {self.name}"
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
		# frappe.msgprint("Notification sent to user: " + user_id)