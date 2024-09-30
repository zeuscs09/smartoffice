# Copyright (c) 2024, beansx and contributors
# For license information, please see license.txt

import frappe

def execute(filters=None):
    user = frappe.session.user  # ดึง username ของผู้ใช้งานที่ล็อกอินอยู่
    query = """
        select 
            task.assign_to,
            task.customer_name,
            task.job_type,
            task.start_date,
            task.project,
            task.site,
            1 as add_total_row
        from `tabSMO Working Team` u 
        inner join `tabSMO Task` task on task.name=u.parent 
        and u.parenttype='SMO Task' 
        and u.parentfield='team'
        where u.user = %(user)s
        order by task.start_date asc
    """
    data = frappe.db.sql(query, {"user": user}, as_dict=True)

    # ระบุคอลัมน์ที่จะแสดงผล
    columns = [
        {"label": "Assign To", "fieldname": "assign_to", "fieldtype": "Data"},
        {"label": "Customer Name", "fieldname": "customer_name", "fieldtype": "Data"},
        {"label": "Job Type", "fieldname": "job_type", "fieldtype": "Data"},
        {"label": "Start Date", "fieldname": "start_date", "fieldtype": "Date"},
        {"label": "Project", "fieldname": "project", "fieldtype": "Data"},
        {"label": "Site", "fieldname": "site", "fieldtype": "Data"},
     
    ]

    return columns, data

# where u.user = %(user)s