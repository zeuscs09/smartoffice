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
    
    # เริ่มด้วย base conditions และ values
    conditions = []
    values = []
    
    # เงื่อนไขหลัก
    conditions.append("""
        (
            (t.allocated_to = %s AND t.reference_type = 'SMO Task')
            OR 
            (s.docstatus = 0 AND s.owner = %s)
        )
    """)
    values.extend([user, user])
    
    # เงื่อนไขการค้นหา
    if search:
        conditions.append("""
            (
                COALESCE(t.name, '') LIKE %s 
                OR COALESCE(t.description, '') LIKE %s 
                OR COALESCE(s.project_name, '') LIKE %s 
                OR COALESCE(cs.site_name, '') LIKE %s
            )
        """)
        values.extend([f"%{search}%"] * 4)
    
    # เงื่อนไขสถานะ
    if status:
        if status.lower() == 'draft':
            conditions.append("(s.docstatus = 0)")
        else:
            conditions.append("(t.status = %s)")
            values.append(status)
    
    # เงื่อนไขวันที่
    if start_date:
        conditions.append("COALESCE(t.date, s.start_date) >= %s")
        values.append(start_date)
    
    if end_date:
        conditions.append("COALESCE(t.date, s.start_date) <= %s")
        values.append(end_date)
    
    where_clause = " AND ".join(conditions)
    sort_clause = f"ORDER BY {sort_field} {sort_order}" if sort_field and sort_order else "ORDER BY COALESCE(t.creation, s.creation) DESC"
    
    query = f"""
    SELECT 
        COALESCE(t.name, CONCAT('DRAFT-', s.name)) as name,
        COALESCE(t.description, s.task_name) as description, 
        COALESCE(t.status, 'Draft') as status, 
        COALESCE(t.allocated_to, s.assign_to) as allocated_to, 
        s.name as reference_name,
        s.project_name as project, 
        s.project_code,
        s.site, 
        s.contact_person as contact_person, 
        s.contact_mobile as contact_phone, 
        s.contact_email,
        s.start_date, 
        s.finish_date, 
        s.job_type, 
        COALESCE(t.priority, 'Medium') as priority,
        cs.site_name, 
        COALESCE(t.date, s.start_date) as due_date,
        s.assign_to,
        s.customer_name,
        COALESCE(t.creation, s.creation) as creation,
        COUNT(*) OVER () as ttl_records
    FROM 
        `tabSMO Task` s
    LEFT JOIN 
        `tabToDo` t ON t.reference_name = s.name AND t.reference_type = 'SMO Task'
    LEFT JOIN
        `tabSMO Customer Site` cs ON s.site = cs.name
    WHERE 
        {where_clause}
    {sort_clause}
    LIMIT %s OFFSET %s
    """
    
    values.extend([page_size, offset])
    
    # Debug prints
    # frappe.errprint("Query:")
    # frappe.errprint(query)
    # frappe.errprint("Values:")
    # frappe.errprint(values)
    
    result = frappe.db.sql(query, tuple(values), as_dict=True)
    
    # frappe.errprint("Result:")
    # frappe.errprint(result)
    
    total_count = result[0].ttl_records if result else 0
    
    return {
        "data": [
            {k: v for k, v in item.items() if k != 'ttl_records'}
            for item in result
        ],
        "total": total_count,
        "page": page,
        "page_size": page_size,
        "total_pages": -(-total_count // page_size)
    }

