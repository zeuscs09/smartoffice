import frappe

@frappe.whitelist()
def get_taxi_rate():
    return frappe.db.get_single_value("Smart Office Setting", "taxi_rate")