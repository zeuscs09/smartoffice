# Copyright (c) 2025, beansx and contributors
# For license information, please see license.txt

# import frappe
from frappe.model.document import Document


class ThaiAddress(Document):
	def validate(self):
		# สร้าง full_address จากข้อมูลที่กรอก
		address_parts = []
		
		if self.province:
			address_parts.append(self.province)
		if self.amphoe:
			address_parts.append(self.amphoe)
		if self.tambol:
			address_parts.append(self.tambol)
		if self.zipcode:
			address_parts.append(self.zipcode)
			
		self.full_address = " >> ".join(address_parts)
