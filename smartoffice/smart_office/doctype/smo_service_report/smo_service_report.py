# Copyright (c) 2024, beansx and contributors
# For license information, please see license.txt

import frappe
from frappe import _
from frappe.model.document import Document
from frappe.utils import getdate, time_diff_in_seconds, get_datetime, get_url, cint, format_datetime, format_date, format_time
import hashlib
import os
from frappe.utils import get_url, now
from urllib.parse import quote


class SMOServiceReport(Document):
    
	def before_save(self):
		pass

	def after_insert(self):
		pass
	
	def on_submit(self):
		
		self.create_timesheet()
  
		# ปิด ToDo ที่เชื่อมโยงกับ SMO Task
		
		
		# Redirect logic will be handled in JavaScript
	
	def on_update(self):
		frappe.errprint(f"Workflow State: {self.workflow_state}")
		if self.workflow_state == "Customer Review":
			if self.from_todo:
				todo = frappe.get_doc("ToDo", self.from_todo)
				todo.status = "Closed"
				todo.flags.ignore_permissions = True
				todo.save()
			self._update_task_status()
			self.notify_customer()

	def on_cancel(self):
		self._update_task_status("On Hold")

	def after_delete(self):
		self._update_task_status("On Hold")

	def validate(self):
		if self.workflow_state == "Draft":
			self._check_holiday()
			self._calculate_duration()
			self._check_overnight()
			self._set_approval_data()

	def _check_holiday(self):
		check_date = getdate(self.job_start_on)
		holiday = frappe.db.get_value("Holiday", 
			{"holiday_date": check_date, "parenttype": "Holiday List"},
			["description", "name"], as_dict=True)
		
		if holiday:
			self.is_holiday = 1
			self.holiday_description = holiday.description
		else:
			self.is_holiday = 0
			self.holiday_description = None

	def _calculate_duration(self):
		start = get_datetime(self.job_start_on)
		finish = get_datetime(self.job_finish)
		self.duration = time_diff_in_seconds(finish, start)

	def _check_overnight(self):
		start_date = getdate(self.start_date_input)
		finish_date = getdate(self.finish_date_input)
		self.over_night = (finish_date - start_date).days > 0

	def _update_task_status(self):
		if self.task:
			todos = frappe.get_all("ToDo", 
				filters={
					"reference_type": "SMO Task",
					"reference_name": self.task,
					"status": ["=", "Open"]
				},
				pluck="name"
			)
			frappe.errprint(f"Todos: {todos}")
			for todo_name in todos:
				todo = frappe.get_doc("ToDo", todo_name)
				todo.status = "Closed"
				todo.flags.ignore_permissions = True
				todo.save()

	def create_timesheet(self):
		for item in self.team:
			employee = frappe.get_doc('Employee', {"user_id": item.user})
			
			timesheet = frappe.get_doc({
				'doctype': 'Timesheet',
				'company': employee.company,
				'employee': employee.name,
				'time_logs': [{
					'activity_type': 'Service Customer',
					'from_time': self.job_start_on,
					'hours': self.duration / 3600,
					'completed': 1,
					'project': self.project_link,
					
				}]
			})
			
			if self.customer:
				timesheet.customer = self.customer
			
			timesheet.flags.ignore_validate = True
			timesheet.insert(ignore_permissions=True)
			timesheet.submit()

	def notify_customer(self):
		frappe.errprint(f"Notify Customer: {self.contact_email} {self.approval_hash}")
		if not self.contact_email or not self.approval_hash:
			return

		args = self.as_dict()
		
		# จัดรูปแบบวันที่และเวลา
		job_start = get_datetime(self.job_start_on)
		args['formatted_date'] = format_date(job_start, "dd MMMM yyyy")
		args['formatted_time'] = format_time(job_start)
		
		# สร้าง approve_link และ reject_link
		base_url = get_url("/servicereport_landing")
		common_params = f"name={quote(self.name)}&customer_email={quote(self.contact_email)}&hash={quote(self.approval_hash)}&timestamp={quote(self.approval_timestamp)}"
		
		args['approve_link'] = f"{base_url}?action=approve&{common_params}"
		args['reject_link'] = f"{base_url}?action=reject&{common_params}"

		# ดึง template จาก Smart Office Settings
		template = frappe.db.get_single_value("Smart Office Setting", "service_report_approval_template")
		if not template:
			frappe.msgprint(_("Please set default template for Service Report Review in Smart Office Settings."))
			return

		email_template = frappe.get_doc("Email Template", template)
		subject = frappe.render_template(email_template.subject, args)
		message = frappe.render_template(email_template.response, args)

		# เรียกใช้ฟังก์ชัน notify เพื่อส่งอีเมล
		self.notify({
			"message": message,
			"message_to": self.contact_email,
			"subject": subject,
		})

		frappe.msgprint(_("Notification email sent to customer for review."))

	def notify(self, args):
		args = frappe._dict(args)
		contact = args.message_to

		sender = dict()
		user = frappe.get_doc("User", frappe.session.user)
		sender["email"] = user.email
		sender["full_name"] = user.full_name

		frappe.errprint(f"Sender: {sender}")  # เพื่อตรวจสอบค่า

		try:
			frappe.sendmail(
				recipients=contact,
				sender=sender["email"],
				subject=args.subject,
				message=args.message,
			)
			frappe.msgprint(_("Email sent to {0}").format(contact))
		except frappe.OutgoingEmailError:
			frappe.log_error(f"Failed to send email for Service Report {self.name}")
			frappe.msgprint(_("Failed to send email. Please check error logs."))

	def _set_approval_data(self):
		if self.workflow_state == "Draft" and not self.approval_hash:
			# สร้าง salt
			salt = os.urandom(16).hex()
			
			# สร้าง hash
			timestamp = now()
			hash_string = f"{self.name}|{self.contact_email}|{timestamp}|{salt}"
			hash_object = hashlib.sha256(hash_string.encode())
			hash_value = hash_object.hexdigest()
			
			# บันทึก hash, salt และ timestamp
			self.approval_hash = hash_value
			self.approval_salt = salt
			self.approval_timestamp = timestamp

