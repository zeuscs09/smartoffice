import frappe
from frappe import _

@frappe.whitelist()
def get_advance_entry_by_user(page=1, page_size=10, search=None, status=None, start_date=None, end_date=None, sort_field=None, sort_order=None):
    user = frappe.session.user
    page = int(page)
    page_size = int(page_size)
    offset = (page - 1) * page_size
    
    conditions = ["(ae.owner = %s OR approver.users like %s)"]
    values = [user, f"%{user}%"]
    
    if search:
        conditions.append("(ae.name LIKE %s OR ae.customer LIKE %s OR ae.project LIKE %s OR ae.reference_code LIKE %s)")
        values.extend([f"%{search}%"] * 4)
    
    if status:
        conditions.append("ae.workflow_state = %s")
        values.append(status)
    
    if start_date:
        conditions.append("ae.service_date >= %s")
        values.append(start_date)
    
    if end_date:
        conditions.append("ae.service_date <= %s")
        values.append(end_date)
    
    where_clause = " AND ".join(conditions)
    
    sort_clause = f"ORDER BY {sort_field} {sort_order}" if sort_field and sort_order else "ORDER BY ae.modified DESC"
    
    query = f"""
    SELECT 
        ae.name,
        ae.docstatus,
        ae.modified,
        ae.customer,
        ae.customer_name,
        ae.project_name,
        ae.total_amount,
        ae.owner,
        ae.service_date,
        ae.to,
        ae.reference_code,
        ae.approver,
        ae.total_amount,
        ae.creation,
        ae.workflow_state,
        approver.users as approvers,
        CASE WHEN ae.workflow_state in ('Approved','Rejected') THEN '' ELSE ae.next_action END AS next_action,
        COUNT(*) OVER () as ttl_records
    FROM 
        `tabSMO Advance Entry` ae inner join
        (
            SELECT parent, 
                GROUP_CONCAT(user_id ORDER BY idx SEPARATOR ', ') AS users
            FROM `tabWorkflow Approver`
            where 
            parenttype ='SMO Advance Entry'
                    and parentfield ='approvers'
                    GROUP BY parent
        ) as approver on ae.name =approver.parent
    WHERE 
        {where_clause}
    {sort_clause}
    LIMIT %s OFFSET %s
    """
    
    values.extend([page_size, offset])
    
    # print("=== DEBUG SQL QUERY ===")
    # final_query = frappe.db.mogrify(query, tuple(values))
    # frappe.errprint(f"Final Query: {final_query}")
    # print("=====================")
    
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
