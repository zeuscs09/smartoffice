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
def get_todos_with_smo_tasks(page=1, page_size=10, search=None, status=None, start_date=None, end_date=None, sort_field=None, sort_order=None):
    user = frappe.session.user
    page = int(page)
    page_size = int(page_size)
    offset = (page - 1) * page_size
    
    conditions = ["t.allocated_to = %s", "t.reference_type = 'SMO Task'"]
    values = [user]
    
    if search:
        conditions.append("(t.name LIKE %s OR t.description LIKE %s OR s.project_name LIKE %s OR cs.site_name LIKE %s)")
        values.extend([f"%{search}%"] * 4)
    
    if status:
        conditions.append("t.status = %s")
        values.append(status)
   
    
    if start_date:
        conditions.append("t.date >= %s")
        values.append(start_date)
    
    if end_date:
        conditions.append("t.date <= %s")
        values.append(end_date)
    
    where_clause = " AND ".join(conditions)
    
    sort_clause = f"ORDER BY {sort_field} {sort_order}" if sort_field and sort_order else "ORDER BY t.date ASC"
    
    query = f"""
    SELECT 
        t.name, t.description, t.status, t.allocated_to, t.reference_name,
        s.project_name project, s.site, s.contact_name contact_person, s.contact_mobile as contact_phone, s.contact_email,
        s.start_date, s.finish_date, s.job_type, t.priority,
        cs.site_name, t.date due_date,s.assign_to ,
        COUNT(*) OVER () as ttl_records
    FROM 
        `tabToDo` t
    LEFT JOIN 
        `tabSMO Task` s ON t.reference_name = s.name
    LEFT JOIN
        `tabSMO Customer Site` cs ON s.site = cs.name
    WHERE 
        {where_clause}
    {sort_clause}
    LIMIT %s OFFSET %s
    """
    
    values.extend([page_size, offset])
    
    result = frappe.db.sql(query, tuple(values), as_dict=True)
    
    total_count = result[0].ttl_records if result else 0
    
    return {
        "data": [
            {k: v for k, v in item.items() if k != 'ttl_records'}
            for item in result
        ],
        "total": total_count,
        "page": page,
        "page_size": page_size,
        "total_pages": -(-total_count // page_size)  # การหารปัดขึ้น
    }
