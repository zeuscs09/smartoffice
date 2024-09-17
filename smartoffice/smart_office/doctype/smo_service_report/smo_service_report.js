// Copyright (c) 2024, beansx and contributors
// For license information, please see license.txt

frappe.ui.form.on("SMO Service Report", {
  refresh(frm) {},
  task(frm) {
    // get data from SMO Working Team where parent=task parenttype='SMO Task' and parentfield='team'
    frappe.call({
        method: 'smartoffice.smart_office.doctype.smo_task.smo_task.fetch_task_data',  // API ที่สร้างไว้
        args: {
            task: frm.doc.task  // ส่งค่า task ที่เลือกไปยัง API
        },
        callback: function(r) {
            if (r.message) {
                 // ล้างข้อมูลใน child table ก่อน เพื่อให้ข้อมูลไม่ซ้ำ
                 console.log(r.message);
                 frm.clear_table('team');

                 // วนลูปเพิ่มข้อมูลที่ได้จาก API ลงใน child table
                 $.each(r.message, function(i, d) {
                     // เพิ่มแถวใหม่ใน child table
                     console.log(d.full_name)
                     let row = frm.add_child('team');
                     console.log("row",row);
                    
                     row.user = d.user;  // แทนที่ด้วยฟิลด์จริงใน child table
                     row.email = d.email;  // แทนที่ด้วยฟิลด์จริงใน child table
                     
                     row.full_name = d.full_name;  // แทนที่ด้วยฟิลด์จริงใน child table
                 });

                 // รีเฟรชหน้าจอเพื่อแสดงข้อมูลใน child table
                 frm.refresh_field('team');
            }
        }
    });
  },
  customer(frm) {
    frm.set_query("customer_site", () => {
      return {
        filters: {
          customer: frm.doc.customer,
        },
      };
    });
  },
});
