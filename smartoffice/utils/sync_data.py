import frappe
from frappe.utils import now
import pymysql

def sync_vtiger_projects():
    # ดึงการตั้งค่าจาก Smart Office Setting
    settings = frappe.get_single("Smart Office Setting")
    
    # แยก host และ port (ถ้ามี)
    host_parts = settings.db_host.split(':')
    host = host_parts[0]
    port = int(host_parts[1]) if len(host_parts) > 1 else 3306
    
    # เชื่อมต่อกับ MariaDB
    connection = pymysql.connect(
        host=host,
        port=port,
        user=settings.db_user,
        password=settings.get_password('db_password'),
        database=settings.db_name
    )
    
    try:
        with connection.cursor(pymysql.cursors.DictCursor) as cursor:
            # Query ข้อมูลจาก vtiger
            sql = """
                select
                    vp.projectid,
                    vp.projectname project_code,
                    vp.project_no project_number,
                    vp4.cf_734 project_name,
                    vp3.potential_no custom_opportunity_id,
                    va.account_no customer,
                    vp.projecttype project_type,
                    vp.projectstatus
                from vtiger_project vp
                inner join vtiger_account va on vp.linktoaccountscontacts = va.accountid 
                left join vtiger_projectcf vp4 on vp.projectid = vp4.projectid
                left join vtiger_potentialscf vp2 on vp.projectname = vp2.cf_782
                left join vtiger_potential vp3 on vp2.potentialid = vp3.potentialid
            """
            cursor.execute(sql)
            projects = cursor.fetchall()

            # Sync ข้อมูลไปยัง Frappe
            for project in projects:
                try:
                    project_data = {
                        "project_number": project["project_number"],
                        "project_name": project["project_name"],
                        "custom_opportunity_id": project["custom_opportunity_id"],
                        "customer": project["customer"],
                        "project_type": project["project_type"],
                        "status": project["projectstatus"],
                        "custom_project_code": project["project_code"],
                        "modified": now()
                    }

                    if frappe.db.exists("Project", project["project_code"]):
                        # Update existing project
                        doc = frappe.get_doc("Project", project["project_code"])
                        doc.update(project_data)
                        doc.save()
                    else:
                        # Create new project
                        doc = frappe.get_doc({
                            "doctype": "Project",
                            "name": project["project_code"],
                            "project_code": project["project_code"],
                            **project_data
                        })
                        doc.flags.ignore_mandatory = True
                        doc.insert(ignore_permissions=True)

                except Exception as e:
                    frappe.log_error(title="Error syncing project", message=f"Error syncing project {project['project_code']}: {str(e)}")
                    continue

    finally:
        connection.close()

def sync_vtiger_customers():
    # ดึงการตั้งค่าจาก Smart Office Setting
    settings = frappe.get_single("Smart Office Setting")
    
    # แยก host และ port (ถ้ามี)
    host_parts = settings.db_host.split(':')
    host = host_parts[0]
    port = int(host_parts[1]) if len(host_parts) > 1 else 3306
    
    # เชื่อมต่อกับ MariaDB
    connection = pymysql.connect(
        host=host,
        port=port,
        user=settings.db_user,
        password=settings.get_password('db_password'),
        database=settings.db_name
    )
    
    try:
        with connection.cursor(pymysql.cursors.DictCursor) as cursor:
            sql = """
                SELECT
                    account_no name,
                    accountname customer_name,
                    va.cf_766 custom_customer_name_local,
                    industry customer_group
                FROM vtiger_account a
                LEFT JOIN vtiger_accountscf va ON a.accountid = va.accountid
            """
            cursor.execute(sql)
            customers = cursor.fetchall()

            for customer in customers:
                try:
                    # Debug: พิมพ์ค่าที่ได้จาก Vtiger
                    frappe.errprint(f"Customer data from Vtiger: {customer}")
                    
                    # ตรวจสอบและสร้าง Customer Group ถ้ายังไม่มี
                    if customer["customer_group"] and not frappe.db.exists("Customer Group", customer["customer_group"]):
                        customer_group = frappe.get_doc({
                            "doctype": "Customer Group",
                            "customer_group_name": customer["customer_group"],
                            "parent_customer_group": "All Customer Groups"
                        })
                        customer_group.insert(ignore_permissions=True)
                        frappe.db.commit()

                    # เตรียมข้อมูลสำหรับ update/insert
                    customer_data = {
                        "customer_name": customer["customer_name"],
                        "customer_group": customer["customer_group"],
                        "custom_customer_name_local": customer["custom_customer_name_local"],
                        "modified": now()
                    }
                    
                    # เพิ่ม custom_customer_name_local ถ้ามีค่า
                    
                    if frappe.db.exists("Customer", customer["name"]):
                        # Debug: พิมพ์ค่าที่จะ update
                        frappe.errprint(f"Updating customer {customer['name']} with data: {customer_data}")
                        
                        # Update existing customer
                        frappe.db.set_value(
                            "Customer",
                            customer["name"],
                            customer_data,
                            update_modified=False
                        )
                        frappe.db.commit()
                    else:
                        # Debug: พิมพ์ค่าที่จะ insert
                        print(f"Inserting new customer with data: {customer_data}")
                        
                        # Create new customer
                        doc = frappe.get_doc({
                            "doctype": "Customer",
                            "name": customer["name"],
                            **customer_data
                        })
                        doc.flags.ignore_mandatory = True
                        doc.insert(ignore_permissions=True, ignore_if_duplicate=True)
                        frappe.db.commit()

                except Exception as e:
                    error_msg = str(e)[:100]
                    frappe.log_error(
                        title=f"Error syncing customer {customer['name']}", 
                        message=error_msg
                    )
                    print(f"Error syncing customer {customer['name']}: {error_msg}")  # Debug
                    continue

    finally:
        connection.close()

def daily_sync_vtiger_data():
    """
    ฟังก์ชันสำหรับ sync ข้อมูลจาก Vtiger โดย sync customers ก่อนแล้วค่อย sync projects
    """
    try:
        # Sync Customers ก่อน
        sync_vtiger_customers()
        
        # รอให้ sync customers เสร็จก่อน (ไม่ใช้ async) แล้วค่อย sync projects
        frappe.db.commit()  # commit การเปลี่ยนแปลงของ customers
        
        # Sync Projects
        sync_vtiger_projects()
        
        frappe.logger().info("Scheduled Vtiger sync completed successfully")
        
    except Exception as e:
        frappe.logger().error(f"Error in scheduled Vtiger sync: {str(e)}")
