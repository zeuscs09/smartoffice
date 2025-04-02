# Copyright (c) 2025, beansx and contributors
# For license information, please see license.txt

import frappe
from frappe.model.document import Document
from frappe.utils import getdate, get_datetime, get_time, time_diff_in_hours
import calendar

class SMOTimesheet(Document):
	def validate(self):
		# แปลงเดือนจากชื่อเป็นตัวเลข
		months = {
			'January': '1', 'February': '2', 'March': '3', 'April': '4',
			'May': '5', 'June': '6', 'July': '7', 'August': '8',
			'September': '9', 'October': '10', 'November': '11', 'December': '12'
		}
		
		if self.month:
			self.month_value = months.get(self.month, '')
		
		# ดึงข้อมูล Approver จาก report_to ของ employee
		if self.employee:
			employee_doc = frappe.get_doc("Employee", self.employee)
			if employee_doc.reports_to:
				# ดึง user_id จาก employee ที่เป็น reports_to
				reports_to_user = frappe.db.get_value("Employee", employee_doc.reports_to, "user_id")
				if reports_to_user:
					self.approver = reports_to_user
				else:
					self.approver = ""
			else:
				# ถ้าไม่มี reports_to ให้เคลียร์ค่า approver
				self.approver = ""
		if not self.approver:
			frappe.throw( self.employee + " ไม่มีผู้อนุมัติ")
		total_hours = 0
		for time_sheet in self.time_sheets:
			total_hours += time_sheet.working_hours
		self.total_hours = total_hours
	def on_submit(self):
		self.create_notification(self.approver, "Timesheet รอการอนุมัติ: " + self.name)
	
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
					subject = message or f"Timesheet รอการอนุมัติ: {self.name}"
					content = f"""
					<p>เรียน {frappe.db.get_value("User", user_id, "full_name") or user_id}</p>
					<p>{subject}</p>
					<p>คุณสามารถเข้าดูรายละเอียดเพิ่มเติมได้ที่ลิงก์ด้านล่าง:</p>
					<p><a href="{frappe.utils.get_url()}/intranet/timesheet/{self.name}">คลิกที่นี่เพื่อดูรายละเอียด</a></p>
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
   
@frappe.whitelist()
def get_timesheets(employee=None, year=None, month=None):
	if not employee or not year or not month:
		frappe.throw("กรุณาระบุ Employee, Year และ Month")

	# แปลงเดือนจากชื่อเป็นตัวเลข
	months = {
		'January': 1, 'February': 2, 'March': 3, 'April': 4,
		'May': 5, 'June': 6, 'July': 7, 'August': 8,
		'September': 9, 'October': 10, 'November': 11, 'December': 12
	}
	month_number = months.get(month)
	
	# คำนวณวันแรกและวันสุดท้ายของเดือน
	year_int = int(year)
	_, last_day = calendar.monthrange(year_int, month_number)
	start_date = f"{year}-{month_number:02d}-01"
	end_date = f"{year}-{month_number:02d}-{last_day}"
	
	result = []
	
	# ดึงรายการ doc_number ที่ถูกใช้ใน timesheet ที่ยังไม่ได้ยกเลิก
	used_docs = frappe.db.sql("""
		SELECT DISTINCT tsi.doc_number
		FROM `tabSMO Timesheet` ts
		JOIN `tabSMO Timesheet Item` tsi ON ts.name = tsi.parent
		WHERE ts.docstatus < 2  # 0 = Draft, 1 = Submitted
		AND ts.employee = %s
	""", (employee), as_dict=1)
	
	used_doc_numbers = [d.doc_number for d in used_docs]
	
	# ดึง Task ที่มีพนักงานอยู่ในทีม
	tasks_with_employee = frappe.db.sql("""
		SELECT DISTINCT parent 
		FROM `tabSMO Working Team` 
		WHERE employee = %s
	""", (employee), as_dict=1)
	
	task_names = [d.parent for d in tasks_with_employee]
	
	if task_names:
		# ดึง Task ที่ไม่มี Service Report และยังไม่ถูกใช้ใน timesheet
		tasks = frappe.get_all(
			"SMO Task",
			filters={
				"name": ["in", task_names],
				"name": ["not in", used_doc_numbers],  # เพิ่มเงื่อนไขนี้
				"start_date": ["between", [start_date, end_date]],
				"docstatus": 1
			},
			fields=["name", "start_date", "start_hour_input", "start_minute_input",
				   "finish_date", "finish_hour_input", "finish_minute_input",
				   "project_code", "customer", "expected_time_use","customer_name"]
		)

		# เพิ่มข้อมูลจาก Tasks
		for task in tasks:
			# ตรวจสอบว่ามี Service Report หรือไม่
			has_service_report = frappe.db.exists("SMO Service Report", {"task": task.name})
			if not has_service_report:
				from_time = get_datetime(f"{task.start_date} {task.start_hour_input}:{task.start_minute_input}:00")
				to_time = get_datetime(f"{task.finish_date} {task.finish_hour_input}:{task.finish_minute_input}:00")
				
				result.append({
					"from_time": from_time,
					"to_time": to_time,
					"working_hours": task.expected_time_use,
					"link_from_doc": "SMO Task",
					"doc_number": task.name,
					"project_code": task.project_code,
					"customer": task.customer,
					"customer_name": task.customer_name
				})

	# ดึง Service Reports ที่มีพนักงานอยู่ในทีม
	sr_with_employee = frappe.db.sql("""
		SELECT DISTINCT parent 
		FROM `tabSMO Working Team` 
		WHERE employee = %s
	""", (employee), as_dict=1)
	
	sr_names = [d.parent for d in sr_with_employee]
	
	if sr_names:
		# ดึง Service Reports ที่ยังไม่ถูกใช้ใน timesheet
		service_reports = frappe.get_all(
			"SMO Service Report",
			filters={
				"name": ["in", sr_names],
				"name": ["not in", used_doc_numbers],  # เพิ่มเงื่อนไขนี้
				"start_date_input": ["between", [start_date, end_date]],
				"docstatus": 1
			},
			fields=["name", "start_date_input", "start_hour_input", "start_minute_input",
				   "finish_date_input", "finish_hour_input", "finish_minute_input",
				   "project_code", "customer", "duration","customer_name"]
		)

		# เพิ่มข้อมูลจาก Service Reports
		for sr in service_reports:
			from_time = get_datetime(f"{sr.start_date_input} {sr.start_hour_input}:{sr.start_minute_input}:00")
			to_time = get_datetime(f"{sr.finish_date_input} {sr.finish_hour_input}:{sr.finish_minute_input}:00")
			
			result.append({
				"from_time": from_time,
				"to_time": to_time,
				"working_hours": sr.duration,
				"link_from_doc": "SMO Service Report",
				"doc_number": sr.name,
				"project_code": sr.project_code,
				"customer": sr.customer,
				"customer_name": sr.customer_name
			})
	
	# sort by from_time
	result.sort(key=lambda x: x['from_time'])
	return result
