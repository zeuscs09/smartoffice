import frappe
from frappe import _

@frappe.whitelist()
def check_user_task(user,activity_date):
   
    
    # Query ข้อมูลจากฐานข้อมูล
    expense_entries = frappe.db.sql("""
       select
            task.name task_id
        from
        `tabSMO Task` task inner join
        `tabSMO Working Team` team on task.name=team.parent and team.parenttype='SMO Task' and team.parentfield='team'
        where
            team.user=%(user)s
            and task.start_date= %(activity_date)s
            and task.status not in ('Cancel','Completed')
           
    """, {
        "user": user,
        "activity_date": activity_date,
       
    }, as_dict=True)

    # Return ข้อมูลออกมาในรูปแบบ JSON
    return expense_entries


@frappe.whitelist()
def get_todos_with_smo_tasks():
    user = frappe.session.user
    query = """
    SELECT 
        t.name, t.description, t.status, t.allocated_to, t.reference_name,
        s.project_name project, s.site, s.contact_name contact_person, s.contact_mobile as contact_phone, s.contact_email,
        s.start_date, s.finish_date, s.job_type, t.priority,
        cs.site_name,t.date due_date
    FROM 
        `tabToDo` t
    LEFT JOIN 
        `tabSMO Task` s ON t.reference_name = s.name
    LEFT JOIN
        `tabSMO Customer Site` cs ON s.site = cs.name
    WHERE 
        t.allocated_to = %s 
        AND t.reference_type = 'SMO Task'
        AND t.status = 'Open'
    ORDER BY 
        t.date asc
    
    """
    
    result = frappe.db.sql(query, (user,), as_dict=True)
    return result