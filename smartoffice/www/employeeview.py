import frappe
from frappe import _
from datetime import datetime, timedelta, date

def get_context(context):
    user = frappe.session.user
    context.is_employee = False
    context.employee = None
    context.company_name = frappe.db.get_single_value('System Settings', 'app_name') or 'Frappe'

    employee = frappe.get_doc("Employee", {"user_id": user})
    if employee:
        context.is_employee = True
        context.employee = employee

    context.logo_url = get_app_logo()
    context.tasks = get_employee_tasks(user)
    context.shortcuts = [
        {"name": _("Task"), "route": "/smo-task/new", "icon": "fa-tasks"},
        {"name": _("Service Report"), "route": "/smo-service-report/new", "icon": "fa-file-alt"},
        {"name": _("Expense Entry"), "route": "/smp-expense-entry/new", "icon": "fa-receipt"},
        {"name": _("Advance Entry"), "route": "/smo-advance-entry/new", "icon": "fa-money-bill-wave"},
        {"name": _("Expense Request"), "route": "/smo-expense-request/new", "icon": "fa-file-invoice-dollar"},
    ]
    context.pending_documents = get_pending_documents(user)
    context.recent_documents = get_recent_documents(user)
    context.upcoming_events = get_upcoming_events(user)

    # ปรับปรุงการดึงข้อมูลสรุปงาน
    ytd_tasks = get_ytd_tasks()
    mtd_tasks = get_mtd_tasks()

    context.ytd_task_count = len(ytd_tasks)
    context.mtd_task_count = len(mtd_tasks)

    context.ytd_tasks = {
        'total': len(ytd_tasks),
        'completed': sum(1 for task in ytd_tasks if task['status'] == 'Completed'),
        'cancelled': sum(1 for task in ytd_tasks if task['status'] == 'Cancelled'),
        'pending': sum(1 for task in ytd_tasks if task['status'] == 'Open')
    }

    context.mtd_tasks = {
        'total': len(mtd_tasks),
        'completed': sum(1 for task in mtd_tasks if task['status'] == 'เสร็จสมบูรณ์'),
        'cancelled': sum(1 for task in mtd_tasks if task['status'] == 'ยกเลิก'),
        'pending': sum(1 for task in mtd_tasks if task['status'] == 'กำลังดำเนินการ')
    }

    return context

def get_app_logo():
    navbar_settings = frappe.get_single("Navbar Settings")
    if navbar_settings.app_logo:
        return navbar_settings.app_logo
    return None

def get_employee_tasks(user):
    # ข้อมูลจำลองสำหรับงานของพนักงาน
    return [
        {"name": "TASK-001", "subject": "Install New Wifi", "priority": "สูง", "due_date": datetime.now() + timedelta(days=2)},
        {"name": "TASK-002", "subject": "Maintain Server", "priority": "ปานกลาง", "due_date": datetime.now() + timedelta(days=5)},
        {"name": "TASK-003", "subject": "Configure New Printer", "priority": "สูง", "due_date": datetime.now() + timedelta(days=1)},
        {"name": "TASK-004", "subject": "Preventive Maintenance", "priority": "ต่ำ", "due_date": datetime.now() + timedelta(days=7)},
        {"name": "TASK-005", "subject": "Collect Data", "priority": "สูง", "due_date": datetime.now() + timedelta(days=3)}
    ]

def get_pending_documents(user):
    # ข้อมูลจำลองสำหรับเอกสารที่รอดำเนินการ
    return [
        {"name": "SR-001", "doctype": "SMO Service Report", "date": datetime.now() - timedelta(days=1), "url": "/smo-service-report/SR-001"},
        {"name": "EE-001", "doctype": "SMO Expense Entry", "date": datetime.now() - timedelta(days=2), "url": "/smo-expense-entry/EE-001"},
        {"name": "ER-001", "doctype": "SMO Expense Request", "date": datetime.now() - timedelta(days=3), "url": "/smo-expense-request/ER-001"},
        {"name": "AE-001", "doctype": "SMO Advance Entry", "date": datetime.now() - timedelta(days=4), "url": "/smo-advance-entry/AE-001"},
        {"name": "SR-002", "doctype": "SMO Service Report", "date": datetime.now() - timedelta(days=5), "url": "/smo-service-report/SR-002"}
    ]

def get_recent_documents(user):
    # ข้อมูลจำลองสำหรับเอกสารล่าสุด
    return [
        {"name": "FILE-001", "file_name": "รายงานยอดขายประจำเดือน.pdf", "modified": datetime.now() - timedelta(hours=2)},
        {"name": "FILE-002", "file_name": "แผนการตลาด Q2.docx", "modified": datetime.now() - timedelta(hours=5)},
        {"name": "FILE-003", "file_name": "ใบเสนอราคาลูกค้า A.xlsx", "modified": datetime.now() - timedelta(days=1)},
        {"name": "FILE-004", "file_name": "รายชื่อลูกค้าใหม่.csv", "modified": datetime.now() - timedelta(days=2)},
        {"name": "FILE-005", "file_name": "สรุปการประชุมทีม.pptx", "modified": datetime.now() - timedelta(days=3)}
    ]

def get_upcoming_events(user):
    # ข้อมูลจำลองสำหรับกิจกรรมที่กำลังจะมาถึง
    return [
        {"subject": "ประชุมทีมขายประจำสัปดาห์", "starts_on": datetime.now() + timedelta(days=1)},
        {"subject": "อบรมพนักงานใหม่", "starts_on": datetime.now() + timedelta(days=3)},
        {"subject": "นำเสนอโครงการกับลูกค้า", "starts_on": datetime.now() + timedelta(days=5)},
        {"subject": "สัมมนาการตลาดออนไลน์", "starts_on": datetime.now() + timedelta(days=7)},
        {"subject": "ประชุมสรุปผลงานประจำเดือน", "starts_on": datetime.now() + timedelta(days=10)}
    ]

def get_ytd_tasks():
    # ข้อมูลจำลองสำหรับงานสะสมปีนี้ (YTD)
    return [
        {"name": "TASK-001", "status": "Completed"},
        {"name": "TASK-002", "status": "Open"},
        {"name": "TASK-003", "status": "Completed"},
        {"name": "TASK-004", "status": "Cancelled"},
        {"name": "TASK-005", "status": "Open"},
        {"name": "TASK-006", "status": "Completed"},
        {"name": "TASK-007", "status": "Open"},
        {"name": "TASK-008", "status": "Completed"},
        {"name": "TASK-009", "status": "Cancelled"},
        {"name": "TASK-010", "status": "Open"}
    ]

def get_mtd_tasks():
    # ข้อมูลจำลองสำหรับงานเดือนนี้ (MTD)
    return [
        {"name": "TASK-011", "status": "เสร็จสมบูรณ์"},
        {"name": "TASK-012", "status": "กำลังดำเนินการ"},
        {"name": "TASK-013", "status": "เสร็จสมบูรณ์"},
        {"name": "TASK-014", "status": "ยกเลิก"},
        {"name": "TASK-015", "status": "กำลังดำเนินการ"},
        {"name": "TASK-016", "status": "เสร็จสมบูรณ์"},
        {"name": "TASK-017", "status": "กำลังดำเนินกา��"},
        {"name": "TASK-018", "status": "เสร็จสมบูรณ์"}
    ]

def get_total_tasks():
    return frappe.db.count('Task', {'owner': frappe.session.user})

def get_tasks_by_status(status):
    return frappe.db.count('Task', {'owner': frappe.session.user, 'status': status})