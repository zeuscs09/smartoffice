// Copyright (c) 2024, beansx and contributors
// For license information, please see license.txt

frappe.ui.form.on("SMO Task", {
  refresh(frm) {
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

    if(frappe.utils.get_query_params().action){
      frm.copy_doc();
    }
   
    const canGoBack = window.history.length > 1;
    if(frm.doc.from_page == "copy"){
      canGoBack = false;
    }
    
    if (
      frm.doc.status === "Completed" ||
      frm.doc.status === "Cancel" ||
      frm.doc.status === "In Review"
    ) {
      frm.disable_form();
    }
  },
  
  start_date: function(frm) {
    if(frm.doc.start_date) {
      frm.set_value("finish_date", frm.doc.start_date);
      recalculateEndTime(frm);
    }
  },
  customer_opportunity(frm) {
    frm.set_value("customer", frm.doc.customer_opportunity);
  },
  start_hour_input: function(frm) {
    recalculateEndTime(frm);
  },
  
  start_minute_input: function(frm) {
    recalculateEndTime(frm);
  },
  
  expected_time_use: function(frm) {
    recalculateEndTime(frm);
  },
  
  finish_date: function(frm) {
    calculateDurationFromEndTime(frm);
  },
  
  finish_hour_input: function(frm) {
    calculateDurationFromEndTime(frm);
  },
  
  finish_minute_input: function(frm) {
    calculateDurationFromEndTime(frm);
  },
  
  period: function(frm) {
    const periodTimes = {
      "All day": { hour: "08", minute: "30", toHour: "17", toMinute: "30" },
      "AM": { hour: "08", minute: "30", toHour: "12", toMinute: "00" },
      "PM": { hour: "13", minute: "00", toHour: "17", toMinute: "30" },
      "Not Specific": { hour: "00", minute: "00", toHour: "00", toMinute: "00" },
      "default": { hour: "08", minute: "30", toHour: "17", toMinute: "30" }
    };
    
    const times = periodTimes[frm.doc.period] || periodTimes.default;
    
    frm.set_value("start_hour_input", times.hour);
    frm.set_value("start_minute_input", times.minute);
    frm.set_value("finish_hour_input", times.toHour);
    frm.set_value("finish_minute_input", times.toMinute);
  },
  
  customer(frm) {
    frm.set_query("site", () => {
      return {
        filters: {
          customer: frm.doc.customer,
        },
      };
    });
  },
  job_group(frm) {
    frm.set_value("job_type", "");
    frm.set_query("job_type", () => {
      return {
        filters: {
          group: frm.doc.job_group,
        },
      };
    });

    console.log(frm.doc.job_group);
    
    frm.set_value("project", "");
    frm.set_value("opportunity", "");
    frm.set_value("customer", "");

  },
  
  // job_type(frm) {
  //   const prefix = `[${frm.doc.job_type}]`;
  //   const task_name = frm.doc.task_name || "";
    
  //   if (!task_name.startsWith(prefix)) {
  //     frm.set_value("task_name", `${prefix} ${task_name.trim()}`);
  //   }
  // },
  
  // เพิ่ม trigger สำหรับ location field
  location: function(frm) {
    // ซ่อนปุ่มที่มีอยู่ก่อน (ถ้ามี)
    frm.remove_custom_button('Save with Service Report');
    
    // แสดงปุ่มเฉพาะเมื่อเป็น On Site
    if (frm.doc.location === "On Site" && 
        (frm.doc.__islocal || (!frm.doc.docstatus && frm.doc.status === "Draft"))) {
      frm.add_custom_button(__("Save with Service Report"), function() {
        frappe.confirm(
          'คุณต้องการบันทึกและสร้าง Service Report หรือไม่?',
          function() {
           
            frm.save('Submit', function() {
              frappe.new_doc('SMO Service Report', {
                task: frm.doc.name,
                from_page: frm.doc.from_page,
                task_date: frm.doc.start_date,
              });
            });
          }
        );
      }).addClass('btn-primary');
    }
  },
});

function validateDates(frm) {
  if (frm.doc.start_date && frm.doc.finish_date) {
    if (frm.doc.start_date > frm.doc.finish_date) {
      frappe.msgprint({
        title: 'Error',
        indicator: 'red',
        message: 'Start date cannot be greater than end date'
      });
      frm.set_value('finish_date', '');
    }
  }
}

function recalculateEndTime(frm) {
  if (frm.doc.start_date && frm.doc.start_hour_input && 
      frm.doc.start_minute_input && frm.doc.expected_time_use) {
    
    let startDateTime = new Date(frm.doc.start_date + 'T00:00:00Z');
    startDateTime.setUTCHours(parseInt(frm.doc.start_hour_input));
    startDateTime.setUTCMinutes(parseInt(frm.doc.start_minute_input));

    let durationHours = Math.floor(frm.doc.expected_time_use / 3600);
    let durationMinutes = Math.floor((frm.doc.expected_time_use % 3600) / 60);
    
    let endDateTime = new Date(startDateTime.getTime() + 
      (durationHours * 60 * 60 * 1000) + 
      (durationMinutes * 60 * 1000));

    let endDate = endDateTime.toISOString().split('T')[0];
    frm.set_value('finish_date', endDate);

    let endHour = endDateTime.getUTCHours().toString().padStart(2, '0');
    frm.set_value('finish_hour_input', endHour);

    let endMinute = endDateTime.getUTCMinutes();
    let validMinutes = [0, 10, 20, 30, 40, 50];
    let closestMinute = validMinutes.reduce((prev, curr) => {
      return (Math.abs(curr - endMinute) < Math.abs(prev - endMinute) ? curr : prev);
    });
    frm.set_value('finish_minute_input', closestMinute.toString().padStart(2, '0'));
  }
}

function calculateDurationFromEndTime(frm) {
  if (frm.doc.start_date && frm.doc.start_hour_input && 
      frm.doc.start_minute_input && frm.doc.finish_date && 
      frm.doc.finish_hour_input && frm.doc.finish_minute_input) {
    
    let startDateTime = new Date(frm.doc.start_date + 'T00:00:00Z');
    startDateTime.setUTCHours(parseInt(frm.doc.start_hour_input));
    startDateTime.setUTCMinutes(parseInt(frm.doc.start_minute_input));

    let endDateTime = new Date(frm.doc.finish_date + 'T00:00:00Z');
    endDateTime.setUTCHours(parseInt(frm.doc.finish_hour_input));
    endDateTime.setUTCMinutes(parseInt(frm.doc.finish_minute_input));

    let diffInSeconds = (endDateTime - startDateTime) / 1000;
    
    if (diffInSeconds < 0) {
      frappe.msgprint('End time cannot be earlier than start time');
      return;
    }

    frm.set_value('expected_time_use', diffInSeconds);
  }
}

frappe.ui.form.on("SMO Working Team", {
  user(frm, cdt, cdn) {
    const row = locals[cdt][cdn];
    if (row.user) {
      frappe.dom.freeze("Loading data");
      frappe.call({
        method: "smartoffice.api.task.check_user_task",
        args: {
          user: row.user,
          activity_date: frm.doc.start_date,
        },
        callback: function(r) {
          if (r.message && r.message.length > 0) {
            row.overlapping_job_on_date = 1;
            row.filter = `?start_date=${frm.doc.start_date}&assign_to=["like","%${row.user}%"]`;
          } else {
            row.overlapping_job_on_date = 0;
            row.filter = "";
          }
          frm.refresh_field("user");
          frappe.dom.unfreeze();
        },
      });
    }
  },
  
  view_task(frm, cdt, cdn) {
    const row = locals[cdt][cdn];
    if (row.filter) {
      window.open(`/app/smo-task/${row.filter}`);
    }
  },
});
