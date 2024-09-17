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
  period: function (frm) {
    // msgprint('Period');
    console.log(frm.doc.period);
    switch (frm.doc.period) {
      case "AM":
        frm.set_value("start_time", "08:30:00");
        frm.set_value("to_time", "12:00:00");
        break;
      case "PM":
        frm.set_value("start_time", "13:00:00");
        frm.set_value("to_time", "18:00:00");
        break;
      case "After working hours":
        frm.set_value("start_time", "18:00:00");
        frm.set_value("to_time", "23:59:59");
        break;
      default:
        frm.set_value("start_time", "00:00:00");
        frm.set_value("to_time", "23:59:59");
        break;
    }
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
    console.log(frm.doc.job_type);

    let prefix = "[" + frm.doc.job_type + "]";
    let task_name = frm.doc.task_name||"";

    // ตรวจสอบว่า task_name มี prefix อยู่หรือไม่
    if (!task_name.includes(prefix)) {
      // ถ้าไม่มี ให้ prepend prefix ลงใน task_name
      task_name = prefix + " " + task_name;
      frm.set_value("task_name", task_name);
    }
  },
});
