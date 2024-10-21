import frappe
from frappe import _
import calendar
from datetime import datetime

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

@frappe.whitelist()
def get_team_workload(month, year):
    # แปลง month และ year เป็นตัวเลข
    month = int(month)
    year = int(year)
    querySring=""
    # ดึงข้อมูล employee ที่เป็นลูกน้องของคนที่ login
    def get_subordinates(employee):
        subordinates = []
        direct_reports = frappe.get_all("Employee", filters={"reports_to": employee}, fields=["name"])
        for report in direct_reports:
            subordinates.append(report.name)
            subordinates.extend(get_subordinates(report.name))
        return subordinates

    user = frappe.session.user
    employee = frappe.get_value("Employee", {"user_id": user}, "name")
    
    if employee:
        subordinates = get_subordinates(employee)
        subordinates.append(employee)  # รวมตัวเองด้วย
        
        employees = frappe.get_all("Employee", 
                                   filters={"name": ["in", subordinates]},
                                   fields=["name", "employee_name", "department as team","user_id"])

        # ตรวจสอบว่ามีพนักงานหรือไม่
        if employees:
            # ตรวจสอบและดึงข้อมูล user_id อีกครั้ง
            employee_names = [e.name for e in employees]
            employee_user_ids = frappe.get_all("Employee", 
                                               filters={"name": ["in", employee_names]},
                                               fields=["name", "user_id"])
            
            # สร้าง dictionary ของ name และ user_id
            employee_dict = {e.name: e.user_id for e in employee_user_ids if e.user_id}
            
            # ตรวจสอบว่ามี user_id หรือไม่
            if not employee_dict:
                frappe.throw(_("ไม่พบ user_id สำหรับพนักงานที่เลือก"))
            
            query = """
                SELECT 
                    t.date,
                    t.allocated_to,
                    count(*) count_jov
                FROM 
                    `tabToDo` t
                INNER JOIN 
                    `tabSMO Task` s ON t.reference_name = s.name
                WHERE 
                    t.allocated_to IN %(employee_user_ids)s
                    AND MONTH(t.date) = %(month)s
                    AND YEAR(t.date) = %(year)s
                group by 
                    t.date,
                    t.allocated_to
            """

            params = {
                "employee_user_ids": tuple(employee_dict.values()),
                "month": month,
                "year": year
            }


            # ดำเนินการ query จริง
            tasks = frappe.db.sql(query, params, as_dict=True)
            
        else:
            tasks = []
    else:
        employees = []
        tasks = []

    holidays = frappe.db.sql("""
        SELECT h.holiday_date 
        FROM `tabHoliday` h
        INNER JOIN `tabHoliday List` hl ON h.parent = hl.name
        WHERE year(h.holiday_date) = %s and month(h.holiday_date) = %s
    """, (year,month), as_dict=True)
    
    # หาจำนวนวันในเดือนที่ระบุ
    _, days_in_month = calendar.monthrange(year, month)

    # แปลงข้อมูลให้อยู่ในรูปแบบที่ต้องการ
    result = []
    for idx, employee in enumerate(employees, start=1):
        employee_tasks = [task for task in tasks if task.allocated_to == employee.user_id]
        
        # สร้าง dictionary สถานะสำหรับแต่ละวันในเดือน
        status = {}
        for day in range(1, days_in_month + 1):
            date = datetime(year, month, day).date()
            is_holiday = any(holiday.holiday_date == date for holiday in holidays)
            has_task = any(task.date == date for task in employee_tasks)
            
            if is_holiday and has_task:
                status[str(day)] = "work_on_holiday"
            elif is_holiday:
                status[str(day)] = "holiday"
            elif has_task:
                status[str(day)] = "unavailable"
            else:
                status[str(day)] = "available"
        
        employee_data = {
            "id": idx,
            "name": employee.employee_name,
            "user_id": employee.user_id,
            "status": status
        }
        result.append(employee_data)

    return result
