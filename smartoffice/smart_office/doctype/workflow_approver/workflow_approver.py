# Copyright (c) 2024, beansx and contributors
# For license information, please see license.txt

import frappe
from frappe.model.document import Document
from frappe.utils import time_diff_in_seconds


class WorkflowApprover(Document):
	def validate(self):
		self.calculate_duration()

	def calculate_duration(self):
		if self.receive_date and self.action_date:
			duration_seconds = time_diff_in_seconds(self.action_date, self.receive_date)
			self.duration = duration_seconds
		else:
			self.duration = 0
