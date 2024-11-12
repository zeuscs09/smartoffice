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
        # ดึง reports_to ของ user ที่ login เข้ามา
        reports_to = frappe.get_value("Employee", employee, "reports_to")
        
        # ดึงลูกน้องทั้งหมดของ user ที่ login
        subordinates = get_subordinates(employee)
        
        if reports_to:
            # ดึงรายชื่อพนักงานที่มี reports_to เดียวกัน (เพื่อนร่วมทีม)
            team_members = frappe.get_all("Employee",
                filters={"reports_to": reports_to},
                fields=["name", "employee_name", "department as team", "user_id"])
            
            # ดึงรายชื่อลูกน้องทั้งหมด
            subordinate_members = frappe.get_all("Employee",
                filters={"name": ["in", subordinates]},
                fields=["name", "employee_name", "department as team", "user_id"])
            
            # รวมรายชื่อทั้งหมด (เพื่อนร่วมทีม + ลูกน้อง + ตัวเอง)
            all_members = team_members + subordinate_members
            # ลบรายชื่อที่ซ้ำกัน โดยใช้ name เป็น key
            unique_members = {member.name: member for member in all_members}.values()
            employees = list(unique_members)
        else:
            # กรณีไม่มี reports_to (อาจเป็นหัวหน้าสูงสุด)
            subordinates.append(employee)  # รวมตัวเองด้วย
            
            employees = frappe.get_all("Employee",
                filters={"name": ["in", subordinates]},
                fields=["name", "employee_name", "department as team", "user_id"])

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
                    count(*) count_job,
                    GROUP_CONCAT(
                        CONCAT(
                            COALESCE(s.project_code, ''),
                            ' - ',
                            COALESCE(s.project_name, ''),
                            ' (',
                            COALESCE(s.customer_name, ''),
                            ')',
                            IF(s.task_name IS NOT NULL, CONCAT(' | ', s.task_name), ''),
                            IF(s.location IS NOT NULL, CONCAT(' @ ', s.location), ''),
                            IF(s.start_time IS NOT NULL AND s.to_time IS NOT NULL,
                                CONCAT(' (', TIME_FORMAT(s.start_time, '%%H:%%i'), ' - ', TIME_FORMAT(s.to_time, '%%H:%%i'), ')'),
                                ''
                            )
                        ) SEPARATOR '{|}'
                    ) as task_details
                FROM 
                    `tabToDo` t
                INNER JOIN 
                    `tabSMO Task` s ON t.reference_name = s.name
                LEFT JOIN
                    `tabProject` p ON s.project = p.name
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
            
            # หา task สำหรับวันนี้และนับจำนวน job
            day_tasks = [task for task in employee_tasks if task.date == date]
            count_job = day_tasks[0].count_job if day_tasks else 0
            has_task = bool(day_tasks)
            
            if is_holiday and has_task:
                status[str(day)] = {
                    "status": "work_on_holiday",
                    "count_job": count_job,
                    "task_details": day_tasks[0].task_details if day_tasks else ""
                }
            elif is_holiday:
                status[str(day)] = {
                    "status": "holiday",
                    "count_job": 0,
                    "task_details": ""
                }
            elif has_task:
                status[str(day)] = {
                    "status": "unavailable",
                    "count_job": count_job,
                    "task_details": day_tasks[0].task_details if day_tasks else ""
                }
            else:
                status[str(day)] = {
                    "status": "available",
                    "count_job": 0,
                    "task_details": ""
                }

        employee_data = {
            "id": idx,
            "name": employee.employee_name,
            "user_id": employee.user_id,
            "status": status
        }
        result.append(employee_data)

    return result
