// Copyright (c) 2024, beansx and contributors
// For license information, please see license.txt

frappe.ui.form.on("SMO Advance Entry", {
  onload(frm) {
    frm.set_query(
      "input_expense_types",
      "expense_item",
      function (doc, cdt, cdn) {
        console.log(frm.customer);
        return {
          filters: {
            for_advance: 1,
          },
        };
      }
    );
  },
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
      if (frm.doc.workflow_state !== "Rejected") {
        frm.page.btn_secondary.hide();
      } else {
        frm.page.btn_secondary.show();
      }
    }
    // if (frappe.utils.get_query_params().from) {
    //   frappe.breadcrumbs.add("");
    //   $(".navbar").hide();
    //   $(".menu-btn-group").hide();
    //   $(".page-icon-group").hide();
    //   //$('.standard-actions').hide();
    //   // $('.next-doc').hide();
    // }
    // if (frm.doc.from_page) {
    //   frappe.breadcrumbs.add("");
    //   $(".navbar").hide();
    //   $(".menu-btn-group").hide();
    //   $(".page-icon-group").hide();
    // }

    // // เพิ่มการตรวจสอบว่าสามารถใช้ history.back() ได้หรือไม่
    // const canGoBack = window.history.length > 1;

    // frm.add_custom_button(__(canGoBack ? "Back" : "Close"), function () {
    //   if (canGoBack) {
    //     history.back();
    //   } else {
    //     // ดำเนินการเมื่อไม่สามารถย้อนกลับได้
    //     // ตัวอย่างเช่น ปิดหน้าต่างหรือนำทางไปยังหน้าหลัก
    //     window.close();
    //   }
    // });

    //เช็คสถานะจาก workflow_state
    if (frm.doc.workflow_state && frm.doc.workflow_state == "Draft") {
      frm.set_df_property("doc_detail_section", "hidden", 0);
      frm.set_df_property("expense_items_section", "hidden", 0);
      frm.set_df_property("advance_info", "hidden", 0);
    } else {
      frm.set_df_property("doc_detail_section", "hidden", 1);
      frm.set_df_property("expense_items_section", "hidden", 1);
      frm.set_df_property("advance_info", "hidden", 1);
      frm.events.update_html_summary(frm);
    }

    frappe.call({
      method: "smartoffice.api.setting.get_taxi", // API ที่สร้างไว้
      args: {},
      callback: function (r) {
        if (r.message) {
          let config = r.message;
          alert;
          if (frm.doc.config_taxi_rate == 0) {
            frm.set_value("config_taxi_rate", config.taxi_rate);
          }
          if (frm.doc.config_taxi_init == 0) {
            frm.set_value("config_taxi_init", config.taxi_start);
          }
          frappe.dom.unfreeze();
        }
      },
    });
  },
  cal_total(frm) {
    console.log("cal_total");
    let total_amount = 0;

    if (frm.doc.expense_item) {
      frm.doc.expense_item.forEach((e) => {
        total_amount += e.total_cost || 0;
      });
    }
    console.log(total_amount);
    frm.set_value("total_amount", total_amount);
  },
  customer(frm) {
    frm.set_query("customer_site", () => {
      return {
        filters: {
          customer: frm.doc.customer,
        },
      };
    });
    frm.set_query("project", () => {
      return {
        filters: {
          customer: frm.doc.customer,
        },
      };
    });
    frm.set_query("item_site", "expense_item", function (doc, cdt, cdn) {
      console.log(frm.customer);
      return {
        filters: {
          customer: frm.doc.customer,
        },
      };
    });
  },
  update_html_summary(frm) {
    let html = `
      <div style="
        max-width: 600px;
        margin: 0 auto;
        padding: 20px;
        background-color: #fff;
        box-shadow: 0 0 10px rgba(0,0,0,0.1);
        border-radius: 8px;
        font-family: Arial, sans-serif;
      ">
        <h2 style="text-align: center; margin-bottom: 20px;">สรุปรายการค่าใช้จ่าย</h2>
        
        <div style="margin-bottom: 20px; border: 1px solid #ddd; padding: 10px; border-radius: 5px;">
          <div style="display: grid; grid-template-columns: 1fr 1fr; gap: 10px;">
            <div>
              <p><strong>ลูกค้า:</strong> ${frm.doc.customer_name || "ไม่ระบุ"}</p>
              <p><strong>วันที่ให้บริการ:</strong> ${frappe.datetime.str_to_user(frm.doc.service_date) || "ไม่ระบุ"}</p>
              <p><strong>โครงการ:</strong> ${frm.doc.project_name || "ไม่ระบุ"}</p>
            </div>
            <div>
              <p><strong>เอกสารอ้างอิงเลขที่:</strong> ${frm.doc.reference_code_finance || "ไม่ระบุ"}</p>
              <p><strong>ยอดเบิก:</strong> ${new Intl.NumberFormat('th-TH', { 
                style: 'currency', 
                currency: 'THB'
              }).format(frm.doc.advance_amount || 0)}</p>
            </div>
          </div>
        </div>

        <table style="width: 100%; border-collapse: collapse;">
          <thead>
            <tr style="border-bottom: 2px solid #ddd;">
              <th style="text-align: left; padding: 10px;">รายการ</th>
              <th style="text-align: right; padding: 10px;">จำนวนเงิน</th>
            </tr>
          </thead>
          <tbody>
    `;

    let total = 0;

    // สร้าง HTML จาก child table
    frm.doc.expense_item.forEach((item) => {
      html += `
        <tr style="border-bottom: 1px solid #eee;">
          <td style="padding: 10px;">
            ${item.expense_type_name || ""}
            ${item.description ? `<br><small>${item.description}</small>` : ""}
            ${
              item.fuel_detail
                ? `<br><small>รายละเอียดน้ำมัน: ${item.fuel_detail}</small>`
                : ""
            }
            ${
              item.fuel_liter
                ? `<br><small>จำนวนลิตร: ${item.fuel_liter}</small>`
                : ""
            }
            ${
              item.hotel_name && item.total_day
                ? `<br><small>โรงแรม: ${item.hotel_name}  ${item.total_day} วัน</small>`
                : ""
            }
            ${
              item.taxi_depart_distance
                ? `<br><small>ระยะทางไป: ${item.taxi_depart_distance} กม.</small>`
                : ""
            }
            ${
              item.taxi_return_distance
                ? `<br><small>ระยะทางกลับ: ${item.taxi_return_distance} กม.</small>`
                : ""
            }
            ${
              item.receipt_date
                ? `<br><small>วันที่ใบเสร็จ: ${frappe.datetime.str_to_user(
                    item.receipt_date
                  )}</small>`
                : ""
            }
          </td>
          <td style="text-align: right; padding: 10px;">${frappe.format(
            item.total_cost,
            { fieldtype: "Currency" }
          )}</td>
        </tr>
      `;
      total += item.total_cost || 0;
    });

    // เพิ่มแถวรวม และ reject reason (ถ้ามี)
    html += `
          <tr style="border-top: 2px solid #ddd; font-weight: bold;">
            <td style="padding: 10px;">รวมทั้งหมด</td>
            <td style="text-align: right; padding: 10px;">${frappe.format(
              total,
              { fieldtype: "Currency" }
            )}</td>
          </tr>
        </tbody>
      </table>
      ${frm.doc.reject_reason ? `
        <div style="margin-top: 20px; padding: 10px; background-color: #fff3f3; border: 1px solid #ffcdd2; border-radius: 5px;">
          <p style="color: #d32f2f; margin: 0;"><strong>เหตุผลที่ปฏิเสธ:</strong> ${frm.doc.reject_reason}</p>
        </div>
      ` : ''}
    </div>
    `;

    // อัพเดท HTML field
    frm.set_df_property("html_summary", "options", html);
    frm.refresh_field("html_summary");
  },
  before_workflow_action: function (frm) {
    if (frm.selected_workflow_action === "Reject") {
      // ยกเลิก default action
      return new Promise(function (resolve, reject) {
        // This will cancel save
        // frappe.validated = false;
        // reject();

        // This will continue to save
        // var negative = 'frappe.validated = false';
        // resolve(negative);

        // If you comment all of it
        // Save button will be disabled (like it still processing)
        frappe.dom.unfreeze();
        frappe.prompt(
          [
            {
              label: "เหตุผลในการ Reject",
              fieldname: "reject_reason",
              fieldtype: "Small Text",
              reqd: 1,
            },
          ],
          function (values) {
            // // เมื่อได้เหตุผลแล้ว
            frm.set_value("reject_reason", values.reject_reason);

            // // ดำเนินการ workflow action ต่อ
            // frm.selected_workflow_action = "Reject";
            frm.save("Update", () => {
              var negative = "frappe.validated = false";
              resolve(negative);
            });

            // var negative = 'frappe.validated = false';
            // resolve(negative);
          },
          __("ระบุเหตุผลในการ Reject"),
          __("ยืนยัน")
        );
      });
    }
  },
});

frappe.ui.form.on("SMO Expense Item", {
  refresh(frm) {
    var df = frappe.meta.get_docfield(
      "SMO Expense Item",
      "paid_by",
      cur_frm.doc.name
    );
    df.hidden = 1;
  },

  expense_item_add: function (frm, cdt, cdn) {
    let cur_frm = frm;
    let taxi_rate = frm.get_field("config_taxi_rate").value;
    let taxi_initial = frm.get_field("config_taxi_init").value;
    // เข้าถึงแถวที่ถูกเพิ่ม (child row)
    let row = locals[cdt][cdn];
    row.receipt_date = frappe.datetime
      .get_datetime_as_string(frm.doc.service_date)
      .substr(0, 10);
    // ตั้งค่าฟิลด์ใน child row ด้วยค่าเริ่มต้น
    row.rate_per_km = taxi_rate;
    row.taxi_initial = taxi_initial;
    row.ref_code = frm.get_field("reference_code_finance").value;

    row.paid_by = "เงินทดรอง";
    var df = frappe.meta.get_docfield(
      "SMO Expense Item",
      "paid_by",
      frm.doc.name
    );
    df.hidden = 1;

    frm.trigger("cal_total");
    frm.refresh_field("expense_item");
  },
  expense_item_remove: function (frm, cdt, cdn) {
    frm.trigger("cal_total");
  },

  input_expense_types: function (frm, cdt, cdn) {
    let row = locals[cdt][cdn];
    row.expense_type = row.input_expense_types;

    if (row.rate_per_km == 0) {
      let taxi_rate = frm.get_field("config_taxi_rate").value;
      let taxi_initial = frm.get_field("config_taxi_init").value;
      row.rate_per_km = taxi_rate;
      row.taxi_initial = taxi_initial;
    }
    if (row.expense_type == "EP001") {
      row.taxi_depart_distance = frm.get_field("distance_depart").value;
      row.total_cost =
        row.taxi_initial + row.taxi_depart_distance * row.rate_per_km;
    }

    if (row.expense_type == "EP002") {
      row.taxi_return_distance = frm.get_field("distance_return").value;
      row.total_cost =
        row.taxi_initial + row.taxi_return_distance * row.rate_per_km;
    }
    var df = frappe.meta.get_docfield(
      "SMO Expense Item",
      "total_cost",
      frm.doc.name
    );
  

    // if (row.expense_type == "EP004") {
    //   df.toggle_editable("total_cost", 0);
    // } else {
    //   df.toggle_editable("total_cost", 1);
    // }
    
    frm.trigger("cal_total");
    frm.refresh_field("expense_item");
  },
  taxi_depart_distance: function (frm, cdt, cdn) {
    let row = locals[cdt][cdn];

    row.total_cost = row.taxi_depart_distance * row.rate_per_km;
    frm.trigger("cal_total");
    frm.refresh_field("expense_item");
  },
  taxi_return_distance: function (frm, cdt, cdn) {
    let row = locals[cdt][cdn];

    row.total_cost = row.taxi_return_distance * row.rate_per_km;
    frm.trigger("cal_total");
    frm.refresh_field("expense_item");
  },
  total_cost: function (frm, cdt, cdn) {
    frm.trigger("cal_total");
  },
});
