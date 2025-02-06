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
                    va.accountname custom_customer_name,
                    vp.projecttype project_type,
                    vp.projectstatus
                from vtiger_project vp
                inner join vtiger_account va on vp.linktoaccountscontacts = va.accountid 
                left join vtiger_projectcf vp4 on vp.projectid = vp4.projectid
                left join vtiger_potentialscf vp2 on vp.projectname = vp2.cf_782 and vp2.cf_782 <>''
                left join vtiger_potential vp3 on vp2.potentialid = vp3.potentialid
            """
            cursor.execute(sql)
            projects = cursor.fetchall()

            # เพิ่มตัวแปรสำหรับนับ
            success_count = 0
            error_count = 0

            # Sync ข้อมูลไปยัง Frappe
            for project in projects:
                try:
                    # Debug: พิมพ์ค่าที่ได้จาก Vtiger
                    # print(f"Project data from Vtiger: {project}")
                    
                    project_data = {
                        "custom_project_number": project["project_number"],
                        "project_name": project["project_name"],
                        "custom_opportunity_id": project["custom_opportunity_id"],
                        "customer": project["customer"],
                        "custom_customer_name": project["custom_customer_name"],
                        "project_type": project["project_type"],
                        "status": project["projectstatus"],
                        "custom_project_code": project["project_code"],
                        "modified": now()
                    }

                    if frappe.db.exists("Project", project["project_number"]):
                        # Debug: พิมพ์ค่าที่จะ update
                        # print(f"Updating project {project['project_number']} with data: {project_data}")
                        
                        # Update existing project
                        frappe.db.set_value(
                            "Project",
                            project["project_number"],
                            project_data,
                            update_modified=False
                        )
                        frappe.db.commit()
                    else:
                        # Debug: พิมพ์ค่าที่จะ insert
                        # print(f"Inserting new project with data: {project_data}")
                        
                        # Create new project
                        doc = frappe.get_doc({
                            "doctype": "Project",
                            "name": project["project_number"],
                            **project_data
                        })
                        doc.flags.ignore_mandatory = True
                        doc.insert(ignore_permissions=True, ignore_if_duplicate=True)
                        frappe.db.commit()
                    
                    success_count += 1
                
                except Exception as e:
                    error_count += 1
                    error_msg = str(e)
                    frappe.log_error(
                        title=f"Error syncing project {project['project_number']}", 
                        message=error_msg
                    )
                    print(f"Error syncing project {project['project_number']}: {error_msg}")  # Debug
                    continue
            
            # แสดงสรุปหลังจาก sync เสร็จ
            print(f"\nProject Sync Summary:")
            print(f"Total Projects: {len(projects)}")
            print(f"Successfully Synced: {success_count}")
            print(f"Failed: {error_count}")
                    
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

            # เพิ่มตัวแปรสำหรับนับ
            success_count = 0
            error_count = 0
            
            for customer in customers:
                try:
                    # Debug: พิมพ์ค่าที่ได้จาก Vtiger
                   
                    
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
                      
                        
                        # Create new customer
                        doc = frappe.get_doc({
                            "doctype": "Customer",
                            "name": customer["name"],
                            **customer_data
                        })
                        doc.flags.ignore_mandatory = True
                        doc.insert(ignore_permissions=True, ignore_if_duplicate=True)
                        frappe.db.commit()
                        
                        # ตรวจสอบว่ามี Customer Site หรือไม่
                        if not frappe.db.exists("SMO Customer Site", {"customer": customer["name"]}):
                            # สร้าง Customer Site HQ
                            site_doc = frappe.get_doc({
                                "doctype": "SMO Customer Site",
                                "customer": customer["name"],
                                "site_name": "HQ",
                                "depart_km": 0,
                                "return_km": 0
                            })
                            site_doc.insert(ignore_permissions=True)
                            frappe.db.commit()
                    
                    success_count += 1

                except Exception as e:
                    error_count += 1
                    error_msg = str(e)[:100]
                    frappe.log_error(
                        title=f"Error syncing customer {customer['name']}", 
                        message=error_msg
                    )
                    print(f"Error syncing customer {customer['name']}: {error_msg}")
                    continue
            
            # แสดงสรุปหลังจาก sync เสร็จ
            print(f"\nCustomer Sync Summary:")
            print(f"Total Customers: {len(customers)}")
            print(f"Successfully Synced: {success_count}")
            print(f"Failed: {error_count}")

    finally:
        connection.close()

def sync_vtiger_opportunity():
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
                select 
                    va.account_no as party_name,
                    'Customer' as opportunity_from,
                    potential_no as name,
                    amount as opportunity_amount,
                    sales_stage,
                    potentialname custom_opportunity_name,
                    pj.cf_782 project_code
                from 
                    vtiger_potential po inner join
                    vtiger_account va on po.related_to = va.accountid 
                        left join vtiger_potentialscf pj on po.potentialid = pj.potentialid                      
            """
            cursor.execute(sql)
            opportunities = cursor.fetchall()

            # เพิ่มตัวแปรสำหรับนับ
            success_count = 0
            error_count = 0
            
            for opportunity in opportunities:
                try:
                    # ตรวจสอบและสร้าง Sales Stage ถ้ายังไม่มี
                    if opportunity["sales_stage"] and not frappe.db.exists("Sales Stage", opportunity["sales_stage"]):
                        sales_stage = frappe.get_doc({
                            "doctype": "Sales Stage",
                            "stage_name": opportunity["sales_stage"]
                        })
                        sales_stage.insert(ignore_permissions=True)
                        frappe.db.commit()

                    opportunity_data = {
                        "opportunity_from": opportunity["opportunity_from"],
                        "party_name": opportunity["party_name"],
                        "opportunity_amount": opportunity["opportunity_amount"],
                        "sales_stage": opportunity["sales_stage"],
                        "custom_opportunity_name": opportunity["custom_opportunity_name"],
                        "modified": now()
                    }

                    if frappe.db.exists("Opportunity", opportunity["name"]):
                        # Update existing opportunity
                        frappe.db.set_value(
                            "Opportunity",
                            opportunity["name"],
                            opportunity_data,
                            update_modified=False
                        )
                        frappe.db.commit()
                    else:
                        # Create new opportunity
                        doc = frappe.get_doc({
                            "doctype": "Opportunity",
                            "name": opportunity["name"],
                            **opportunity_data
                        })
                        doc.flags.ignore_mandatory = True
                        doc.insert(ignore_permissions=True, ignore_if_duplicate=True)
                        frappe.db.commit()
                    
                    success_count += 1

                except Exception as e:
                    error_count += 1
                    error_msg = str(e)
                    frappe.log_error(
                        title=f"Error syncing opportunity {opportunity['name']}", 
                        message=error_msg
                    )
                    print(f"Error syncing opportunity {opportunity['name']}: {error_msg}")
                    continue
            
            # แสดงสรุปหลังจาก sync เสร็จ
            print(f"\nOpportunity Sync Summary:")
            print(f"Total Opportunities: {len(opportunities)}")
            print(f"Successfully Synced: {success_count}")
            print(f"Failed: {error_count}")

    finally:
        connection.close()

def daily_sync_vtiger_data():
    """
    ฟังก์ชันสำหรับ sync ข้อมูลจาก Vtiger โดย sync customers ก่อนแล้วค่อย sync projects และ opportunities
    """
    try:
        # Sync Customers ก่อน
        sync_vtiger_customers()
        
        # รอให้ sync customers เสร็จก่อน (ไม่ใช้ async) แล้วค่อย sync projects
        frappe.db.commit()  # commit การเปลี่ยนแปลงของ customers
        
        # Sync Projects
        sync_vtiger_projects()

        # Sync Opportunities
        sync_vtiger_opportunity()
        
        frappe.logger().info("Scheduled Vtiger sync completed successfully")
        
    except Exception as e:
        frappe.logger().error(f"Error in scheduled Vtiger sync: {str(e)}")
