# Copyright (c) 2024, beansx and contributors
# For license information, please see license.txt

import frappe
from frappe.model.document import Document


class SMOExpenseRequest(Document):
	def before_save(self):
		if self.workflow_state != "Draft":
			for item in self.expense_request_item:
				frappe.db.set_value("SMO Expense Entry", item.expense, "is_request", 1)
	def on_cancel(self):
		for item in self.expense_request_item:
				frappe.db.set_value("SMO Expense Entry", item.expense, "is_request", 0)
	def after_delete(self):
		for item in self.expense_request_item:
				frappe.db.set_value("SMO Expense Entry", item.expense, "is_request", 0)
