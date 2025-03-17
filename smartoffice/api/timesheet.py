import frappe
from frappe import _
from frappe.utils import nowdate, getdate, get_datetime, get_time, get_first_day, get_last_day, add_days, add_months, date_diff

@frappe.whitelist()
def get_timesheets(page=1, page_size=10, filters=None):
    """
    Get a list of timesheets with pagination
    """
    try:
        page = int(page)
        page_size = int(page_size)
        start = (page - 1) * page_size
        
        conditions = []
        values = {}
        
        if filters:
            if isinstance(filters, str):
                filters = frappe.parse_json(filters)
                
            if filters.get("year"):
                conditions.append("year = %(year)s")
                values["year"] = filters.get("year")
                
            if filters.get("month"):
                conditions.append("month_value = %(month)s")
                values["month"] = filters.get("month")
                
            if filters.get("status") != "":
                conditions.append("docstatus = %(status)s")
                values["status"] = int(filters.get("status"))
        
        # Add condition to only show timesheets for the current user
        employee = frappe.db.get_value("Employee", {"user_id": frappe.session.user}, "name")
        if employee and not frappe.has_permission("SMO Timesheet", "read", user=frappe.session.user):
            conditions.append("employee = %(employee)s")
            values["employee"] = employee
        
        where_clause = " AND ".join(conditions) if conditions else ""
        if where_clause:
            where_clause = f"WHERE {where_clause}"
        
        # Get total count
        count_query = f"""
            SELECT COUNT(*) as total
            FROM `tabSMO Timesheet`
            {where_clause}
        """
        total = frappe.db.sql(count_query, values=values, as_dict=True)[0].get("total")
        
        # Get paginated data
        query = f"""
            SELECT name, employee, year, month, month_value, creation, modified, docstatus,
                   CASE 
                       WHEN docstatus = 0 THEN 'Draft'
                       WHEN docstatus = 1 THEN 'Submitted'
                       WHEN docstatus = 2 THEN 'Cancelled'
                   END as status
            FROM `tabSMO Timesheet`
            {where_clause}
            ORDER BY creation DESC
            LIMIT {start}, {page_size}
        """
        
        data = frappe.db.sql(query, values=values, as_dict=True)
        
        return {
            "data": data,
            "total": total,
            "page": page,
            "page_size": page_size,
            "total_pages": (total + page_size - 1) // page_size
        }
    except Exception as e:
        frappe.log_error(frappe.get_traceback(), _("Error in get_timesheets"))
        return {
            "data": [],
            "total": 0,
            "page": page,
            "page_size": page_size,
            "total_pages": 0
        }

@frappe.whitelist()
def get_timesheet(name):
    """
    Get a single timesheet by name
    """
    try:
        if not name:
            frappe.throw(_("Timesheet name is required"))
        
        timesheet = frappe.get_doc("SMO Timesheet", name)
        
        # Check if user has permission to view this timesheet
        if not frappe.has_permission("SMO Timesheet", "read", doc=timesheet):
            employee = frappe.db.get_value("Employee", {"user_id": frappe.session.user}, "name")
            if timesheet.employee != employee:
                frappe.throw(_("You don't have permission to access this timesheet"))
        
        # Get timesheet items
        timesheet_items = frappe.get_all(
            "SMO Timesheet Item",
            filters={"parent": name},
            fields=["from_time", "to_time", "working_hours", "link_from_doc", "doc_number", "project_code", "customer", "customer_name"],
            order_by="from_time"
        )
        
        timesheet_data = timesheet.as_dict()
        timesheet_data["time_sheets"] = timesheet_items
        
        return timesheet_data
    except Exception as e:
        frappe.log_error(frappe.get_traceback(), _("Error in get_timesheet"))
        frappe.throw(str(e))

@frappe.whitelist()
def save_timesheet(timesheet):
    """
    Save a timesheet
    """
    try:
        if isinstance(timesheet, str):
            timesheet = frappe.parse_json(timesheet)
        
        if timesheet.get("name") and not timesheet.get("name").startswith("new-"):
            # Update existing timesheet
            doc = frappe.get_doc("SMO Timesheet", timesheet.get("name"))
            
            # Check if user has permission to edit this timesheet
            if not frappe.has_permission("SMO Timesheet", "write", doc=doc):
                employee = frappe.db.get_value("Employee", {"user_id": frappe.session.user}, "name")
                if doc.employee != employee:
                    frappe.throw(_("You don't have permission to edit this timesheet"))
            
            # Only allow editing if timesheet is in draft state
            if doc.docstatus != 0:
                frappe.throw(_("Cannot edit submitted or cancelled timesheet"))
            
            # Update fields
            doc.employee = timesheet.get("employee")
            doc.year = timesheet.get("year")
            doc.month = timesheet.get("month")
            doc.month_value = timesheet.get("month_value")
            
            # Save the document
            doc.save()
            return doc.as_dict()
        else:
            # Create new timesheet
            doc = frappe.new_doc("SMO Timesheet")
            doc.employee = timesheet.get("employee")
            doc.year = timesheet.get("year")
            doc.month = timesheet.get("month")
            doc.month_value = timesheet.get("month_value")
            
            # Save the document
            doc.insert()
            return doc.as_dict()
    except Exception as e:
        frappe.log_error(frappe.get_traceback(), _("Error in save_timesheet"))
        frappe.throw(str(e))

@frappe.whitelist()
def submit_timesheet(name):
    """
    Submit a timesheet
    """
    try:
        if not name:
            frappe.throw(_("Timesheet name is required"))
        
        doc = frappe.get_doc("SMO Timesheet", name)
        
        # Check if user has permission to submit this timesheet
        if not frappe.has_permission("SMO Timesheet", "submit", doc=doc):
            employee = frappe.db.get_value("Employee", {"user_id": frappe.session.user}, "name")
            if doc.employee != employee:
                frappe.throw(_("You don't have permission to submit this timesheet"))
        
        # Only allow submitting if timesheet is in draft state
        if doc.docstatus != 0:
            frappe.throw(_("Cannot submit a timesheet that is not in draft state"))
        
        # Submit the document
        doc.submit()
        return {"success": True}
    except Exception as e:
        frappe.log_error(frappe.get_traceback(), _("Error in submit_timesheet"))
        frappe.throw(str(e))

@frappe.whitelist()
def cancel_timesheet(name):
    """
    Cancel a timesheet
    """
    try:
        if not name:
            frappe.throw(_("Timesheet name is required"))
        
        doc = frappe.get_doc("SMO Timesheet", name)
        
        # Check if user has permission to cancel this timesheet
        if not frappe.has_permission("SMO Timesheet", "cancel", doc=doc):
            employee = frappe.db.get_value("Employee", {"user_id": frappe.session.user}, "name")
            if doc.employee != employee:
                frappe.throw(_("You don't have permission to cancel this timesheet"))
        
        # Only allow cancelling if timesheet is in submitted state
        if doc.docstatus != 1:
            frappe.throw(_("Cannot cancel a timesheet that is not submitted"))
        
        # Cancel the document
        doc.cancel()
        return {"success": True}
    except Exception as e:
        frappe.log_error(frappe.get_traceback(), _("Error in cancel_timesheet"))
        frappe.throw(str(e))

@frappe.whitelist()
def get_timesheet_data(employee, year, month):
    """
    Get timesheet data for a specific employee, year, and month
    """
    try:
        if not employee:
            frappe.throw(_("Employee is required"))
        
        if not year:
            frappe.throw(_("Year is required"))
        
        if not month:
            frappe.throw(_("Month is required"))
        
        # Check if user has permission to view this employee's data
        if not frappe.has_permission("Employee", "read"):
            user_employee = frappe.db.get_value("Employee", {"user_id": frappe.session.user}, "name")
            if employee != user_employee:
                frappe.throw(_("You don't have permission to access this employee's data"))
        
        # Get the first and last day of the month
        first_day = f"{year}-{month}-01"
        last_day = get_last_day(first_day)
        
        # Get all service reports and tasks for this employee in the specified month
        time_sheets = []
        
        # Get service reports
        service_reports = frappe.get_all(
            "SMO Service Report",
            filters={
                "employee": employee,
                "docstatus": 1,
                "date": ["between", [first_day, last_day]]
            },
            fields=["name", "date", "start_time", "end_time", "working_hour", "project_code", "customer", "customer_name"]
        )
        
        for sr in service_reports:
            from_time = get_datetime(f"{sr.date} {sr.start_time}")
            to_time = get_datetime(f"{sr.date} {sr.end_time}")
            
            time_sheets.append({
                "from_time": from_time,
                "to_time": to_time,
                "working_hours": sr.working_hour,
                "link_from_doc": "SMO Service Report",
                "doc_number": sr.name,
                "project_code": sr.project_code,
                "customer": sr.customer,
                "customer_name": sr.customer_name
            })
        
        # Get tasks
        tasks = frappe.get_all(
            "SMO Task",
            filters={
                "assigned_to": employee,
                "docstatus": 1,
                "start_date": ["<=", last_day],
                "end_date": [">=", first_day]
            },
            fields=["name", "start_date", "end_date", "working_hours", "project_code", "customer", "customer_name"]
        )
        
        for task in tasks:
            # Only include task time within the month
            start_date = max(getdate(task.start_date), getdate(first_day))
            end_date = min(getdate(task.end_date), getdate(last_day))
            
            # Calculate working hours for the period within the month
            total_days = date_diff(task.end_date, task.start_date) + 1
            days_in_month = date_diff(end_date, start_date) + 1
            hours_in_month = (task.working_hours / total_days) * days_in_month if total_days > 0 else 0
            
            from_time = get_datetime(f"{start_date} 09:00:00")
            to_time = get_datetime(f"{end_date} 17:00:00")
            
            time_sheets.append({
                "from_time": from_time,
                "to_time": to_time,
                "working_hours": hours_in_month,
                "link_from_doc": "SMO Task",
                "doc_number": task.name,
                "project_code": task.project_code,
                "customer": task.customer,
                "customer_name": task.customer_name
            })
        
        # Sort by from_time
        time_sheets.sort(key=lambda x: x["from_time"])
        
        return {
            "time_sheets": time_sheets
        }
    except Exception as e:
        frappe.log_error(frappe.get_traceback(), _("Error in get_timesheet_data"))
        frappe.throw(str(e)) 