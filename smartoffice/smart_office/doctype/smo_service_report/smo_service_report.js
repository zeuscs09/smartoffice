// Copyright (c) 2024, beansx and contributors
// For license information, please see license.txt

frappe.ui.form.on("SMO Service Report", {
  refresh(frm) {
    // if(frappe.utils.get_query_params().from){
    //   frappe.breadcrumbs.add("");
    //   $('.navbar').hide();
    //   $('.standard-actions').hide();
    //   // $('.next-doc').hide();
    // }
    if (frm.doc.from_page || frappe.utils.get_query_params().from_page) {
      $(".navbar").css("visibility", "hidden");
      $(".menu-btn-group").hide();
      $(".page-icon-group").hide();
      if (window.opener && typeof window.opener.refresh_table === 'function') {
        window.opener.refresh_table();
      }
      frm.add_custom_button(__("Close"), function () {
        window.close();
      });
    }
    
    // เพิ่มการตรวจสอบว่าสามารถใช้ history.back() ได้หรือไม่
    // const canGoBack = window.history.length > 1;
    
    // frm.add_custom_button(__(canGoBack ? 'Back' : 'Close'), function() {
    //   if (canGoBack) {
    //     history.back();
    //   } else {
    //     // ดำเนินการเมื่อไม่สามารถย้อนกลับได้
    //     // ัวอย่างเช่น ปิดหน้าต่างหรือนำทางไปยังหน้าหลัก
    //    window.close();
    //   }
    // });

    if (frm.doc.workflow_state && frm.doc.workflow_state !== "Draft") {
      frm.disable_form();
    }

    if (frm.doc.from_todo && !frm.doc.start_date_input) {
      frappe.db.get_value('ToDo', frm.doc.from_todo, 'date')
        .then(r => {
          if (r.message && r.message.date) {
            frm.set_value('start_date_input', r.message.date);
          }
        });
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
                     row.employee = d.employee;
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
  from_page(frm) {
    if(frm.doc.from_page) {
      $('.navbar').hide();
      $('.standard-actions').hide();
    }
  },
  start_date_input: function(frm) {
    if(frm.doc.start_date_input) {
      frm.set_value("finish_date_input", frm.doc.start_date_input);
      recalculateEndTime(frm);
    }
  },
  start_hour_input: function(frm) {
    recalculateEndTime(frm);
  },
  start_minute_input: function(frm) {
    recalculateEndTime(frm);
  },
  duration: function(frm) {
    recalculateEndTime(frm);
  },
});

// แยกฟังก์ชันคำนวณเวลาออกมาเพื่อเรียกใช้ซ้ำ
function recalculateEndTime(frm) {
  if (frm.doc.start_date_input && frm.doc.start_hour_input && 
      frm.doc.start_minute_input && frm.doc.duration) {
    // แปลงเวลาเริ่มต้นเป็น Date object และตั้งค่า timezone เป็น UTC
    let startDateTime = new Date(frm.doc.start_date_input + 'T00:00:00Z');
    startDateTime.setUTCHours(parseInt(frm.doc.start_hour_input));
    startDateTime.setUTCMinutes(parseInt(frm.doc.start_minute_input));

    // แปลงวินาทีเป็นชั่วโมงและนาที
    let durationHours = Math.floor(frm.doc.duration / 3600);
    let durationMinutes = Math.floor((frm.doc.duration % 3600) / 60);
    
    // คำนวณเวลาสิ้นสุดโดยเพิ่มจำนวนมิลลิวินาที
    let endDateTime = new Date(startDateTime.getTime() + 
      (durationHours * 60 * 60 * 1000) + 
      (durationMinutes * 60 * 1000));

    // แปลงวันที่เป็น YYYY-MM-DD format
    let endDate = endDateTime.toISOString().split('T')[0];
    frm.set_value('finish_date_input', endDate);

    // set ค่าชั่วโมงสิ้นสุด
    let endHour = endDateTime.getUTCHours().toString().padStart(2, '0');
    frm.set_value('finish_hour_input', endHour);

    // set ค่านาทีสิ้นสุด
    let endMinute = endDateTime.getUTCMinutes();
    let validMinutes = [0, 10, 20, 30, 40, 50];
    let closestMinute = validMinutes.reduce((prev, curr) => {
      return (Math.abs(curr - endMinute) < Math.abs(prev - endMinute) ? curr : prev);
    });
    frm.set_value('finish_minute_input', closestMinute.toString().padStart(2, '0'));

    // เช็คว่าเป็นการทำงานข้ามคืนหรือไม่
    if (startDateTime.getUTCDate() !== endDateTime.getUTCDate()) {
      frm.set_value('over_night', 1);
    } else {
      frm.set_value('over_night', 0);
    }
  }
}

frappe.ui.form.on("SMO Working Team", {

  view_task(frm,cdt, cdn) {
    let row = locals[cdt][cdn];
    let url=`/app/smo-task/${row.filter}`;
    window.open(url);
  },
});
