# Copyright (c) 2024, beansx and contributors
# For license information, please see license.txt

import frappe
from frappe.model.document import Document


class SMOTask(Document):
    def validate(self):
        self.assign_to = self.get_assigned_users()
        self.title = f"{self.name} - {self.task_name}"

    def get_assigned_users(self):
        if not isinstance(self.team, list):
            return None
        return ",".join(
            str(team.user) if isinstance(team.user, str) else ",".join(map(str, team.user))
            for team in self.team
            if hasattr(team, 'user')
        )

@frappe.whitelist()
def fetch_task_data(task):
    if not task:
        frappe.throw(_("Task is required"))
    
    task_doc = frappe.get_doc("SMO Task", task)
    
    return [
        {
            'user': item.user,
            'email': item.email,
            'full_name': item.full_name,
            'overlapping_job_on_date': item.overlapping_job_on_date,
            'filter': item.filter,
        }
        for item in task_doc.team
    ]
