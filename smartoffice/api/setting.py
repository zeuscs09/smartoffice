import frappe

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