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

    if (frm.is_new()) {
      // ฟอร์มนี้เป็นฟอร์มใหม่และยังไม่เคยบันทึก
      // ดึงเดือนปัจจุบัน
      const currentMonth = new Date().getMonth(); // ดึง index ของเดือน (เริ่มจาก 0)
      const fullMonthName = monthNames[currentMonth]; // ชื่อเดือนเต็ม

      // ตั้งค่าเดือนปัจจุบันในฟิลด์ (สมมติว่าเป็นฟิลด์ชื่อ 'month')
      frm.set_value("month", fullMonthName);
      frm.set_value("year", currentYear);
    }
  },
  refresh(frm) {
    
    if(frappe.utils.get_query_params().from){
      $('.navbar').hide();
      $('.menu-btn-group').hide();
      $('.page-icon-group').hide();
      // $('.standard-actions').hide();
      // $('.next-doc').hide();
    }
    if(frm.doc.from_page) {
      
      $('.app-logo').hide();
      $("#navbar-search").hide();
      $("#navbar-breadcrumbs").hide();
      // $('.menu-btn-group').hide();
      //$('.page-icon-group').hide();
    }
    
    // เพิ่มการตรวจสอบว่าสามารถใช้ history.back() ได้หรือไม่
    const canGoBack = window.history.length > 1;
    
    frm.add_custom_button(__(canGoBack ? 'Back' : 'Close'), function() {
      if (canGoBack) {
        history.back();
      } else {
        // ดำเนินการเมื่อไม่สามารถย้อนกลับได้
        // ตัวอย่างเช่น ปิดหน้าต่างหรือนำทางไปยังหน้าหลัก
       window.close();
      }
    });
    
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
      frappe.throw("กรุณาเลือกผู้ขอเบิก");
      return false;
    }

    frappe.dom.freeze("กำลังโหลดข้อมูล");

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
      "December"
    ];

    frappe.call({
      method: "smartoffice.api.expense.get_expense_entries",
      args: {
        month: monthNames.indexOf(frm.doc.month) + 1, // แปลงชื่อเดือนเป็นตัวเลข (1-12)
        year: frm.doc.year,
        request_by: frm.doc.request_by,
      },
      callback: function (r) {
        if (r.message) {
          console.log(r.message);
          frm.clear_table("expense_request_item");
          let total = 0;
          let others = 0;
          let advance = 0;
          
          $.each(r.message, function (i, d) {
            let row = frm.add_child("expense_request_item");
            row.expense = d.expense_entry_id;
            row.expense_item = d.expense_item;
            row.object_data = JSON.stringify(d);
            total += d.total_cost;
       
            if (d.paid_by == "เงินทดรอง") advance += d.total_cost;
            else others += d.total_cost;
          });

          frm.refresh_field("expense_request_item");
          frm.set_value("total", total);
          frm.set_value("advance_payment", advance);
          frm.set_value("general_payment", others);

          render_summary(r.message, function (html) {
            $("[data-fieldname='html_data']").html(html);
          });
          frappe.dom.unfreeze();
        }
      },
      error: function(xhr, status, error) {
        frappe.dom.unfreeze();
        frappe.msgprint("เกิดข้อผิดพลาดในการโหลดข้อมูล: " + error);
      }
    });
  },
  before_workflow_action: function(frm) {
    if (frm.selected_workflow_action === "Reject") {
      frappe.validated = false;
      
      frappe.prompt([
        {
          label: 'เหตุผลในการ Reject',
          fieldname: 'reject_reason',
          fieldtype: 'Small Text',
          reqd: 1
        }
      ],
      function(values){
        // หาแถวของผู้อนุมัติปัจจุบัน
        let current_approver = frm.doc.approvers.find(a => a.user_id === frappe.session.user);
        if (current_approver) {
          current_approver.comment = values.reject_reason;
          current_approver.status = "Rejected";
          frm.refresh_field('approvers');
          console.log("current_approver",current_approver);
        }
        frm.doc.next_action = "";
        // บันทึกการเปลี่ยนแปลงก่อนที่จะดำเนินการ workflow
        frm.save('Update', () => {
          // หลังจากบันทึกสำเร็จ ดำเนินการ workflow ต่อ
          frm.selected_workflow_action = "Reject";
          //frm.workflow_action_dialog.hide();
          frm.save('Update', () => {
            frm.refresh();
            
          });
        });
      },
      'ระบุเหตุผลในการ Reject',
      'ยืนยัน'
      );
      
      return false;
    }
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
            return `<td style="text-align: right">${cost.toLocaleString()}</td>`;
          })
          .join("")}
        <td style="text-align: right">${total.toLocaleString()}</td>
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
              (type) => `<th style="text-align: right">${grandTotals[type.desc].toLocaleString()}</th>`
            )
            .join("")}
          <th style="text-align: right">${grandTotalOverall.toLocaleString()}</th>
        </tr>
      </tfoot>
    </table>
  `;
   
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

