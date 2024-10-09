import frappe
from frappe import _

@frappe.whitelist()
def get_expense_entries(month, year, request_by):
    # ตรวจสอบและแปลงค่า month และ year เป็น integer
    try:
        month = int(month)
        year = int(year)
    except ValueError:
        frappe.throw(_("Month and Year must be numeric"))
    
    # ใช้ list comprehension แทน SQL query
    expense_entries = [
        {
            "expense_entry_id": ee.name,
            "owner": ee.owner,
            "customer_name": ee.customer,
            "project_name": ee.project,
            "service_date": ee.service_date,
            "expense_items": [
                {
                    "expense_type": ei.expense_type,
                    "expense_type_desc": frappe.db.get_value("SMO Expense Type", ei.expense_type, "description"),
                    "from_date": ei.from_date,
                    "to_date": ei.to_date,
                    "total_cost": ei.total_cost,
                    "total_day": ei.total_day,
                    # เพิ่มฟิลด์อื่นๆ ตามต้องการ
                }
                for ei in ee.expense_item
            ]
        }
        for ee in frappe.get_all(
            "SMO Expense Entry",
            filters={
                "is_request": 0,
                "workflow_state": "approved",
                "owner": request_by,
                "creation": ["between", [f"{year}-{month:02d}-01", f"{year}-{month:02d}-31"]]
            },
            fields=["name", "owner", "customer", "project", "service_date"],
            as_dict=True
        )
    ]

    return expense_entries
