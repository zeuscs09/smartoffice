import frappe
from frappe import _
from datetime import datetime, timedelta

def get_week_range(date):
    start = date - timedelta(days=(date.weekday() + 1) % 7)  # วันอาทิตย์
    end = start + timedelta(days=6)  # วันเสาร์
    return start, end

@frappe.whitelist()
def get_dashboard_home(time_range):
    today = datetime.now().date()
    
    if time_range == 'week':
        start_date, end_date = get_week_range(today)
    elif time_range == 'month':
        start_date = today.replace(day=1)
        end_date = (start_date.replace(month=start_date.month % 12 + 1) - timedelta(days=1))
    else:  # year
        start_date = today.replace(month=1, day=1)
        end_date = today.replace(month=12, day=31)

    current_period = {
        'start_date': start_date,
        'end_date': end_date
    }
    
    if time_range == 'week':
        previous_start, previous_end = get_week_range(start_date - timedelta(days=7))
    elif time_range == 'month':
        previous_end = start_date - timedelta(days=1)
        previous_start = previous_end.replace(day=1)
    else:  # year
        previous_end = start_date - timedelta(days=1)
        previous_start = previous_end.replace(month=1, day=1)
    
    previous_period = {
        'start_date': previous_start,
        'end_date': previous_end
    }

    user = frappe.session.user

    current_stats = get_period_stats(current_period, user)
    previous_stats = get_period_stats(previous_period, user)

    return {
        'total_tasks': {
            'current': current_stats['total_tasks'],
            'previous': previous_stats['total_tasks'],
            'change': get_percentage_change(current_stats['total_tasks'], previous_stats['total_tasks'])
        },
        'urgent_tasks': {
            'current': current_stats['urgent_tasks'],
            'previous': previous_stats['urgent_tasks'],
            'change': get_percentage_change(current_stats['urgent_tasks'], previous_stats['urgent_tasks'])
        },
        'completed_tasks': {
            'current': current_stats['completed_tasks'],
            'previous': previous_stats['completed_tasks'],
            'change': get_percentage_change(current_stats['completed_tasks'], previous_stats['completed_tasks'])
        },
        'period': {
            'current': {
                'start': current_period['start_date'].strftime('%Y-%m-%d'),
                'end': current_period['end_date'].strftime('%Y-%m-%d')
            },
            'previous': {
                'start': previous_period['start_date'].strftime('%Y-%m-%d'),
                'end': previous_period['end_date'].strftime('%Y-%m-%d')
            }
        }
    }

def get_previous_period(start_date, end_date):
    period_length = end_date - start_date
    return {
        'start_date': start_date - period_length - timedelta(days=1),
        'end_date': start_date - timedelta(days=1)
    }

def get_period_stats(period, user):
    return {
        'total_tasks': frappe.db.count('ToDo', filters={
            'date': ['between', [period['start_date'], period['end_date']]],
            'allocated_to': user
        }),
        'urgent_tasks': frappe.db.count('ToDo', filters={
            'date': ['between', [period['start_date'], period['end_date']]],
            'priority': 'High',
            'allocated_to': user
        }),
        'completed_tasks': frappe.db.count('ToDo', filters={
            'date': ['between', [period['start_date'], period['end_date']]],
            'status': 'Closed',
            'allocated_to': user
        })
    }

def get_percentage_change(current, previous):
    if previous == 0:
        return 100 if current > 0 else 0
    change = ((current - previous) / previous) * 100
    return round(change, 2)

@frappe.whitelist()
def get_heatmap_data(start_date=None, end_date=None):
    if not start_date:
        start_date = (datetime.now() - timedelta(days=365)).strftime('%Y-%m-%d')
    if not end_date:
        end_date = datetime.now().strftime('%Y-%m-%d')

    # ดึงข้อมูลผู้ใช้ที่เข้าสู่ระบบ
    user = frappe.session.user

    # สร้าง SQL query
    sql = """
        SELECT DATE(date) as date, COUNT(*) as count
        FROM `tabToDo`
        WHERE 1=1
        and date BETWEEN %s AND %s
        AND allocated_to = %s
        GROUP BY DATE(date)
    """
    
    # พิมพ์ SQL query
    frappe.errprint(sql)
    
    # ดำเนินการ query
    data = frappe.db.sql(sql, (start_date, end_date, user), as_dict=True)

    # แปลงข้อมูลให้อยู่ในรูปแบบที่ Heatmap ต้องการ
    heatmap_data = {item['date'].strftime('%Y-%m-%d'): item['count'] for item in data}

    return heatmap_data
