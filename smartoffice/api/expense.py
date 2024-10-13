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
            "customer_name": frappe.db.get_value("Customer", ee.customer, "customer_name"),
            "project_name": frappe.db.get_value("Project", ee.project, "project_name"),
            "service_date": ee.service_date,
            "expense_items": [
                {
                    "expense_item": ei.name,
                    "expense_type": ei.expense_type,
                    "expense_type_desc": frappe.db.get_value("SMO Expense Type", ei.expense_type, "description"),
                    "from_date": ei.from_date,
                    "to_date": ei.to_date,
                    "total_cost": ei.total_cost,
                    "total_day": ei.total_day,
                    "fuel_detail": ei.fuel_detail,
                    "fuel_liter": ei.fuel_liter,
                    "hotel_name": ei.hotel_name,
                    "paid_by": ei.paid_by,
                    "rate_per_km": ei.rate_per_km,
                    "receipt_date": ei.receipt_date,
                    "ref_code": ei.ref_code,
                    "system_reminder": ei.system_reminder,
                    "taxi_depart_distance": ei.taxi_depart_distance,
                    "taxi_return_distance": ei.taxi_return_distance,
                }
                for ei in frappe.get_all("SMO Expense Item", 
                    filters={"parent": ee.name}, 
                    fields=["name", "expense_type", "from_date", "to_date", "total_cost", "total_day",
                            "fuel_detail", "fuel_liter", "hotel_name", "paid_by", "rate_per_km",
                            "receipt_date", "ref_code", "system_reminder", "taxi_depart_distance",
                            "taxi_return_distance"]
                )
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
            fields=["name", "owner", "customer", "project", "service_date"]
        )
    ]

    return expense_entries
