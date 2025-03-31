# Copyright (c) 2024, beansx and contributors
# For license information, please see license.txt

import frappe
from frappe.model.document import Document
from frappe import _
from datetime import datetime, timedelta

from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from email.mime.base import MIMEBase
from email import encoders
import smtplib

  
class SMOTask(Document):
    def validate(self):
        self.assign_to = self.get_assigned_users()
        self.title = f"{self.name} - {self.task_name}"
        
        self.set_times()
        
        # ถ้าไม่มี project แต่มี opcode ให้ค้นหา project จาก opcode
        # if not self.project and self.opportunity:
        #     project = frappe.get_value("Project", 
        #         filters={"custom_opportunity_id": self.opportunity},
        #         as_dict=True
        #     )
        #     if project:
        #         self.project = project.name
        #         project_doc = frappe.get_doc("Project", project.name)
        #         self.project_code = project_doc.name
        #         self.project_name = project_doc.project_name
        #     else:
        #         frappe.throw(_(f"No project found for opcode: {self.opportunity}"))
        
    def set_times(self):
        # คำนวณ start_time และ to_time จาก input
        self.start_time = f"{self.start_hour_input}:{self.start_minute_input}:00"
        self.to_time = f"{self.finish_hour_input}:{self.finish_minute_input}:00"
        
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
        self.send_task_email()
        if self.location in ["Office", "Remote"]:
            self.create_timesheet()

    def on_cancel(self):
        self.delete_todos()

    def create_todos(self):
        start_date = datetime.strptime(self.start_date, '%Y-%m-%d')
        
        # ถ้า expected_time_use น้อยกว่า 24 ชั่วโมง (86400 วินาที) ให้ใช้ start_date เป็น end_date
        if self.expected_time_use <= 86400:  # 24 * 60 * 60 วินาที
            end_date = start_date
        else:
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
                    # "status": "Closed" if self.location == "Office" else "Open",
                    "status": "Open"
                })
                todo.insert(ignore_permissions=True)
                current_date += timedelta(days=1)
    def send_task_email(self):
        try:
            # เช็คก่อนว่ามี email account หรือไม่
            if not frappe.db.exists('Email Account', {'default_outgoing': 1}):
                frappe.msgprint(_("No default outgoing email account found. Email notification will not be sent."))
                return
            
            email_settings = frappe.get_doc('Email Account', {'default_outgoing': 1})
            
            # แปลง self.start_date เป็น datetime ถ้าจำเป็น
            start_date = self.start_date
            if isinstance(self.start_date, str):
                start_date = datetime.strptime(self.start_date, '%Y-%m-%d')

            # วนลูปสหรับแต่ละวันในช่วงเวลา
            current_date = start_date
            end_date = datetime.strptime(self.finish_date or self.start_date, '%Y-%m-%d')
            while current_date <= end_date:
                # สร้างไฟล์ .ics ด้วยตนเอง
                attendees = "\n".join(
                    f"ATTENDEE;ROLE=REQ-PARTICIPANT;PARTSTAT=NEEDS-ACTION;RSVP=TRUE;CN={frappe.get_doc('Employee', member.employee).employee_name}:MAILTO:{frappe.get_doc('Employee', member.employee).personal_email or member.user}"
                    for member in self.team
                )

                # ตรวจสอบว่าเป็นทั้งวันหรือไม่
                if self.period == "All day":
                    dtstart = current_date.strftime('%Y%m%d')
                    dtend = (current_date + timedelta(days=1)).strftime('%Y%m%d')
                    dtstart_format = f"DTSTART;VALUE=DATE:{dtstart}"
                    dtend_format = f"DTEND;VALUE=DATE:{dtend}"
                else:
                    # รวมวันที่และเวลาเริ่มต้นที่วางแผนไว้
                    start_datetime = datetime.combine(
                        current_date.date(),
                        datetime.strptime(self.start_time, '%H:%M:%S').time()
                    )
                    # คำนวณเวลาสิ้นสุดโดยบวกเวลาที่คาดว่าจะใช้
                    end_datetime = start_datetime + timedelta(hours=self.expected_time_use/3600)
                    
                    dtstart = start_datetime.strftime('%Y%m%dT%H%M%S')
                    dtend = end_datetime.strftime('%Y%m%dT%H%M%S')
                    dtstart_format = f"DTSTART;TZID=Asia/Bangkok:{dtstart}"
                    dtend_format = f"DTEND;TZID=Asia/Bangkok:{dtend}"

                # สร้าง URL สำหรับ link กลับไปยัง document
                doc_url = f"{frappe.utils.get_url()}/app/smo-task/{self.name}?from_page=calendar"

                ics_content = f"""BEGIN:VCALENDAR
VERSION:2.0
PRODID:-//Smart Office Task Calendar//
METHOD:REQUEST
BEGIN:VTIMEZONE
TZID:Asia/Bangkok
X-LIC-LOCATION:Asia/Bangkok
BEGIN:STANDARD
TZOFFSETFROM:+0700
TZOFFSETTO:+0700
TZNAME:ICT
DTSTART:19700101T000000
END:STANDARD
END:VTIMEZONE
BEGIN:VEVENT
UID:{self.name}-{current_date.strftime('%Y%m%d')}@{frappe.local.site}
DTSTAMP:{datetime.now().strftime('%Y%m%dT%H%M%SZ')}
ORGANIZER;CN={frappe.session.user}:MAILTO:{frappe.session.user}
{attendees}
SUMMARY:{self.task_name}
{dtstart_format}
{dtend_format}
DESCRIPTION:Task: {self.task_name}\\nLocation: {self.location}\\nPriority: {self.priority}\\nProject: {self.project_code} - {self.project_name}\\n\\nView Task: {doc_url}
LOCATION:{self.location}
URL:{doc_url}
STATUS:CONFIRMED
SEQUENCE:0
END:VEVENT
END:VCALENDAR"""

                
                
                email_body = f"""
                Dear Team,

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

                # รวบรวมอีเมลของสมาชิกในทีม
                recipient_emails = [frappe.get_doc("Employee", member.employee).personal_email or member.user for member in self.team]
                msg['To'] = ", ".join(recipient_emails)

                # สร้าง alternative part
                alt = MIMEMultipart('alternative')
                
                # เพิ่ม text part
                text_part = MIMEText(email_body, 'plain')
                alt.attach(text_part)
                
                # เพิ่ม calendar part
                cal_part = MIMEText(ics_content, 'text/calendar; method=REQUEST; charset=UTF-8')
                cal_part.add_header('Content-Disposition', 'inline; filename=invite.ics')
                cal_part.add_header('Content-Class', 'urn:content-classes:calendarmessage')
                alt.attach(cal_part)
                
                msg.attach(alt)

                with smtplib.SMTP(email_settings.smtp_server, email_settings.smtp_port) as server:
                    if email_settings.use_tls:
                        server.starttls()
                    # เช็คว่ามี password หรือไม่
                    if email_settings.password:
                        server.login(email_settings.email_id, email_settings.get_password())
                    server.send_message(msg)

                current_date += timedelta(days=1)

        except Exception as e:
            frappe.throw(f"Failed to send calendar invitation: {str(e)}")
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
