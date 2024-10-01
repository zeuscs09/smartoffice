# Copyright (c) 2024, beansx and contributors
# For license information, please see license.txt

import frappe
from frappe.model.document import Document


class SMOTask(Document):
    def validate(self):
        # Check if self.team is a list
        if isinstance(self.team, list):
            user_list = []
            # Loop through each team in the self.team list
            for team in self.team:
                # Check if the team object has a 'user' attribute
                if hasattr(team, 'user'):
                    # If 'user' is a list, extend the user_list with its values
                    if isinstance(team.user, list):
                        user_list.extend(team.user)
                    else:
                        # If 'user' is not a list, convert it to a string and append it
                        user_list.append(str(team.user))
            # Join all users in the list with a comma and assign to self.assign_to
            self.assign_to = ",".join(user_list)
        else:
            # If there is no team, set assign_to to None
            self.assign_to = None
        self.title=self.name + ' - ' + self.task_name
        
@frappe.whitelist()
def fetch_task_data(task):
    # ตรวจสอบว่ามีการส่ง task เข้ามา
    if not task:
        frappe.throw(_("Task is required"))
    
    # ดึงข้อมูลจาก SMO Task
    task_doc = frappe.get_doc("SMO Task", task)
    
        
    task_items = []

    for item in task_doc.team:
        task_items.append({
            'user': item.user,
            'email': item.email,
            'full_name':item.full_name,
            'overlapping_job_on_date': item.overlapping_job_on_date,
            'filter': item.filter,
            # เพิ่มฟิลด์ที่ต้องการดึงข้อมูลอื่น ๆ
                    })

    return task_items
