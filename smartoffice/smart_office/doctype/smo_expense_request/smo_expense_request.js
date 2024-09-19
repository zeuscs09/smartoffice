// Copyright (c) 2024, beansx and contributors
// For license information, please see license.txt

frappe.ui.form.on("SMO Expense Request", {
  onload: function (frm) {
    // เมื่อเปิดฟอร์ม, ดึงข้อมูลจากฟิลด์ Text Editor (hidden) และแสดงในฟิลด์ HTML

    if (!frm.doc.request_by) frm.set_value("request_by", frappe.user.name);

    let currentYear = new Date().getFullYear();
    let lastYear = currentYear - 1;

    // เพิ่มตัวเลือกปีปัจจุบันและปีก่อนหน้าในฟิลด์ Select
    frm.set_df_property("year", "options", [currentYear, lastYear].join("\n"));

    // ตั้งค่าปีปัจจุบันเป็นค่าเริ่มต้น
    if (!frm.doc.year) frm.set_value("year", currentYear);

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
    if (!frm.doc.month) frm.set_value("month", fullMonthName);
  },
  refresh(frm) {
    if (frm.doc.expense_request_item) {
      let msg = [];

      $.each(frm.doc.expense_request_item, function (i, d) {
        msg.push(JSON.parse(d.object_data));
      });

      render_summary(msg, function (html) {
        $("[data-fieldname='html_data']").html(html);
      });

      // frm.set_df_property("html_data", "options", html);
    }
  },
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
        request_by: frappe.user.name,
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
            row.object_data = JSON.stringify(d);
            total += d.total_cost;
          });

          // รีเฟรชหน้าจอเพื่อแสดงข้อมูลใน child table
          frm.refresh_field("expense_request_item");
          frm.set_value("total", total);

          
          render_summary(r.message, function (html) {
            $("[data-fieldname='html_data']").html(html);
          });
          frappe.dom.unfreeze();
        }
      },
    });
  },
});

function render_summary(data, callback) {
  get_expense_type(function (expenseTypes) {
    // กำหนดรายการประเภทค่าใช้จ่ายและลำดับคอลัมน์

    // จัดกลุ่มข้อมูลตาม expense_entry_id
    let groupedData = data.reduce((acc, cur) => {
      if (!acc[cur.expense_entry_id]) {
        acc[cur.expense_entry_id] = {
          expense_entry_id: cur.expense_entry_id,
          service_date: cur.service_date ? new Date(cur.service_date) : null,
          customer_name: cur.customer_name || "",
          project_name: cur.project_name || "",
          receipt_date: cur.receipt_date ? new Date(cur.receipt_date) : null,
          paid_by: cur.paid_by || "",
          expense_types: {}, // เก็บค่าใช้จ่ายแต่ละประเภท
        };
      }

      // สะสมค่าใช้จ่ายแต่ละประเภท
      if (!acc[cur.expense_entry_id].expense_types[cur.expense_type_desc]) {
        acc[cur.expense_entry_id].expense_types[cur.expense_type_desc] = 0;
      }
      acc[cur.expense_entry_id].expense_types[cur.expense_type_desc] +=
        cur.total_cost;

      return acc;
    }, {});

    // แปลง groupedData เป็น array และจัดเรียงตาม service_date
    let groupedArray = Object.values(groupedData).sort((a, b) => {
      if (a.service_date && b.service_date) {
        return a.service_date - b.service_date;
      } else if (a.service_date) {
        return -1;
      } else if (b.service_date) {
        return 1;
      } else {
        return 0;
      }
    });

    // เริ่มต้นสร้าง HTML สำหรับตารางโดยใช้ Bootstrap
    let html = `
    <table class="table table-bordered table-striped">
      <thead class="thead-dark">
        <tr>
          <th>Service Date</th>
          <th>Customer</th>
          <th>Project</th>
          <th>Receipt Date</th>
          ${expenseTypes.map((type) => `<th>${type.desc}</th>`).join("")}
          <th>Total</th>
        </tr>
      </thead>
      <tbody>
  `;
    console.log(html);
    // ตัวแปรสำหรับเก็บผลรวมของแต่ละประเภท
    let grandTotals = expenseTypes.reduce((acc, type) => {
      acc[type.desc] = 0;
      return acc;
    }, {});
    let grandTotalOverall = 0;

    groupedArray.forEach((group) => {
      // คำนวณ total สำหรับแต่ละแถว
      const total = expenseTypes.reduce((sum, type) => {
        const cost = group.expense_types[type.desc] || 0;
        // เพิ่มค่าใช้จ่ายลงใน grandTotals
        grandTotals[type.desc] += cost;
        return sum + cost;
      }, 0);
      grandTotalOverall += total;

      html += `
      <tr>
        <td>${group.service_date ? formatDate(group.service_date) : ""}</td>
        <td>${group.customer_name}</td>
        <td>${group.project_name}</td>
        <td>${group.receipt_date ? formatDate(group.receipt_date) : ""}</td>
        ${expenseTypes
          .map((type) => {
            const cost = group.expense_types[type.desc] || 0;
            return `<td>${cost.toLocaleString()}</td>`;
          })
          .join("")}
        <td>${total.toLocaleString()}</td>
      </tr>
    `;
    });

    // เพิ่มแถว Grand Total
    html += `
      </tbody>
      <tfoot>
        <tr>
          <th colspan="4">Grand Total</th>
          ${expenseTypes
            .map(
              (type) => `<th>${grandTotals[type.desc].toLocaleString()}</th>`
            )
            .join("")}
          <th>${grandTotalOverall.toLocaleString()}</th>
        </tr>
      </tfoot>
    </table>
  `;

    // คืนค่า HTML string
    return callback(html);
  });
}

function get_expense_type(callback) {
  frappe.db
    .get_list("SMO Expense Type", {
      fields: ["name", "description"],
    })
    .then((records) => {
      let expenseType = records.map((record) => {
        return {
          code: record.name,
          desc: record.description,
        };
      });

      callback(expenseType);
    })
    .catch((err) => {
      console.error(err);
    });
}

function formatDate(date) {
  const d = new Date(date);
  const year = d.getFullYear();
  const month = String(d.getMonth() + 1).padStart(2, "0");
  const day = String(d.getDate()).padStart(2, "0");
  return `${year}-${month}-${day}`;
}
