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

      if (window.opener && typeof window.opener.refresh_table === "function") {
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
      frm.set_df_property("section_approvers", "hidden", 0);
    } else {
      frm.set_df_property("doc_detail_section", "hidden", 1);
      frm.set_df_property("expense_items_section", "hidden", 1);
      frm.set_df_property("advance_info", "hidden", 1);
      frm.set_df_property("section_approvers", "hidden", 1);
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
        max-width: 1000px;
        margin: 0 auto;
        font-family: Arial, sans-serif;
      ">
        <!-- ส่วนข้อมูลลูกค้า -->
        <div style="
          background: white;
          border-radius: 8px;
          padding: 20px;
          margin-bottom: 20px;
          box-shadow: 0 1px 3px rgba(0,0,0,0.1);
        ">
          <h3 style="margin: 0 0 15px 0; color: #666;">Customer Information</h3>
          <div style="display: grid; grid-template-columns: repeat(2, 1fr); gap: 20px;">
            <div>
              <div style="margin-bottom: 12px;">
                <div style="color: #666; font-size: 0.9em;">Customer</div>
                <div style="font-weight: 500;">${
                  frm.doc.customer_name || "-"
                }</div>
              </div>
              <div style="margin-bottom: 12px;">
                <div style="color: #666; font-size: 0.9em;">Project</div>
                <div style="font-weight: 500;">${
                  frm.doc.project_name || "-"
                }</div>
              </div>
              <div>
                <div style="color: #666; font-size: 0.9em;">Service Date</div>
                <div style="font-weight: 500;">${
                  frappe.datetime.str_to_user(frm.doc.service_date) || "-"
                }</div>
              </div>
            </div>
            <div>
              <div style="margin-bottom: 12px;">
                <div style="color: #666; font-size: 0.9em;">Site</div>
                <div style="font-weight: 500;">${frm.doc.site_name || "-"}</div>
              </div>
              <div style="margin-bottom: 12px;">
                <div style="color: #666; font-size: 0.9em;">Project Code</div>
                <div style="font-weight: 500;">${
                  frm.doc.project_code || "-"
                }</div>
              </div>
            </div>
          </div>
        </div>

        <!-- ส่วนรายละเอียดการเบิก -->
        <div style="
          background: white;
          border-radius: 8px;
          padding: 20px;
          margin-bottom: 20px;
          box-shadow: 0 1px 3px rgba(0,0,0,0.1);
        ">
          <h3 style="margin: 0 0 15px 0; color: #666;">Advance Details</h3>
          <div style="display: grid; grid-template-columns: repeat(2, 1fr); gap: 20px;">
            <div>
              <div style="margin-bottom: 12px;">
                <div style="color: #666; font-size: 0.9em;">Reference Code Finance</div>
                <div style="font-weight: 500;">${
                  frm.doc.reference_code_finance || "-"
                }</div>
              </div>
            </div>
            <div>
              <div style="margin-bottom: 12px;">
                <div style="color: #666; font-size: 0.9em;">Reference Code Accounting</div>
                <div style="font-weight: 500;">${
                  frm.doc.reference_code_accounting || "-"
                }</div>
              </div>
            </div>
            <div>
              <div>
                <div style="color: #666; font-size: 0.9em;">Advance Amount</div>
                <div style="font-weight: 500;">${frappe.format(
                  frm.doc.advance_amount || 0,
                  { fieldtype: "Currency" }
                )}</div>
              </div>
            </div>
          </div>
        </div>

        <!-- ส่วนรายการค่าใช้จ่าย -->
        <div style="
          background: white;
          border-radius: 8px;
          padding: 20px;
          box-shadow: 0 1px 3px rgba(0,0,0,0.1);
        ">
          <h3 style="margin: 0 0 15px 0; color: #666;">Expense Items</h3>
          <table style="width: 100%; border-collapse: collapse;">
            <thead>
              <tr style="border-bottom: 1px solid #eee;">
                <th style="text-align: left; padding: 12px 8px; color: #666;">ITEM</th>
                <th style="text-align: left; padding: 12px 8px; color: #666;">RECEIPT DATE</th>
                <th style="text-align: right; padding: 12px 8px; color: #666;">AMOUNT</th>
                <th style="text-align: center; padding: 12px 8px; color: #666;">ATTACHMENT</th>
              </tr>
            </thead>
            <tbody>
    `;

    let total = 0;

    // สร้างแถวรายการ
    frm.doc.expense_item.forEach((item) => {
      total += item.total_cost || 0;
      html += `
        <tr style="border-bottom: 1px solid #eee;">
          <td style="padding: 12px 8px;">
            <div style="font-weight: 500;">${item.expense_type_name || ""}</div>
            <div style="color: #666; font-size: 0.9em; margin-top: 4px;">${
              item.description || ""
            }</div>
          </td>
          <td style="padding: 12px 8px;">
            ${frappe.datetime.str_to_user(item.receipt_date) || ""}
          </td>
          <td style="text-align: right; padding: 12px 8px;">
            ${frappe.format(item.total_cost, { fieldtype: "Currency" })}
          </td>
          <td style="text-align: center; padding: 12px 8px;">
            <!-- ส่วนแสดง attachment ถ้ามี -->
          </td>
        </tr>
      `;
    });

    // สรุปยอด
    html += `
            <tr style="border-top: 2px solid #eee; font-weight: 500;">
              <td colspan="2" style="padding: 12px 8px;">Total Expenses</td>
              <td style="text-align: right; padding: 12px 8px;">${frappe.format(
                total,
                { fieldtype: "Currency" }
              )}</td>
              <td></td>
            </tr>
            <tr style="font-weight: 500;">
              <td colspan="2" style="padding: 12px 8px;">Advance Amount</td>
              <td style="text-align: right; padding: 12px 8px;">${frappe.format(
                frm.doc.advance_amount || 0,
                { fieldtype: "Currency" }
              )}</td>
              <td></td>
            </tr>
            <tr style="font-weight: 500; color: ${
              total - (frm.doc.advance_amount || 0) > 0 ? "#d32f2f" : "#2e7d32"
            };">
              <td colspan="2" style="padding: 12px 8px;">Advance ${
                total - (frm.doc.advance_amount || 0) > 0
                  ? "Shortfall (Pay More)"
                  : "Surplus (Return)"
              }</td>
              <td style="text-align: right; padding: 12px 8px;">${frappe.format(
                Math.abs(total - (frm.doc.advance_amount || 0)),
                { fieldtype: "Currency" }
              )}</td>
              <td></td>
            </tr>
          </tbody>
        </table>
      </div>
    </div>
    `;

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

    // const attach_field =  frappe.meta.get_field(
    //   "SMO Expense Item",
    //   "attachment",
    //   frm.doc.name
    // );
    
		// attach_field.on_attach_click = function () {
		// 	attach_field.set_upload_options();
		// 	attach_field.upload_options.restrictions.allowed_file_types = [
		// 		"application/pdf",
		// 	];
		// 	attach_field.file_uploader = new frappe.ui.FileUploader(attach_field.upload_options);
		// };
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
