# Copyright (c) 2024, beansx and contributors
# For license information, please see license.txt

import frappe
from frappe.model.document import Document


class SMOAdvanceEntry(Document):
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

		for item in self.expense_item:
			item.paid_by="เงินทดรอง"
			item.ref_code=self.reference_code
