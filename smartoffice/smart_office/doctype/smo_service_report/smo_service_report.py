# Copyright (c) 2024, beansx and contributors
# For license information, please see license.txt

import frappe
from frappe import _
from frappe.model.document import Document
from frappe.utils import getdate,time_diff_in_seconds,add_to_date
from datetime import datetime,timedelta

class SMOServiceReport(Document):
    
	def before_save(self):
		pass

	def after_insert(self):
		 # สร้าง Timesheet ใหม่
		pass
	
	def on_submit(self):
		doc=self
		plan_task = frappe.get_doc("SMO Task", doc.task)
		plan_task.status = "Completed"
		plan_task.save()
  
		self.create_timesheet()
		# frappe.msgprint("Submited document and update Task " +plan_task.task_name +" finish.")

	def on_update(self):
		doc=self
		# frappe.throw(doc.workflow_state)
		if doc.workflow_state=="Customer Review" or doc.workflow_state=="Draft":
			plan_task = frappe.get_doc("SMO Task", doc.task)
			plan_task.status = "In Process"
			plan_task.save()
		# if doc.workflow_state=="Customer Approve":
		# 	self.create_timesheet()
		# # check and set holiday
			# วันที่ที่ต้องการตรวจสอบ
	
	def on_cancel(self):
		doc=self
		plan_task = frappe.get_doc("SMO Task", doc.task)
		plan_task.status = "On Hold"
		plan_task.save()
	
	def after_delete(self):
		doc=self
		plan_task = frappe.get_doc("SMO Task", doc.task)
		plan_task.status = "On Hold"
		plan_task.save()
	
	def validate(self):
        		# duration
		check_date = getdate(self.job_start_on)

		# รัน query เพื่อเช็ควันหยุด
		result = frappe.db.sql("""
			SELECT GROUP_CONCAT(hd.description SEPARATOR ', ') as holiday_description
			FROM `tabHoliday List` hl
			INNER JOIN (
				SELECT holiday_date, parent, description 
				FROM `tabHoliday` 
				WHERE parentfield = 'holidays' 
				AND parenttype = 'Holiday List'
			) hd ON hl.name = hd.parent
			WHERE %s BETWEEN hl.from_date AND hl.to_date
			AND hd.holiday_date = %s
		""", (check_date, check_date), as_dict=True)
		
		# ถ้ามีรายการวันหยุด
		if result and result[0].holiday_description:
			# ตั้งค่าให้ฟิลด์ is_holiday และ holiday_description
			self.is_holiday = 1
			self.holiday_description = result[0].holiday_description
			
		else:
			# ถ้าไม่มีวันหยุด ตั้งค่า is_holiday เป็น 0 หรือค่าอื่นๆ
			self.is_holiday = 0
			self.holiday_description = None
		
		

		d = time_diff_in_seconds(self.job_finish,self.job_start_on) 
		# frappe.errprint(f"Duration in seconds: {d}")
		self.duration = d
	
	def create_timesheet(self):
		for item in self.team:
			employee = frappe.get_last_doc('Employee', filters={"user_id": item.user})
			timesheet = frappe.get_doc({
				'doctype': 'Timesheet',
				'company': employee.company,
				'employee': employee.name,
				
				'time_logs': [
					{
						'activity_type': 'Service Customer',
						'from_time': self.job_start_on,
						'hours': self.duration/3600,
						'completed':1
					}
				]
			})
			
			if self.customer:
				timesheet.customer = self.customer
			if self.project_link:
				timesheet.project = self.project_link
				timesheet.time_logs[0].project = self.project_link
			# บันทึก Timesheet
			timesheet.flags.ignore_validate = True
			timesheet.insert(ignore_permissions=True)
			
			# หากต้องการส่ง Timesheet โดยข้าม validation
			timesheet.submit()
			# frappe.msgprint(f"Timesheet {timesheet.name} created successfully.")
# def before_insert(self):
	# 	task_status = frappe.db.sql("""
	# 									SELECT task.name 
	# 									FROM `tabSMO Service Report` sv 
	# 									INNER JOIN `tabSMO Task` task 
	# 									ON sv.task = task.name 
	# 									WHERE task.status  IN ('Completed', 'Cancel', 'In Review')
	# 									AND sv.task = %s
	# 								""", (self.task))

	# 	if task_status:
	# 		frappe.throw(_("This task has already been created in a service report with an active status."))