// Copyright (c) 2024, beansx and contributors
// For license information, please see license.txt

frappe.ui.form.on("SMO Expense Request", {
  onload: function (frm) {
    // เมื่อเปิดฟอร์ม, ดึงข้อมูลจากฟิลด์ Text Editor (hidden) และแสดงในฟิลด์ HTML

    $("[data-fieldname=html_data]").html("");

    if (frm.doc.data_for_preview) {
      // ฟิลด์ hidden
      // $("[data-fieldname=html_data]").html(frm.doc.data_for_preview);
      // frm.set_df_property("html_data", "options", frm.doc.data_for_preview);
    }
    frm.set_value("request_by", frappe.user.name);

    let currentYear = new Date().getFullYear();
    let lastYear = currentYear - 1;

    // เพิ่มตัวเลือกปีปัจจุบันและปีก่อนหน้าในฟิลด์ Select
    frm.set_df_property("year", "options", [currentYear, lastYear].join("\n"));

    // ตั้งค่าปีปัจจุบันเป็นค่าเริ่มต้น
    frm.set_value("year", currentYear);

    const monthNames = [
      "January",
      "February",
      "March",
      "April",
      "May",
      "June",
      "July",
      "August",
      "September",
      "October",
      "November",
      "December",
    ];

    // ดึงเดือนปัจจุบัน
    const currentMonth = new Date().getMonth(); // ดึง index ของเดือน (เริ่มจาก 0)
    const fullMonthName = monthNames[currentMonth]; // ชื่อเดือนเต็ม

    // ตั้งค่าเดือนปัจจุบันในฟิลด์ (สมมติว่าเป็นฟิลด์ชื่อ 'month')
    frm.set_value("month", fullMonthName);
  },
  refresh(frm) {},
  get_data: function (frm) {
    if (!frm.doc.request_by) {
      frappe.throw("Please select Request By");

      return false;
    }

    frappe.dom.freeze("Load Data");

    frappe.call({
      method: "smartoffice.api.expense.get_expense_entries", // API ที่สร้างไว้
      args: {
        month: 9,
        year: 2024,
        request_by:frappe.user.name
      },
      callback: function (r) {
        if (r.message) {
          console.log(r.message);
          // เรียกฟังก์ชันเพื่อแสดงผลลัพธ์ใน HTML field
          frm.clear_table("expense_request_item");
          let total = 0;
          // วนลูปเพิ่มข้อมูลที่ได้จาก API ลงใน child table
          $.each(r.message, function (i, d) {
            // เพิ่มแถวใหม่ใน child table

            let row = frm.add_child("expense_request_item");

            row.expense = d.expense_entry_id; // แทนที่ด้วยฟิลด์จริงใน child table
            row.expense_item = d.expense_item; // แทนที่ด้วยฟิลด์จริงใน child table
            total += d.total_cost;
          });

          // รีเฟรชหน้าจอเพื่อแสดงข้อมูลใน child table
          frm.refresh_field("expense_request_item");
          frm.set_value("total", total);

          let html = render_summary(r.message);
          frm.set_df_property("html_data", "options", html);
          frm.set_value("data_for_preview", html);
          $(".expense-group").click(function () {
            $(this).find(".expense-details").toggle();
          });
          frappe.dom.unfreeze();
        }
      },
    });
  },
});

frappe.ui.form.on("SMO Expense Request", {
  onload: function (frm) {
    // เมื่อเปิดฟอร์ม, ดึงข้อมูลจากฟิลด์ Text Editor (hidden) และแสดงในฟิลด์ HTML

    $("[data-fieldname=html_data]").html("");

    if (frm.doc.data_for_preview) {
      // ฟิลด์ hidden

      frm.set_df_property("html_data", "options", frm.doc.data_for_preview);
    }

    let currentYear = new Date().getFullYear();
    let lastYear = currentYear - 1;

    // เพิ่มตัวเลือกปีปัจจุบันและปีก่อนหน้าในฟิลด์ Select
    frm.set_df_property("year", "options", [currentYear, lastYear].join("\n"));

    // ตั้งค่าปีปัจจุบันเป็นค่าเริ่มต้น
    frm.set_value("year", currentYear);

    const monthNames = [
      "January",
      "February",
      "March",
      "April",
      "May",
      "June",
      "July",
      "August",
      "September",
      "October",
      "November",
      "December",
    ];

    // ดึงเดือนปัจจุบัน
    const currentMonth = new Date().getMonth(); // ดึง index ของเดือน (เริ่มจาก 0)
    const fullMonthName = monthNames[currentMonth]; // ชื่อเดือนเต็ม

    // ตั้งค่าเดือนปัจจุบันในฟิลด์ (สมมติว่าเป็นฟิลด์ชื่อ 'month')
    frm.set_value("month", fullMonthName);
  },
});
function render_summary(data) {
  // จัดกลุ่มข้อมูลตาม expense_type_desc
  let groupedData = data.reduce((acc, cur) => {
    if (!acc[cur.expense_type_desc]) {
      acc[cur.expense_type_desc] = {
        total_cost: 0,
        entries: [],
      };
    }
    acc[cur.expense_type_desc].total_cost += cur.total_cost;
    acc[cur.expense_type_desc].entries.push(cur);
    return acc;
  }, {});

  // เริ่มต้นสร้าง HTML ที่จะแสดงผลโดยใช้ Card ของ Bootstrap 4/5
  let html = '<div style="margin-bottom: 20px;">';

  Object.keys(groupedData).forEach((expenseType) => {
    let group = groupedData[expenseType];
    html += `
        <div class="card mt-3">
          <div class="card-header bg-primary text-white expense-group" style="cursor: pointer;">
            <strong>${expenseType}:</strong> ${group.total_cost.toLocaleString()} THB
          </div>
          <div class="card-body expense-details" >
            <div class="row">
              ${group.entries
                .map(
                  (entry) => `
                  <div class="col-md-4">
                    <div class="card" style="border: 1px solid #ddd; padding: 10px; box-shadow: 0 2px 5px rgba(0,0,0,0.1);">
                      <p><strong>Customer:</strong> ${entry.customer_name}${
                    entry.system_reminder
                      ? ` <span class="badge badge-danger"> (${entry.system_reminder})</span>`
                      : ""
                  } </p>
                      <p><strong>Project:</strong> ${entry.project_name}</p>
                      <p><strong>Total Cost:</strong> ${entry.total_cost.toLocaleString()} THB <span> (${entry.paid_by.toLocaleString()}) </span></p>
                       <p><strong>Receipt Date:</strong> ${entry.receipt_date.toLocaleString()} </p>
                    </div>
                  </div>
                `
                )
                .join("")}
            </div>
          </div>
        </div>
      `;
  });

  html += "</div>";

  // Return the HTML string
  return html;
}

// เรียกใช้หลังจากที่ HTML ถูกสร้างแล้ว เพื่อให้ toggle ทำงานได้
$(document).on("click", ".expense-group", function () {
  $(this).next(".expense-details").toggle();
});

// $(".layout-side-section").hide();