import frappe
from smartoffice.utils.sync_data import sync_vtiger_projects, sync_vtiger_customers
@frappe.whitelist()
def get_taxi_rate():
    return frappe.db.get_single_value("Smart Office Setting", "taxi_rate")

@frappe.whitelist()
def get_taxi():
    taxi_start= frappe.db.get_single_value("Smart Office Setting", "start_taxi")
    taxi_rate = get_taxi_rate()
    result={
        "taxi_start":taxi_start,
        "taxi_rate":taxi_rate,
        "over_night_rate":frappe.db.get_single_value("Smart Office Setting", "over_night_rate")
    }
    return result


@frappe.whitelist()
def sync_project_from_vtiger():
    frappe.enqueue(
        'smartoffice.utils.sync_data.sync_vtiger_projects',
        queue='long',
        timeout=3000,
        is_async=True
    )
    return "Sync process started in background"

@frappe.whitelist()
def sync_customer_from_vtiger():
    frappe.enqueue(
        'smartoffice.utils.sync_data.sync_vtiger_customers',
        queue='long',
        timeout=3000,
        is_async=True
    )
    return "Sync process started in background"

@frappe.whitelist()
def sync_opportunity_from_vtiger():
    """
    Sync opportunities from Vtiger to ERPNext
    """
    frappe.enqueue(
        'smartoffice.utils.sync_data.sync_vtiger_opportunity',
        queue='long',
        timeout=3000
    )
    return True