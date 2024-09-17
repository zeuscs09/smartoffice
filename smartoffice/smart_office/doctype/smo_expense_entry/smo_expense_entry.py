# Copyright (c) 2024, beansx and contributors
# For license information, please see license.txt

import frappe
from frappe.model.document import Document


class SMOExpenseEntry(Document):
	def validate(self):
		
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
	def before_save(self):
		if self.workflow_state != "Draft":
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
					GROUP BY ei.expense_type
				""", (self.service_report, item.expense_type, self.name), as_dict=True)
				
				for row in result:
					total_count = row['total_count']  # จำนวนรวม
					requested_by = row['requested_by']  # รายชื่อผู้ขอ (concat แล้ว)
					if not item.system_reminder :
						item.system_reminder = f"This item been entered {int(total_count)} times by {requested_by}."

