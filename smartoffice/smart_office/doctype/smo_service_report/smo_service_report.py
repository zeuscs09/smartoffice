# Copyright (c) 2024, beansx and contributors
# For license information, please see license.txt

import frappe
from frappe import _
from frappe.model.document import Document


class SMOServiceReport(Document):
	def before_insert(self):
		task_status = frappe.db.sql("""
										SELECT task.name 
										FROM `tabSMO Service Report` sv 
										INNER JOIN `tabSMO Task` task 
										ON sv.task = task.name 
										WHERE task.status  IN ('Completed', 'Cancel', 'In Review')
										AND sv.task = %s
									""", (self.task))

		if task_status:
			frappe.throw(_("This task has already been created in a service report with an active status."))
	
	def on_submit(self):
		doc=self
		plan_task = frappe.get_doc("SMO Task", doc.task)
		plan_task.status = "Completed"
		plan_task.save()
		# frappe.msgprint("Submited document and update Task " +plan_task.task_name +" finish.")

	def on_update(self):
		doc=self
		# frappe.throw(doc.workflow_state)
		if doc.workflow_state=="Customer Review" or doc.workflow_state=="Draft":
			plan_task = frappe.get_doc("SMO Task", doc.task)
			plan_task.status = "In Review"
			plan_task.save()
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
