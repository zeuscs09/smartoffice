// Copyright (c) 2024, beansx and contributors
// For license information, please see license.txt

frappe.ui.form.on("SMO Service Report", {
  refresh(frm) {
    if(frappe.utils.get_query_params().from){
      frappe.breadcrumbs.add("");
    }
    // เพิ่มปุ่มย้อนกลับ
    frm.add_custom_button(__('Back'), function() {
      // ตรวจสอบว่ามี from_page หรือไม่
      // if (frm.doc.from_page) {
      //  location.href = frm.doc.from_page;
      // } else {
      //   // ถ้าไม่มี from_page ให้ย้อนกลับไปหน้า List View
      //   frappe.set_route("List", "SMO Service Report");
      // }
      history.back();
    });

    if (frm.doc.workflow_state === "Customer Review" && frm.doc.from_page) {
      // frappe.set_route("/" + frm.doc.from_page);
      //location.href = "/" + frm.doc.from_page;
      
    }
  },
  before_save: function(frm) {
    var hour = frm.doc.start_hour_input;  // ดึงค่าจากฟิลด์ชั่วโมง
    var minute = frm.doc.start_minute_input;  // ดึงค่าจากฟิลด์นาที
    
    if (hour && minute) {
        var time_value = frm.doc.start_date_input + ' ' + hour + ':' + minute;
        frm.set_value('job_start_on', time_value);
    }

     hour = frm.doc.finish_hour_input;  // ดึงค่าจากฟิลด์ชั่วโมง
     minute = frm.doc.finish_minute_input;  // ดึงค่าจากฟิลด์นาที
    
    if (hour && minute) {
        var time_value = frm.doc.finish_date_input + ' ' + hour + ':' + minute;
        frm.set_value('job_finish', time_value);
    }
    // validate วันที่เริ่มงานต้องน้อยกว่าวันที่สิ้นสุดงาน
    if (frm.doc.job_start_on > frm.doc.job_finish) {
        frappe.throw("Start date cannot be greater than Finish date");
    }

    if (frm.doc.start_date_input > frm.doc.finish_date_input) {
      frm.set_value('over_night', 1);
    }
  },
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
                     row.overlapping_job_on_date = d.overlapping_job_on_date;
                     row.filter=d.filter;
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
  start_date_input: function(frm) {
    if(frm.doc.start_date_input) {
        
        frm.set_value("finish_date_input", frm.doc.start_date_input);
    }
}
});
frappe.ui.form.on("SMO Working Team", {

  view_task(frm,cdt, cdn) {
    let row = locals[cdt][cdn];
    let url=`/app/smo-task/${row.filter}`;
    window.open(url);
  },
});
