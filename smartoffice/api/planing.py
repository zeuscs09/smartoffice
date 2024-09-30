
import frappe
from frappe import _

@frappe.whitelist()
def get_availability(month, year):
   
   # ดึงข้อมูลพนักงาน
    employees = frappe.db.sql("""
        select user_id as name, employee_name,department as team from `tabEmployee` where designation = 'Engineer'
    """, as_dict=True)
    
    # ดึงวันหยุดตามปี
    holidays = frappe.db.sql("""
        SELECT h.holiday_date 
        FROM `tabHoliday` h
        INNER JOIN `tabHoliday List` hl ON h.parent = hl.name
        WHERE year(h.holiday_date) = %s and month(h.holiday_date) = %s
    """, (year,month), as_dict=True)
    
    # Query ข้อมูลจากฐานข้อมูล
    query = """
            SELECT
                team.user,
                team.full_name AS engineer,
                task.start_date AS date
            FROM
                `tabSMO Working Team` team
            INNER JOIN
                `tabSMO Task` task
            ON
                team.parent = task.name
                AND team.parentfield = 'team'
                AND team.parenttype = 'SMO Task'
            WHERE
                task.status NOT IN ('Cancel')
                AND MONTH(task.start_date) = %s
                AND YEAR(task.start_date) = %s
        """

        # เรียกใช้ frappe.db.sql เพื่อดึงข้อมูล
    tasks = frappe.db.sql(query, (month, year), as_dict=True)

    # Return ข้อมูลออกมาในรูปแบบ JSON
    return {
        "status": "success",
        "data": {
            "employees": employees,
            "holidays": holidays,
            "tasks": tasks
        }
    }
