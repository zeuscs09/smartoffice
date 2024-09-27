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
