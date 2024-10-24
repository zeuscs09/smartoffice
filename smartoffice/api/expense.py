import frappe
from frappe import _

@frappe.whitelist()
def get_expense_entries(month, year,request_by):
    # ตรวจสอบว่า month และ year มีค่าเป็นตัวเลข
    if not month.isdigit() or not year.isdigit():
        frappe.throw(_("Month and Year must be numeric"))
    
    # แปลงค่า month และ year เป็น integer
    month = int(month)
    year = int(year)
    
    # Query ข้อมูลจากฐานข้อมูล
    expense_entries = frappe.db.sql("""
        SELECT 
            ee.name AS expense_entry_id,
            ee.owner,
            ec.customer_name,
            ep.project_name,
            ei.expense_type,
            et.description AS expense_type_desc,
            ei.from_date,
            ei.fuel_detail,
            ei.fuel_liter,
            ei.hotel_name,
            ei.paid_by,
            ei.rate_per_km,
            ei.receipt_date,
            ei.ref_code,
            ei.system_reminder,
            ei.taxi_depart_distance,
            ei.taxi_return_distance,
            ei.to_date,
            ei.total_cost,
            ei.total_day,
            ei.name AS expense_item,
            ee.service_date
        FROM
            `tabSMO Expense Entry` ee
        INNER JOIN
            `tabSMO Expense Item` ei ON ee.name = ei.parent 
            AND ei.parenttype = 'SMO Expense Entry' 
            AND ei.parentfield = 'expense_item'
        INNER JOIN
            `tabCustomer` ec ON ee.customer = ec.name
        INNER JOIN
            `tabProject` ep ON ee.project = ep.name
        LEFT JOIN
            `tabSMO Expense Type` et ON ei.expense_type = et.name
        WHERE
            ee.is_request = 0 and
            ee.workflow_state = 'approved'
            AND MONTH(ee.creation) = %(month)s
            AND YEAR(ee.creation) = %(year)s
            and ee.owner = %(request_by)s
    """, {
        "month": month,
        "year": year,
        "request_by": request_by
    }, as_dict=True)

    # Return ข้อมูลออกมาในรูปแบบ JSON
    return expense_entries

@frappe.whitelist()
def get_user_expense_entries(page, page_size):
    user = frappe.session.user
    page = int(page)
    page_size = int(page_size)
    offset = (page - 1) * page_size
    
    expense_entries = frappe.db.sql("""
        SELECT 
            ee.name, 
            ee.workflow_state, 
            ee.creation, 
            ee.service_date,
            ee.customer,
            cus.customer_name ,
            ee.total_amount,
            COUNT(*) OVER () as ttl_records
        FROM `tabSMO Expense Entry` ee
        inner join `tabCustomer` cus on ee.customer =cus.name
        WHERE ee.owner = %s
        ORDER BY ee.creation DESC
        LIMIT %s OFFSET %s
    """, (user, page_size, offset), as_dict=1)
    
    total_count = expense_entries[0].ttl_records if expense_entries else 0
    
    return {
        "data": [
            {k: v for k, v in entry.items() if k != 'ttl_records'}
            for entry in expense_entries
        ],
        "total": total_count,
        "page": page,
        "page_size": page_size,
        "total_pages": -(-total_count // page_size)  # การหารปัดขึ้น
    }

@frappe.whitelist()
def get_expense_request_by_user(page=1, page_size=10, search=None, status=None, start_date=None, end_date=None, sort_field=None, sort_order=None):
    user = frappe.session.user
    page = int(page)
    page_size = int(page_size)
    offset = (page - 1) * page_size
    
    conditions = ["(er.request_by = %s OR approver.users like %s)"]
    values = [user, f"%{user}%"]
    
    if search:
        conditions.append("(er.name LIKE %s OR er.workflow_description LIKE %s)")
        values.extend([f"%{search}%"] * 2)
    
    if status:
        conditions.append("er.workflow_state = %s")
        values.append(status)
    
    if start_date:
        conditions.append("er.creation >= %s")
        values.append(start_date)
    
    if end_date:
        conditions.append("er.creation <= %s")
        values.append(end_date)
    
    where_clause = " AND ".join(conditions)
    
    sort_clause = f"ORDER BY {sort_field} {sort_order}" if sort_field and sort_order else "ORDER BY er.creation DESC"
    
    query = f"""
    SELECT 
        er.name, er.request_by, er.year, er.month, er.period,
        er.advance_payment
        , er.general_payment, er.total,
        er.workflow_state, er.creation, er.workflow_description,
        COUNT(*) OVER () as ttl_records,
        approver.users as approvers,
        CASE WHEN er.workflow_state in ('Approved','Rejected') THEN '' ELSE er.next_action END AS next_action
    FROM 
        `tabSMO Expense Request` er inner join
        (SELECT parent, 
       GROUP_CONCAT(user_id ORDER BY idx SEPARATOR ', ') AS users
FROM `tabWorkflow Approver`
where 
parenttype ='SMO Expense Request'
        and parentfield ='approvers'
        GROUP BY parent) as approver on er.name =approver.parent
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


@frappe.whitelist()
def get_expense_entry_by_user(page=1, page_size=10, search=None, status=None, start_date=None, end_date=None, sort_field=None, sort_order=None):
    user = frappe.session.user
    page = int(page)
    page_size = int(page_size)
    offset = (page - 1) * page_size
    
    conditions = ["(ee.owner = %s OR ee.approver like %s)"]
    values = [user, f"%{user}%"]
    
    if search:
        conditions.append("(ee.name LIKE %s OR ee.customer_name LIKE %s OR ee.project_name LIKE %s)")
        values.extend([f"%{search}%"] * 3)
    
    if status:
        conditions.append("ee.workflow_state = %s")
        values.append(status)
    
    if start_date:
        conditions.append("ee.creation >= %s")
        values.append(start_date)
    
    if end_date:
        conditions.append("ee.creation <= %s")
        values.append(end_date)
    
    where_clause = " AND ".join(conditions)
    
    sort_clause = f"ORDER BY {sort_field} {sort_order}" if sort_field and sort_order else "ORDER BY ee.creation DESC"
    
    query = f"""
    SELECT 
        ee.name,
        ee.workflow_state,
        ee.creation,
        ee.customer_name,
        ee.project_name,
        ee.total_amount,
        ee.owner,
        ee.approver,
        ee.service_date,
        COUNT(*) OVER () as ttl_records
    FROM 
        `tabSMO Expense Entry` ee
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