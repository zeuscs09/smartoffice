# Copyright (c) 2024, beansx and contributors
# For license information, please see license.txt

import frappe
from frappe.model.document import Document
from frappe import _
from datetime import datetime, timedelta
try:
    from icalendar import Calendar, Event, vText
except ImportError:
    frappe.throw(_("Please install icalendar package: pip install icalendar"))
    
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from email.mime.base import MIMEBase
from email import encoders
import smtplib

  
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
        if self.location == "Office":
            self.create_timesheet()

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
                    "priority": "Medium" if self.priority == "Normal" else self.priority,
                    "status": "Closed" if self.location == "Office" else "Open"
                })
                todo.insert(ignore_permissions=True)

                try:
                    
                    employee = frappe.get_doc("Employee", team_member.employee)
                    cal = Calendar()
                    cal.add('prodid', '-//Smart Office Task Calendar//')
                    cal.add('version', '2.0')

                    event = Event()
                    event.add('status', 'CONFIRMED')
                    event.add('method', 'REQUEST')
                    event.add('sequence', 0)
                    event['uid'] = f"{self.name}@{frappe.local.site}"
                    event.add('organizer', f"mailto:{frappe.session.user}")
                    event.add('attendee', f"mailto:{employee.personal_email or employee.user_id}")
                    event.add('summary', self.task_name)
                    event.add('dtstart', current_date)
                    event.add('dtend', current_date + timedelta(hours=self.expected_time_use/3600))
                    event.add('description', f"""
                        Task: {self.task_name}
                        Location: {self.location}
                        Priority: {self.priority}
                        Project: {self.project_code} - {self.project_name}
                    """)
                    event.add('location', self.location)
                    event.add('priority', 5 if self.priority == "Normal" else 1)
                    
                    cal.add_component(event)

                    email_settings = frappe.get_doc('Email Account', {'default_outgoing': 1})
                    
                    email_body = f"""
                    Dear {employee.employee_name},

                    You have been assigned a new task:
                    Project: {self.project_code} - {self.project_name}
                    Task Name: {self.task_name}
                    Start Date: {self.start_date}
                    End Date: {self.finish_date or self.start_date}
                    Location: {self.location}
                    Priority: {self.priority}

                    Please find attached the calendar invitation.

                    Best regards,
                    {frappe.session.user}
                    """

                    msg = MIMEMultipart('mixed')
                    msg['Subject'] = f"New Task Assignment: {self.task_name}"
                    msg['From'] = email_settings.email_id
                    recipient_email = employee.personal_email or employee.user_id
                    msg['To'] = recipient_email

                    # สร้าง alternative part
                    alt = MIMEMultipart('alternative')
                    
                    # เพิ่ม text part
                    text_part = MIMEText(email_body, 'plain')
                    alt.attach(text_part)
                    
                    # เพิ่ม calendar part
                    cal_part = MIMEText(cal.to_ical().decode('utf-8'), 'text/calendar; method=REQUEST; charset=UTF-8')
                    cal_part.add_header('Content-Disposition', 'attachment; filename=invite.ics')
                    alt.attach(cal_part)
                    
                    msg.attach(alt)

                    with smtplib.SMTP(email_settings.smtp_server, email_settings.smtp_port) as server:
                        server.starttls()
                        server.login(email_settings.email_id, email_settings.get_password())
                        server.send_message(msg)
                    # frappe.msgprint(_(f"Calendar invitation sent to {recipient_email}"))
                except Exception as e:
                    frappe.throw(f"Failed to send calendar invitation to {recipient_email}: {str(e)}")
                
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

    def create_timesheet(self):
        created_timesheets = []  # เก็บรายการ timesheet ที่สร้าง
        for item in self.team:
            try:
                employee = frappe.get_doc('Employee', {"user_id": item.user})
                
                timesheet = frappe.get_doc({
                    'doctype': 'Timesheet',
                    'company': employee.company,
                    'employee': employee.name,
                    'time_logs': [{
                        'activity_type': 'Office Work',
                        'from_time': self.start_date,
                        'hours': self.expected_time_use / 3600,
                        'completed': 1,
                        'project': self.project
                    }]
                })
                
                if self.customer:
                    timesheet.customer = self.customer
                
                try:
                    timesheet.flags.ignore_validate = True
                    timesheet.insert(ignore_permissions=True)
                    timesheet.submit()
                    created_timesheets.append(timesheet.name)  # เก็บชื่อ timesheet
                    # frappe.msgprint(_(f"Timesheet {timesheet.name} created for {employee.employee_name}"))
                except Exception as e:
                    frappe.log_error(f"Failed to create timesheet for {employee.employee_name}: {str(e)}")
                    frappe.throw(_(f"Could not create timesheet for {employee.employee_name}: {str(e)}"))
                
            except frappe.DoesNotExistError:
                frappe.log_error(f"Employee not found for user: {item.user}")
                frappe.throw(_(f"Employee not found for user: {item.user}"))
            except Exception as e:
                frappe.log_error(f"Error creating timesheet: {str(e)}")
                frappe.throw(_(f"Error creating timesheet: {str(e)}"))
        
        return created_timesheets  # ส่งคืนรายการ timesheet ที่สร้างทั้งหมด
@frappe.whitelist()
def fetch_task_data(task):
    if not task:
        frappe.throw(_("Task is required"))
    
    task_doc = frappe.get_doc("SMO Task", task)
    
    return [
        {
            'employee': item.employee,
            'user': item.user,
            'email': item.email,
            'full_name': item.full_name,
            'overlapping_job_on_date': item.overlapping_job_on_date,
            'filter': item.filter,
        }
        for item in task_doc.team
    ]
