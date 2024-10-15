# Copyright (c) 2024, beansx and contributors
# For license information, please see license.txt

import frappe
from frappe.model.document import Document
from datetime import datetime, timedelta

  
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

    def on_submit(self):
        self.create_todos()

    def on_cancel(self):
        self.delete_todos()

    def create_todos(self):
        start_date = datetime.strptime(self.start_date, '%Y-%m-%d')
        end_date = datetime.strptime(self.finish_date or self.start_date, '%Y-%m-%d')
        
        for team_member in self.team:
            current_date = start_date
            while current_date <= end_date:
                todo = frappe.get_doc({
                    "doctype": "ToDo",
                    "owner": frappe.session.user,
                    "assigned_by": frappe.session.user,
                    "reference_type": self.doctype,
                    "reference_name": self.name,
                    "description": f"{self.task_name}",
                    "date": current_date.strftime('%Y-%m-%d'),
                    "allocated_to": team_member.user,
                    "priority": self.priority,
                    "status": "Open"
                })
                todo.insert(ignore_permissions=True)
                current_date += timedelta(days=1)

    def delete_todos(self):
        todos = frappe.get_all("ToDo", 
                               filters={
                                   "reference_type": self.doctype,
                                   "reference_name": self.name
                               },
                               pluck="name")
        for todo in todos:
            frappe.delete_doc("ToDo", todo, ignore_permissions=True)

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
