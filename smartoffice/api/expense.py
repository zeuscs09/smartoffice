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
            ei.name AS expense_item
        FROM
            `tabSMO Expense Entry` ee
        INNER JOIN
            `tabSMO Expense Item` ei ON ee.name = ei.parent 
            AND ei.parenttype = 'SMO Expense Entry' 
            AND ei.parentfield = 'expense_item'
        INNER JOIN
            `tabSMO Customer` ec ON ee.customer = ec.name
        INNER JOIN
            `tabSMO Project` ep ON ee.project = ep.name
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
