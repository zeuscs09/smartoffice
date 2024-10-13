// Copyright (c) 2024, beansx and contributors
// For license information, please see license.txt

frappe.ui.form.on("SMO Task", {
  refresh(frm) {
    if (
      frm.doc.status === "Completed" ||
      frm.doc.status === "Cancel" ||
      frm.doc.status === "In Review"
    ) {
      // Disable all fields
      frm.disable_form();
    }
  },
  
  start_date(frm) {
    if (!frm.doc.finish_date) {
      frm.set_value('finish_date', frm.doc.start_date);
    }
  },
  
  period: function(frm) {
    const periodTimes = {
      "AM": ["08:30:00", "12:00:00"],
      "PM": ["13:00:00", "18:00:00"],
      "After working hours": ["18:00:00", "23:59:59"],
      "default": ["00:00:00", "23:59:59"]
    };
    
    const [start_time, to_time] = periodTimes[frm.doc.period] || periodTimes.default;
    frm.set_value("start_time", start_time);
    frm.set_value("to_time", to_time);
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
  
  job_type(frm) {
    const prefix = `[${frm.doc.job_type}]`;
    const task_name = frm.doc.task_name || "";
    
    if (!task_name.startsWith(prefix)) {
      frm.set_value("task_name", `${prefix} ${task_name.trim()}`);
    }
  },
});

frappe.ui.form.on("SMO Working Team", {
  user(frm, cdt, cdn) {
    const row = locals[cdt][cdn];
    if (row.user) {
      frappe.dom.freeze("กำลังโหลดข้อมูล");
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
