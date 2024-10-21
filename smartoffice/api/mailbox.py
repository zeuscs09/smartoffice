import frappe
@frappe.whitelist()
def get_mail_box(page=1, page_size=10, search=None, status=None, start_date=None, end_date=None, sort_field=None, sort_order=None):
    user = frappe.session.user
    
    page = int(page)
    page_size = int(page_size)
    offset = (page - 1) * page_size

    conditions = ["for_user = %s", "type = 'Alert'"]
    params = [user]

    if search:
        conditions.append("subject LIKE %s")
        params.append(f"%{search}%")

    if status:
        conditions.append("`read` = %s")
        params.append(1 if status.lower() == 'read' else 0)

    if start_date:
        conditions.append("creation >= %s")
        params.append(start_date)

    if end_date:
        conditions.append("creation <= %s")
        params.append(end_date)

    sort_clause = f"ORDER BY {sort_field} {sort_order}" if sort_field and sort_order else "ORDER BY creation DESC"

    query = f"""
    SELECT
        tnl.name,
        document_type,
        document_name,
        `_seen`,
        owner,
        creation,
        modified,
        for_user,
        subject,
        `read`,
        COUNT(*) OVER () as total_count,
        tu.full_name
    FROM
        `tabNotification Log` tnl left join
	(select name,full_name from `tabUser`) tu on tnl.owner =tu.name
    WHERE
        {" AND ".join(conditions)}
    {sort_clause}
    LIMIT %s OFFSET %s
    """

    params.extend([page_size, offset])

    result = frappe.db.sql(query, tuple(params), as_dict=True)

    total_count = result[0].total_count if result else 0

    for row in result:
        row['link'] = frappe.utils.get_url_to_form(row['document_type'], row['document_name'])
        doctype_meta = frappe.get_meta(row['document_type'])
        row['doctype_description'] = doctype_meta.description if doctype_meta else row['document_type']

    return {
        "data": [
            {k: v for k, v in item.items() if k != 'total_count'}
            for item in result
        ],
        "total": total_count,
        "page": page,
        "page_size": page_size,
        "total_pages": -(-total_count // page_size)  # การหารปัดขึ้น
    }

@frappe.whitelist()
def update_notification_read(name):
    try:
        # ตรวจสอบและทำความสะอาดข้อมูลนำเข้า
        if not isinstance(name, str) or not name.strip():
            return {"success": False, "message": "รหัสการแจ้งเตือนไม่ถูกต้อง"}

        # ใช้ frappe.db.set_value เพื่อป้องกัน SQL injection
        frappe.db.set_value('Notification Log', name, 'read', 1)
        
        frappe.db.commit()
        
        return {"success": True, "message": "การแจ้งเตือนถูกทำเครื่องหมายว่าอ่านแล้ว"}
    except frappe.DoesNotExistError:
        frappe.db.rollback()
        return {"success": False, "message": "ไม่พบการแจ้งเตือนที่ระบุ"}
    except Exception as e:
        frappe.db.rollback()
        return {"success": False, "message": f"เกิดข้อผิดพลาด: {str(e)}"}
