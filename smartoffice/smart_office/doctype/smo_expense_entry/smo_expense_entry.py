# Copyright (c) 2024, beansx and contributors
# For license information, please see license.txt

import frappe
from frappe.model.document import Document
from frappe import _
from smartoffice.utils.approval_utils import get_approval_chain,get_next_action
def is_user_in_team(user, team_name):
    # ดึงข้อมูลทีมจากฐานข้อมูล
    team_members = frappe.get_all("SMO Working Team", filters={"parent": team_name,"parenttype":"SMO Service Report","parentfield":"team","user":user}, fields=["user"])
    
    # ตรวจสอบว่า user อยู่ในทีมนี้หรือไม่
    return any(member.user == user for member in team_members)

class SMOExpenseEntry(Document):

	def validate(self):
     
		frappe.errprint(self.workflow_state);
		# ตรวจสอบว่า user ที่ล็อกอินอยู่ในทีมที่เกี่ยวข้องหรือไม่
		if self.workflow_state == "Draft":
			if not is_user_in_team(frappe.session.user, self.service_report):
				frappe.throw(_(f"ไม่สามารถเลือก Service report {self.service_report} เนื่องจากไม่ได้เป็นส่วหนึ่งของทีมที่เกี่ยวข้อง"))
			self.set_approvers()
			self.reject_reason = None
				
		
		# elif self.workflow_state=="Rejected":
		# 	self.next_action = frappe.session.user
		# elif self.workflow_state=="Approved":
		# 	self.next_action = ""
   
		total_cost = 0
		seen_expense = set()
		
		for item in self.expense_item:
			
			# ตรวจสอบรายการซ้ำเฉพาะ expense_type EXP001, EXP002
			if item.expense_type in ["EP001", "EP002"]:
    			# ตรวจสอบ depart distance
				if item.cal_taxi_depart_distance is not None and item.taxi_depart_distance is not None:
					if float(item.cal_taxi_depart_distance) != float(item.taxi_depart_distance):
						item.w_edit_depart = f"Edit Distance from {format(float(item.cal_taxi_depart_distance), '.2f')} to {format(float(item.taxi_depart_distance), '.2f')}"
					else:
						item.w_edit_depart = ""
				else:
					item.w_edit_depart = ""

				# ตรวจสอบ return distance
				if item.cal_taxi_return_distance is not None and item.taxi_return_distance is not None:
					if float(item.cal_taxi_return_distance) != float(item.taxi_return_distance):
						item.w_edit_return = f"Edit Distance from {format(float(item.cal_taxi_return_distance), '.2f')} to {format(float(item.taxi_return_distance), '.2f')}"
					else:
						item.w_edit_return = ""
				else:
					item.w_edit_return = ""
     
				item_key = (item.expense_type)  # ปรับตามโครงสรางข้อมูลจริงของคุณ
				if item_key in seen_expense:
						doc_expense_type=frappe.get_doc("SMO Expense Type", item.expense_type)
						
						frappe.throw(f"Duplicate expense found: {doc_expense_type.description} ")
				seen_expense.add(item_key)
    
			# สร้าง reminder string จาค่าที่มีอยู่เท่านั้น
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
		self.validate_expense_claim()
	
			
		# if self.workflow_state == "Approval Review":
		# 	self.check_service_report_status()
   
	def validate_expense_claim(self):
		
		if self.workflow_state == "Draft":
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
                        and ei.expense_type   in ('EP001','EP002')
					GROUP BY ei.expense_type
				""", (self.service_report, item.expense_type, self.name), as_dict=True)
				
				for row in result:
					total_count = row['total_count']  # จำนวนรวม
					requested_by = row['requested_by']  # ายชื่อผู้ขอ (concat แล้ว)
					frappe.msgprint(item.system_reminder)
					if not item.system_reminder:
						item.system_reminder = f"รายการค่าใช้จ่าย {item.expense_type_name} ถูกบันทึกแล้ว {int(total_count)} ครั้ง โดย {requested_by}"
						frappe.msgprint(item.system_reminder)
	
			
	def on_update(self):
		"""สำหรับ Draft และ Approval Review"""
		pass

	def on_submit(self):
     	
		self.check_service_report_status()
		# บนทึก receive_date ให้ admin (approver คนแรก)
		first_approver = next((a for a in self.approvers if a.approver_level == 1), None)
		if first_approver:
			first_approver.receive_date = frappe.utils.now()
			first_approver.status = "Pending"
			first_approver.db_update()
			# แจ้งเตือน admin
			self.create_notification(
				first_approver.user_id,
				f"มีคำขอเบิกค่าใช้จ่ายใหม่รอการตรวจสอบ: {self.name}"
			)
		

	def on_update_after_submit(self):
		# frappe.errprint(self.has_value_changed("workflow_state"));
		# if self.has_value_changed("workflow_state"):
		self.set_approver_status()
		
			
			# current_approver.db_update()
			# self.db_update()

	def set_approvers(self):
		# เคลียร์ข้อมูลผู้อนุมัติเดิม
		self.approvers = []
		self.max_level = 0
		self.next_action = ""
		self.workflow_description = ""

		# ตึง designation จาก setting
		admin_designation = frappe.get_doc("Smart Office Setting").admin_user
		if not admin_designation:
			frappe.throw("Not found admin designation")

		# ดึง employees ทั้งหมดที่มี designation นี้ และมี user_id
		admin_employees = frappe.get_all(
			"Employee",
			filters={
				"status": "Active",
				"designation": admin_designation
			},
			fields=["user_id"]
		)

		if not admin_employees:
			frappe.throw(f"No employees found with designation: {admin_designation}")

		# กรองเฉพาะ employees ที่มี user_id
		admin_users = [emp.user_id for emp in admin_employees if emp.user_id]
		
		if not admin_users:
			frappe.throw(f"No user accounts found for employees with designation: {admin_designation}")

		# แปลง list ของ users เป็น string คั่นด้วย comma
		admin_user_list = ", ".join(admin_users)

		# เรียกใช้ approval_utils เพื่อสร้าง approval chain
		approvers, max_level, next_user = get_approval_chain(
			total_amount=self.total_amount,
			request_by=frappe.session.user,
			flow_type="Expense Entry"
		)

		# เพิ่ม admin users ทั้งหมดเป็นคนแรก
		
		self.append("approvers", {
			"approver": admin_user_list,
			"user_id": admin_user_list,
			"approver_level": 1,
			"approver_role": "Admin",
			"status": ""
		})

		# ปรับ level ของ approvers ที่เหลือให้เริ่มจาก 2
		for approver_data in approvers:
			self.append("approvers", {
				"approver": approver_data.approver,
				"user_id": approver_data.user_id,
				"approver_level": approver_data.approver_level + 1,  # เพิ่ม level อีก 1
				"approver_role": approver_data.approver_role,
				"status": approver_data.status
			})

		self.max_level = max_level + 1  # เพิ่ม max_level อีก 1 เนื่องจากเพิ่ม admin
		self.next_action = admin_user_list  # กำหนด next_user เป็น admin

	def create_notification(self, user_ids, message):
		# ถ้า user_ids เป็น string ที่มี comma ให้แยกเป็น list
		if isinstance(user_ids, str) and ',' in user_ids:
			user_list = [u.strip() for u in user_ids.split(',')]
		else:
			user_list = [user_ids]

		# สร้าง notification สำหรับแต่ละ user
		for user_id in user_list:
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
			try:
					# ดึงข้อมูลอีเมลของผู้ใช้
				user_email = frappe.db.get_value("User", user_id, "email")
				if user_email:
					# ตั้งค่าหัวข้อและเนื้อหาอีเมล
					subject = message or f"คำขอเบิกค่าใช้จ่ายใหม่รอการอนุมัติ: {self.name}"
					content = f"""
					<p>เรียน {frappe.db.get_value("User", user_id, "full_name") or user_id}</p>
					<p>{subject}</p>
					<p>คุณสามารถเข้าดูรายละเอียดเพิ่มเติมได้ที่ลิงก์ด้านล่าง:</p>
					<p><a href="{frappe.utils.get_url()}/intranet/expense-entry/{self.name}">คลิกที่นี่เพื่อดูรายละเอียด</a></p>
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
   
	def check_service_report_status(self):
		if self.service_report:
			service_report_status = frappe.db.get_value("SMO Service Report", self.service_report, "workflow_state")
			if service_report_status != "Customer Approved":
				frappe.throw(_("ไม่สามารถส่งรายการค่าใช้จ่ายได้ เนื่องจากลูกค้ายังไม่อนุมัติ Service Report"))

	def before_cancel(self):
		# อัพเดท workflow_state เป็น Rejected
		self.workflow_state = "Rejected"
		self.db_update()
	
	def set_approver_status(self):
		current_approver = next((a for a in self.approvers 
							   if frappe.session.user in (a.user_id + ", ")), None)
		
		if current_approver:
			if self.workflow_state in ["Pending Approval", "Approved", "Rejected"]:
				# บันทึกเวลาที่ดำเนินการและสถานะ
				current_approver.action_date = frappe.utils.now()
				current_approver.status = "Rejected" if self.workflow_state == "Rejected" else "Approved"
				
				# คำนวณระยะเวลาที่ใช้
				if current_approver.receive_date:
					duration = frappe.utils.time_diff_in_seconds(
						current_approver.action_date,
						current_approver.receive_date
					)
					current_approver.duration = duration
				
				if self.workflow_state == "Pending Approval":
					# ใช้ get_next_action เพื่อหาคนถัดไป
					next_user, next_level, is_last = get_next_action(self.approvers)
				
					if next_user:
						# หา approver คนถัดไปและบันทึก receive_date
						next_approver = next((a for a in self.approvers if a.user_id == next_user), None)
						frappe.errprint(next_approver.status);
						frappe.errprint(next_approver.receive_date);
						if next_approver:
							next_approver.receive_date = frappe.utils.now()
							next_approver.status = "Pending"
							next_approver.db_update()
							self.next_action = next_user
							# แจ้งเตือนผู้อนุมัติคนถัดไป
							self.create_notification(
								next_user,
								f"มีคำขอเบิกค่าใช้จ่ายรอการอนุมัติ: {self.name}"
							)
					elif is_last:  # ถ้าเป็นการอนุมัติครั้งสุดท้าย
						# แจ้งผู้ขอ
						self.next_action = ""
						self.create_notification(
							self.owner,
							f"คำขอเบิกค่าใช้จ่ายของคุณได้รับการอนุมัติแล้ว: {self.name}"
						)
				elif self.workflow_state == "Approved":
					self.next_action = ""
					self.create_notification(
						self.owner,
						f"คำขอเบิกค่าใช้จ่ายของคุณได้รับการอนุมัติแล้ว: {self.name}"
					)
				elif self.workflow_state == "Rejected":
					# แจ้งเตือนผู้ขอกรณีถูกปฏิเสธ
					self.next_action = ""
					current_approver.comment = self.reject_reason
					reject_message = f"คำขอเบิกค่าใช้จ่ายของคุณถูกปฏิเสธ: {self.name}"
					if self.reject_reason:
						reject_message += f"\nเหตุผล: {self.reject_reason}"
					self.create_notification(self.owner, reject_message)
				current_approver.db_update()
				self.db_update()
