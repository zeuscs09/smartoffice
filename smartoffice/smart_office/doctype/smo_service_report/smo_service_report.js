// Copyright (c) 2024, beansx and contributors
// For license information, please see license.txt

frappe.ui.form.on("SMO Service Report", {
  refresh(frm) {
    if (!frappe.user.has_role("System Manager")) {
      if (
        frm.doc.workflow_state !== "Customer Reject" ||
        frm.doc.owner !== frappe.session.user
      ) {
        frm.page.btn_secondary.hide();
      } else {
        frm.page.btn_secondary.show();
      }
    }
    if (frm.doc.from_page || frappe.utils.get_query_params().from_page) {
      // ตรวจสอบว่าผู้ใช้มีสิทธิ์ System Manager หรือไม่
      if (!frappe.user.has_role("System Manager")) {
        $(".navbar").css("visibility", "hidden");
        $(".menu-btn-group").hide();
        $(".page-icon-group").hide();
      }

      if (window.opener && typeof window.opener.refresh_table === "function") {
        window.opener.refresh_table();
      }
      frm.add_custom_button(__("Close"), function () {
        window.close();
      });
    }

    if (frm.doc.workflow_state && frm.doc.workflow_state !== "Draft") {
      frm.disable_form();
    }

    // Add Resend Email button for submitted documents in Customer Review state
    if (frm.doc.docstatus === 1 && frm.doc.workflow_state === "Customer Review" && frm.doc.contact_email) {
      frm.add_custom_button(__("Resend Email"), function() {
        frappe.confirm(
          __("Are you sure you want to resend the approval email to {0}?", [frm.doc.contact_email]),
          function() {
            frappe.call({
              method: "smartoffice.smart_office.doctype.smo_service_report.smo_service_report.resend_approval_email",
              args: {
                name: frm.doc.name
              },
              freeze: true,
              freeze_message: __("Sending email..."),
              callback: function(r) {
                if (!r.exc) {
                  frappe.msgprint({
                    title: __("Success"),
                    indicator: "green",
                    message: __("Email has been resent to {0} with new approval links", [frm.doc.contact_email])
                  });
                  // Refresh the form to show updated approval data
                  frm.reload_doc();
                }
              }
            });
          }
        );
      });
    }

    if (frm.doc.from_todo && !frm.doc.start_date_input) {
      frappe.db.get_value("ToDo", frm.doc.from_todo, "date").then((r) => {
        if (r.message && r.message.date) {
          frm.set_value("start_date_input", r.message.date);
        }
      });
    }

    // เพิ่มการเรียก API เพื่อดึง open_date
    frappe.db.get_single_value('Smart Office Setting', 'open_date')
      .then(open_date => {
        if (open_date) {
          frm.set_df_property('start_date_input', 'min_date', open_date);
          frm.set_df_property('finish_date_input', 'min_date', open_date);
          
          // ตรวจสอบค่าปัจจุบันและแจ้งเตือนถ้าน้อยกว่า open_date
          if (frm.doc.start_date_input && frm.doc.start_date_input < open_date) {
            frm.set_value('start_date_input', '');
            frappe.msgprint({
              title: 'ข้อผิดพลาด',
              indicator: 'red',
              message: `วันที่เริ่มต้นต้องไม่น้อยกว่า ${open_date}`
            });
          }
          
          if (frm.doc.finish_date_input && frm.doc.finish_date_input < open_date) {
            frm.set_value('finish_date_input', '');
            frappe.msgprint({
              title: 'ข้อผิดพลาด',
              indicator: 'red',
              message: `วันที่สิ้นสุดต้องไม่น้อยกว่า ${open_date}`
            });
          }
        }
      });
  },
  before_save: function (frm) {
    // เพิ่มการตรวจสอบ open_date ก่อนบันทึก
    return new Promise((resolve, reject) => {
      frappe.db.get_single_value('Smart Office Setting', 'open_date')
        .then(open_date => {
          if (open_date) {
            if (frm.doc.start_date_input && frm.doc.start_date_input < open_date) {
              frappe.throw({
                title: 'ข้อผิดพลาด',
                message: `วันที่เริ่มต้นต้องไม่น้อยกว่า ${open_date}`
              });
              reject();
              return;
            }
            
            if (frm.doc.finish_date_input && frm.doc.finish_date_input < open_date) {
              frappe.throw({
                title: 'ข้อผิดพลาด',
                message: `วันที่สิ้นสุดต้องไม่น้อยกว่า ${open_date}`
              });
              reject();
              return;
            }
          }

          // ดำเนินการ before_save logic เดิม
          console.log("before_save triggered");

          var hour = frm.doc.start_hour_input;
          var minute = frm.doc.start_minute_input;

          if (hour && minute) {
            var time_value = frm.doc.start_date_input + " " + hour + ":" + minute;
            frm.set_value("job_start_on", time_value);
          }

          hour = frm.doc.finish_hour_input;
          minute = frm.doc.finish_minute_input;

          if (hour && minute) {
            var time_value = frm.doc.finish_date_input + " " + hour + ":" + minute;
            frm.set_value("job_finish", time_value);
          }

          // validate วันที่เริ่มงานต้องน้อยกว่าวันที่สิ้นสุดงาน
          if (frm.doc.job_start_on > frm.doc.job_finish) {
            frappe.throw(__("Start date cannot be greater than Finish date"));
            reject();
            return;
          }

          if (frm.doc.start_date_input > frm.doc.finish_date_input) {
            frm.set_value("over_night", 1);
          }

          // เพิ่มการ refresh field ที่สำคัญ
          frm.refresh_field("job_start_on");
          frm.refresh_field("job_finish");
          frm.refresh_field("over_night");

          resolve();
        })
        .catch(err => {
          reject(err);
        });
    });
  },
  after_save: function (frm) {
    console.log("after_save triggered");

    // แสดงข้อความยืนยันการบันทึก
    frappe.show_alert(
      {
        message: __("Service Report saved successfully"),
        indicator: "green",
      },
      5
    );

    frm.refresh();
  },
  task(frm) {
    // get data from SMO Working Team where parent=task parenttype='SMO Task' and parentfield='team'
    frappe.call({
      method:
        "smartoffice.smart_office.doctype.smo_task.smo_task.fetch_task_data", // API ที่สร้างไว้
      args: {
        task: frm.doc.task, // ส่งค่า task ที่เลือกไปยัง API
      },
      callback: function (r) {
        if (r.message) {
          // ล้างข้อมูลใน child table ก่อน เพื่อให้ข้อมูลไม่ซ้ำ
          console.log(r.message);
          frm.clear_table("team");

          // วนลูปเพิ่มข้อมูลที่ได้จาก API ลงใน child table
          $.each(r.message, function (i, d) {
            // เพิ่มแถวใหม่ใน child table
            console.log(d.full_name);
            let row = frm.add_child("team");
            console.log("row", row);
            row.employee = d.employee;
            row.user = d.user; // แทนที่ด้วยฟิลด์จริงใน child table
            row.email = d.email; // แทนที่ด้วยฟิลด์จริงใน child table

            row.full_name = d.full_name; // แทนที่ด้วยฟิลด์จริงใน child table
            row.overlapping_job_on_date = d.overlapping_job_on_date;
            row.filter = d.filter;
          });

          // รีเฟรชหน้าจอเพื่อแสดงข้อมูลใน child table
          frm.refresh_field("team");
        }
      },
    });
  },
  task_date(frm) {
    frm.set_value("start_date_input", frm.doc.task_date);
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
    if (frm.doc.from_page) {
      $(".navbar").hide();
      $(".standard-actions").hide();
    }
  },
  start_date_input: function (frm) {
    frappe.db.get_single_value('Smart Office Setting', 'open_date')
      .then(open_date => {
        if (open_date && frm.doc.start_date_input && frm.doc.start_date_input < open_date) {
          frm.set_value('start_date_input', '');
          frappe.msgprint({
            title: 'ข้อผิดพลาด',
            indicator: 'red',
            message: `วันที่เริ่มต้นต้องไม่น้อยกว่า ${open_date}`
          });
          return;
        }

        if (frm.doc.start_date_input) {
          frm.set_value("finish_date_input", frm.doc.start_date_input);
          recalculateEndTime(frm);
        }
      });
  },
  start_hour_input: function (frm) {
    recalculateEndTime(frm);
  },
  start_minute_input: function (frm) {
    recalculateEndTime(frm);
  },
  duration: function (frm) {
    recalculateEndTime(frm);
  },
  finish_date_input: function (frm) {
    frappe.db.get_single_value('Smart Office Setting', 'open_date')
      .then(open_date => {
        if (open_date && frm.doc.finish_date_input && frm.doc.finish_date_input < open_date) {
          frm.set_value('finish_date_input', '');
          frappe.msgprint({
            title: 'ข้อผิดพลาด',
            indicator: 'red',
            message: `วันที่สิ้นสุดต้องไม่น้อยกว่า ${open_date}`
          });
          return;
        }

        calculateDurationFromEndTime(frm);
      });
  },
  finish_hour_input: function (frm) {
    calculateDurationFromEndTime(frm);
  },
  finish_minute_input: function (frm) {
    calculateDurationFromEndTime(frm);
  },
  onload(frm) {
    if (frm.doc.task_date) {
      frm.set_value("start_date_input", frm.doc.task_date);
    }
  },
});

// แยกฟังก์ชันคำนวณเวลาออกมาเพื่อเรียกใช้ซ้ำ
function recalculateEndTime(frm) {
  if (
    frm.doc.start_date_input &&
    frm.doc.start_hour_input &&
    frm.doc.start_minute_input &&
    frm.doc.duration
  ) {
    // แปลงเวลาเริ่มต้นเป็น Date object และตั้งค่า timezone เป็น UTC
    let startDateTime = new Date(frm.doc.start_date_input + "T00:00:00Z");
    startDateTime.setUTCHours(parseInt(frm.doc.start_hour_input));
    startDateTime.setUTCMinutes(parseInt(frm.doc.start_minute_input));

    // แปลงวินาทีเป็นชั่วโมงและนาที
    let durationHours = Math.floor(frm.doc.duration / 3600);
    let durationMinutes = Math.floor((frm.doc.duration % 3600) / 60);

    // คำนวณเวลาสิ้นสุดโดยเพิ่มจำนวนมิลลิวินาที
    let endDateTime = new Date(
      startDateTime.getTime() +
        durationHours * 60 * 60 * 1000 +
        durationMinutes * 60 * 1000
    );

    // แปลงวันที่เป็น YYYY-MM-DD format
    let endDate = endDateTime.toISOString().split("T")[0];
    frm.set_value("finish_date_input", endDate);

    // set ค่าชั่วโมงสิ้นสุด
    let endHour = endDateTime.getUTCHours().toString().padStart(2, "0");
    frm.set_value("finish_hour_input", endHour);

    // set ค่านาทีสิ้นสุด
    let endMinute = endDateTime.getUTCMinutes();
    let validMinutes = [0, 10, 20, 30, 40, 50];
    let closestMinute = validMinutes.reduce((prev, curr) => {
      return Math.abs(curr - endMinute) < Math.abs(prev - endMinute)
        ? curr
        : prev;
    });
    frm.set_value(
      "finish_minute_input",
      closestMinute.toString().padStart(2, "0")
    );

    // เช็คว่าเป็นการทำงานข้ามคืนหรือไม่
    if (startDateTime.getUTCDate() !== endDateTime.getUTCDate()) {
      frm.set_value("over_night", 1);
    } else {
      frm.set_value("over_night", 0);
    }
  }
}

// เพิ่มฟังก์ชันใหม่สำหรับคำนวณ duration จาก end time
function calculateDurationFromEndTime(frm) {
  if (
    frm.doc.start_date_input &&
    frm.doc.start_hour_input &&
    frm.doc.start_minute_input &&
    frm.doc.finish_date_input &&
    frm.doc.finish_hour_input &&
    frm.doc.finish_minute_input
  ) {
    // แปลงเวลาเริ่มต้นเป็น Date object
    let startDateTime = new Date(frm.doc.start_date_input + "T00:00:00Z");
    startDateTime.setUTCHours(parseInt(frm.doc.start_hour_input));
    startDateTime.setUTCMinutes(parseInt(frm.doc.start_minute_input));

    // แปลงเวลาสิ้นสุดเป็น Date object
    let endDateTime = new Date(frm.doc.finish_date_input + "T00:00:00Z");
    endDateTime.setUTCHours(parseInt(frm.doc.finish_hour_input));
    endDateTime.setUTCMinutes(parseInt(frm.doc.finish_minute_input));

    // คำนวณความต่างของเวลาเป็นวินาที
    let diffInSeconds = (endDateTime - startDateTime) / 1000;

    // ถ้าเวลาสิ้นสุดน้อยกว่าเวลาเริ่มต้น ให้แจ้งเตือน
    if (diffInSeconds < 0) {
      frappe.msgprint("End time cannot be earlier than start time");
      return;
    }

    // set ค่า duration
    frm.set_value("duration", diffInSeconds);

    // เช็คการทำงานข้ามคืน
    if (startDateTime.getUTCDate() !== endDateTime.getUTCDate()) {
      frm.set_value("over_night", 1);
    } else {
      frm.set_value("over_night", 0);
    }
  }
}

frappe.ui.form.on("SMO Working Team", {
  view_task(frm, cdt, cdn) {
    let row = locals[cdt][cdn];
    let url = `/app/smo-task/${row.filter}`;
    window.open(url);
  },
});
