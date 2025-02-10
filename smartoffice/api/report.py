# smartoffice/api/report.py

import frappe
from frappe import _
from datetime import datetime
# smartoffice/api/report.py

@frappe.whitelist()
def get_manhour_report(month=None, ungroup_task_type=0, ungroup_engineer=0, job_types=None, departments=None, grades=None):
    if not month:
        return {"error": "กรุณาระบุเดือนที่ต้องการดูรายงาน"}
    
    try:
        # แปลง parameters
        job_types = frappe.parse_json(job_types) if job_types else []
        departments = frappe.parse_json(departments) if departments else []
        grades = frappe.parse_json(grades) if grades else []

        # Base query with conditional GROUP BY
        query = """
            SELECT 
                sr.project_code,
                sr.customer_name,
                sr.project_name,
                {task_type_select},
                {engineer_select},
                COUNT(DISTINCT sr.name) as task_count,
                COALESCE(SUM(sr.duration), 0) as total_seconds,
                SEC_TO_TIME(COALESCE(SUM(sr.duration), 0)) as hours
            FROM 
                `tabSMO Service Report` sr
            INNER JOIN 
                `tabSMO Working Team` wt ON wt.parent = sr.name
            INNER JOIN
                `tabEmployee` emp ON emp.name = wt.employee
            WHERE 
                sr.workflow_state = 'Customer Approved'
                AND DATE_FORMAT(sr.start_date_input, '%%Y-%%m') = %s
                {job_types_filter}
                {departments_filter}
                {grades_filter}
            GROUP BY 
                {group_by}
            ORDER BY 
                total_seconds DESC
        """

        # สร้าง filters
        filters = [month]
        job_types_filter = ""
        if job_types:
            job_types_filter = "AND sr.job_type IN %s"
            filters.append(tuple(job_types))

        departments_filter = ""
        if departments:
            departments_filter = "AND emp.department IN %s"
            filters.append(tuple(departments))

        grades_filter = ""
        if grades:
            grades_filter = "AND emp.grade IN %s"
            filters.append(tuple(grades))

        # ปรับ query ตามการ group
        if int(ungroup_task_type) and int(ungroup_engineer):
            task_type_select = "sr.job_type as task_type"
            engineer_select = "wt.full_name as engineer"
            group_by = "sr.project_code, sr.job_type, wt.full_name"
        elif int(ungroup_task_type):
            task_type_select = "sr.job_type as task_type"
            engineer_select = "GROUP_CONCAT(DISTINCT wt.full_name) as engineer"
            group_by = "sr.project_code, sr.job_type"
        elif int(ungroup_engineer):
            task_type_select = "GROUP_CONCAT(DISTINCT sr.job_type) as task_type"
            engineer_select = "wt.full_name as engineer"
            group_by = "sr.project_code, wt.full_name"
        else:
            task_type_select = "GROUP_CONCAT(DISTINCT sr.job_type) as task_type"
            engineer_select = "GROUP_CONCAT(DISTINCT wt.full_name) as engineer"
            group_by = "sr.project_code"

        # Format query
        formatted_query = query.format(
            task_type_select=task_type_select,
            engineer_select=engineer_select,
            group_by=group_by,
            job_types_filter=job_types_filter,
            departments_filter=departments_filter,
            grades_filter=grades_filter
        )

        # Execute query
        result = frappe.db.sql(formatted_query, tuple(filters), as_dict=1)

        # คำนวณ total สำหรับ percentage
        total_seconds = sum(r.total_seconds for r in result)
        total_tasks = sum(r.task_count for r in result)

        # แปลงข้อมูลให้ตรงกับ format ที่ต้องการ
        formatted_result = []
        for r in result:
            minutes = int(r.total_seconds or 0) // 60
            formatted_result.append({
                "project_code": r.project_code or "",
                "customer_name": r.customer_name or "",
                "project_name": r.project_name or "",
                "task_type": r.task_type or "",
                "engineer": r.engineer or "",
                "task_count": r.task_count or 0,
                "hours": str(r.hours or "00:00:00"),
                "minutes": minutes,
                "percent_hour": round((r.total_seconds / total_seconds * 100) if total_seconds and r.total_seconds else 0, 2),
                "percent_task": round((r.task_count / total_tasks * 100) if total_tasks and r.task_count else 0, 2)
            })

        return {
            "status": "success",
            "data": formatted_result
        }

    except Exception as e:
        frappe.log_error("Manhour Report Error", str(e))
        return {
            "status": "error",
            "message": f"เกิดข้อผิดพลาด: {str(e)[:100]}"
        }

@frappe.whitelist()
def get_manhour_report_by_task(month=None, ungroup_task_type=0, ungroup_engineer=0, job_types=None, departments=None, grades=None):
    if not month:
        return {"error": "กรุณาระบุเดือนที่ต้องการดูรายงาน"}
    
    try:
        # แปลง parameters
        job_types = frappe.parse_json(job_types) if job_types else []
        departments = frappe.parse_json(departments) if departments else []
        grades = frappe.parse_json(grades) if grades else []

        # Base query with conditional GROUP BY
        query = """
            SELECT 
                sr.project_code,
                sr.customer_name,
                sr.project_name,
                {task_type_select},
                {engineer_select},
                COUNT(DISTINCT sr.name) as task_count,
                COALESCE(SUM(sr.expected_time_use), 0) as total_seconds,
                SEC_TO_TIME(COALESCE(SUM(sr.expected_time_use), 0)) as hours
            FROM 
                `tabSMO Task` sr
            INNER JOIN 
                `tabSMO Working Team` wt ON wt.parent = sr.name
            INNER JOIN
                `tabEmployee` emp ON emp.name = wt.employee
            WHERE 
                sr.docstatus = 1
                AND DATE_FORMAT(sr.start_date, '%%Y-%%m') = %s
                {job_types_filter}
                {departments_filter}
                {grades_filter}
            GROUP BY 
                {group_by}
            ORDER BY 
                total_seconds DESC
        """

        # สร้าง filters
        filters = [month]
        job_types_filter = ""
        if job_types:
            job_types_filter = "AND sr.job_type IN %s"
            filters.append(tuple(job_types))

        departments_filter = ""
        if departments:
            departments_filter = "AND emp.department IN %s"
            filters.append(tuple(departments))

        grades_filter = ""
        if grades:
            grades_filter = "AND emp.grade IN %s"
            filters.append(tuple(grades))

        # ปรับ query ตามการ group
        if int(ungroup_task_type) and int(ungroup_engineer):
            task_type_select = "sr.job_type as task_type"
            engineer_select = "wt.full_name as engineer"
            group_by = "sr.project_code, sr.job_type, wt.full_name"
        elif int(ungroup_task_type):
            task_type_select = "sr.job_type as task_type"
            engineer_select = "GROUP_CONCAT(DISTINCT wt.full_name) as engineer"
            group_by = "sr.project_code, sr.job_type"
        elif int(ungroup_engineer):
            task_type_select = "GROUP_CONCAT(DISTINCT sr.job_type) as task_type"
            engineer_select = "wt.full_name as engineer"
            group_by = "sr.project_code, wt.full_name"
        else:
            task_type_select = "GROUP_CONCAT(DISTINCT sr.job_type) as task_type"
            engineer_select = "GROUP_CONCAT(DISTINCT wt.full_name) as engineer"
            group_by = "sr.project_code"

        # Format query
        formatted_query = query.format(
            task_type_select=task_type_select,
            engineer_select=engineer_select,
            group_by=group_by,
            job_types_filter=job_types_filter,
            departments_filter=departments_filter,
            grades_filter=grades_filter
        )

        # Execute query
        result = frappe.db.sql(formatted_query, tuple(filters), as_dict=1)

        # คำนวณ total สำหรับ percentage
        total_seconds = sum(r.total_seconds for r in result)
        total_tasks = sum(r.task_count for r in result)

        # แปลงข้อมูลให้ตรงกับ format ที่ต้องการ
        formatted_result = []
        for r in result:
            minutes = int(r.total_seconds or 0) // 60
            formatted_result.append({
                "project_code": r.project_code or "",
                "customer_name": r.customer_name or "",
                "project_name": r.project_name or "",
                "task_type": r.task_type or "",
                "engineer": r.engineer or "",
                "task_count": r.task_count or 0,
                "hours": str(r.hours or "00:00:00"),
                "minutes": minutes,
                "percent_hour": round((r.total_seconds / total_seconds * 100) if total_seconds and r.total_seconds else 0, 2),
                "percent_task": round((r.task_count / total_tasks * 100) if total_tasks and r.task_count else 0, 2)
            })

        return {
            "status": "success",
            "data": formatted_result
        }

    except Exception as e:
        frappe.log_error("Manhour Report Error", str(e))
        return {
            "status": "error",
            "message": f"เกิดข้อผิดพลาด: {str(e)[:100]}"
        }


@frappe.whitelist()
def get_expense_report(year=None, month=None):
    if not year or not month:
        return {"error": "Please specify year and month"}
    
    try:
        query = """
        WITH ExpenseSummary AS (
            SELECT
                'TPS' AS QCCORP,
                '00000' AS QCBRANCH,
                '' AS QCACCBOOK,
                '' AS `DATE`,
                '' AS CODE,
                CONCAT(
                    'Exp-Engineer บันทึกคชจ. พร้อมตั้งเบิกเงิน  ',
                    IFNULL(er.period_display, '')
                ) AS REMARKH1,
                '' AS REMARKH2,
                '' AS REMARKH3,
                '' AS REMARKH4,
                '' AS REMARKH5,
                ed.account_code AS QCACCHART,
                SUM(ed.AMT) AS AMT,
                us.full_name AS DETAIL,
                ed.project_code AS QCSECTI,
                er.`year`,
                er.`month`,
                er.period
            FROM
                `tabSMO Expense Request` er
            INNER JOIN `tabUser` us ON er.request_by = us.name
            INNER JOIN (
                SELECT
                    ri.parent AS expense_request_name,
                    et.account_code,
                    SUM(ei.total_cost) AS AMT,
                    ee.project_code,
                    ee.name
                FROM
                    `tabSMO Expense Request Item` ri
                INNER JOIN `tabSMO Expense Item` ei ON ri.expense_item = ei.name
                INNER JOIN `tabSMO Expense Type` et ON ei.expense_type = et.name
                INNER JOIN `tabSMO Expense Entry` ee ON ei.parent = ee.name
                GROUP BY
                    ri.parent, et.account_code, ee.project_code, ee.name
            ) ed ON er.name = ed.expense_request_name
            WHERE
                er.workflow_state = 'Approved'
                and er.year = %s
                and er.month = %s
            GROUP BY
                er.request_by, us.full_name, er.year, er.month, er.period, 
                ed.account_code, ed.project_code, er.period_display
        ),
        AdvanceSummary AS (
            SELECT
                'TPS' AS QCCORP,
                '00000' AS QCBRANCH,
                '' AS QCACCBOOK,
                '' AS `DATE`,
                '' AS CODE,
                CONCAT(
                    'เคลียร์เงิน Advance ',
                    reference_code_finance,
                    ' Project ',
                    project_code
                ) AS REMARKH1,
                ae.reference_code_accounting AS REMARKH2,
                '' AS REMARKH3,
                '' AS REMARKH4,
                '' AS REMARKH5,
                '115101' AS QCACCHART,
                SUM(total_amount) AS AMT,
                reference_code AS DETAIL,
                project_code AS QCSECTI,
                YEAR(service_date) AS `year`,
                MONTHNAME(service_date) AS `month`,
                '' AS period
            FROM
                `tabSMO Advance Entry` ae
            INNER JOIN `tabUser` us ON ae.owner = us.name
            WHERE
                ae.workflow_state = 'Approved'
                and YEAR(ae.service_date) = %s
                and MONTHNAME(service_date) = %s
            GROUP BY
                reference_code, project_code, YEAR(service_date), MONTHNAME(service_date)
        )

        SELECT * FROM ExpenseSummary
        UNION ALL
        SELECT * FROM AdvanceSummary
        """

        # Debug: Print parameters
        frappe.log_error(title="Parameters", message=f"year={year}, month={month}")

        # Execute query
        result = frappe.db.sql(query, (year, month, year, month), as_dict=1)

        # Debug: Print result
        frappe.log_error(title="Query Results", message=str(result))

        # Debug: Print raw query with parameters
        formatted_query = query % (year, month, year, month)
        frappe.log_error(title="Formatted Query", message=formatted_query)

        return {
            "status": "success",
            "data": result
        }

    except Exception as e:
        frappe.log_error("Expense Report Error", str(e)[:100])
        return {
            "status": "error",
            "message": f"Error: {str(e)[:100]}"
        }