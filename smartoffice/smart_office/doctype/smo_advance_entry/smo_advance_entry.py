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
		# ตึง designation จาก setting
		checking_role = frappe.get_doc("Smart Office Setting").accounting
		if not checking_role:
			frappe.throw(f"Not found {checking_role}")

		# เปลี่ยนจากการดึง employees ตาม designation เป็นการใช้ role 
		# ดึง users ที่มี role ที่กำหนด
		finance_users = frappe.get_all(
			"Has Role",
			filters={
				"role": checking_role,
				"parenttype": "User"
			},
			fields=["parent"]
		)

		if not finance_users:
			frappe.throw(f"No users found with role: {checking_role}")

		# กรองเฉพาะ active users
		active_finance_users = []
		for user in finance_users:
			user_status = frappe.db.get_value("User", user.parent, "enabled")
			if user_status:
				active_finance_users.append(user.parent)
		
		if not active_finance_users:
			frappe.throw(f"No active users found with role: {checking_role}")

		# เรียกใช้ approval_utils เพื่อสร้าง approval chain
		approvers, max_level, next_user = get_approval_chain(
			total_amount=self.total_amount,
			request_by=frappe.session.user,
			flow_type="Advance Entry"
		)

		
		finance_user_list = ", ".join(active_finance_users)
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
			"approver": finance_user_list,
			"user_id": finance_user_list,
			"approver_level": max_level + 1,
			"approver_role": checking_role,
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
		current_approver = next((a for a in self.approvers if frappe.session.user in a.user_id), None)
		
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
		# แยก user_id ที่คั่นด้วยเครื่องหมายจุลภาค
		user_list = [u.strip() for u in user_id.split(',') if u.strip()]
		
		for single_user in user_list:
			notification = frappe.get_doc({
				"doctype": "Notification Log",
				"subject": message,
				"for_user": single_user,
				"type": "Alert",
				"document_type": self.doctype,
				"document_name": self.name,
				"read": 0,
			})
			notification.insert(ignore_permissions=True)

			# ส่ง realtime notification สำหรับแต่ละ user
			frappe.publish_realtime(
				event='notification',
				message={
					'type': 'Alert',
					'message': message,
					'user': single_user
				},
				user=single_user
			)
			try:
				# ดึงข้อมูลอีเมลของผู้ใช้
				user_email = frappe.db.get_value("User", single_user, "email")
				if user_email:
					# ตั้งค่าหัวข้อและเนื้อหาอีเมล
					subject = message or f"คำขอเบิกค่าใช้จ่ายใหม่รอการอนุมัติ: {self.name}"
					content = f"""
					<p>เรียน {frappe.db.get_value("User", single_user, "full_name") or single_user}</p>
					<p>{subject}</p>
					<p>คุณสามารถเข้าดูรายละเอียดเพิ่มเติมได้ที่ลิงก์ด้านล่าง:</p>
					<p><a href="{frappe.utils.get_url()}/intranet/advance-entry/{self.name}">คลิกที่นี่เพื่อดูรายละเอียด</a></p>
					<p>ขอแสดงความนับถือ</p>
					<p>ระบบแจ้งเตือนอัตโนมัติ</p>
					"""
					
					# ส่งอีเมล
					frappe.sendmail(
						recipients=[user_email],
						subject=subject,
						message=content,
						reference_doctype=self.doctype,
						reference_name=self.name
					)
			except Exception as e:
					frappe.errprint(f"Failed to send email: {str(e)}")
   