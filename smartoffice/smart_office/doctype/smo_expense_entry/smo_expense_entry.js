// Copyright (c) 2024, beansx and contributors
// For license information, please see license.txt

frappe.ui.form.on("SMO Expense Entry", {
  onload(frm) {
    frm.set_query(
      "input_expense_types",
      "expense_item",
      function (doc, cdt, cdn) {
        console.log(frm.customer);
        return {
          filters: {
            for_expense: 1,
          },
        };
      }
    );
  },
  refresh(frm) {
    if (frm.doc.from_page || frappe.utils.get_query_params().from_page) {
      // ตรวจสอบว่าผู้ใช้มีสิทธิ์ System Manager หรือไม่
      if (!frappe.user.has_role("System Manager")) {
        $(".navbar").css("visibility", "hidden");
        $(".menu-btn-group").hide();
        $(".page-icon-group").hide();
        if (frm.doc.workflow_state !== "Rejected") {
          frm.page.btn_secondary.hide();
        } else {
          frm.page.btn_secondary.show();
        }
      }

      if (window.opener && typeof window.opener.refresh_table === "function") {
        window.opener.refresh_table();
      }
      frm.add_custom_button(__("Close"), function () {
        window.close();
      });
    }
    // if(frappe.utils.get_query_params().from){
    //   $('.navbar').hide();
    //   $('.menu-btn-group').hide();
    //   $('.page-icon-group').hide();
    //   // $('.standard-actions').hide();
    //   // $('.next-doc').hide();
    // }
    // if(frm.doc.from_page) {
    //   frappe.breadcrumbs.add("");
    //   $('.navbar').hide();
    //   $('.menu-btn-group').hide();
    //   $('.page-icon-group').hide();
    // }

    // // เพิ่มการตรวจสอบว่าสามารถใช้ history.back() ได้หรือไม่
    // const canGoBack = window.history.length > 1;

    // frm.add_custom_button(__(canGoBack ? 'Back' : 'Close'), function() {
    //   if (canGoBack) {
    //     history.back();
    //   } else {
    //     // ดำเนินการเมื่อไม่สามารถย้อนกลับได้
    //     // ตัวอย่างเช่น ปิดหน้าต่างหรือนำทางไปยังหน้าหลัก
    //    window.close();
    //   }
    // });

    frappe.call({
      method: "smartoffice.api.setting.get_taxi", // API ที่สร้างไว้
      args: {},
      callback: function (r) {
        if (r.message) {
          let config = r.message;
          if (frm.doc.config_taxi_rate == 0) {
            frm.set_value("config_taxi_rate", config.taxi_rate);
            frm.refresh_field("config_taxi_rate");
          }
          if (frm.doc.config_taxi_init == 0) {
            frm.set_value("config_taxi_init", config.taxi_start);
            frm.refresh_field("config_taxi_init");
          }
          if (frm.doc.over_night_rate == 0) {
            frm.set_value("over_night_rate", config.over_night_rate);
            frm.refresh_field("over_night_rate");
          }
          // frm.set_value("config_taxi_rate", r.message);
        }
      },
    });

    frm.fields_dict["expense_item"].grid.get_field("expense_type").get_query =
      function (doc, cdt, cdn) {
        return {
          filters: {
            // เงื่อนไขในการกรองข้อมูล
            for_expense: 1,
          },
        };
      };

    // เพิ่มการเรียก API เพื่อดึง open_date
    frappe.db.get_single_value('Smart Office Setting', 'open_date')
      .then(open_date => {
        if (open_date) {
          // ตรวจสอบค่าปัจจุบันและแจ้งเตือนถ้าน้อยกว่า open_date
          if (frm.doc.service_date && frappe.datetime.str_to_obj(frm.doc.service_date) < frappe.datetime.str_to_obj(open_date)) {
            frm.set_value('service_date', '');
            frappe.msgprint({
              title: 'ข้อผิดพลาด',
              indicator: 'red',
              message: `วันที่ให้บริการต้องไม่น้อยกว่า ${open_date}`
            });
          }
          
          if (frm.doc.finish_date && frappe.datetime.str_to_obj(frm.doc.finish_date) < frappe.datetime.str_to_obj(open_date)) {
            frm.set_value('finish_date', '');
            frappe.msgprint({
              title: 'ข้อผิดพลาด',
              indicator: 'red',
              message: `วันที่สิ้นสุดต้องไม่น้อยกว่า ${open_date}`
            });
          }
        }
      });
  },
  cal_total(frm) {
    console.log("cal_total");
    let total_amount = 0;
    console.log(frm.doc.expense_item);
    if (frm.doc.expense_item) {
      frm.doc.expense_item.forEach((e) => {
        total_amount += e.total_cost || 0;
      });
    }
    console.log(total_amount);
    frm.set_value("total_amount", total_amount);
  },
  is_holiday(frm) {
    if (frm.doc.is_holiday && frm.doc.is_holiday == 1) {
      if (frm.doc.working_hour > 4 * 3600) {
        frm.set_value("ot_rate", 1000);
      } else {
        frm.set_value("ot_rate", 500);
      }
    } else {
      frm.set_value("ot_rate", 0);
    }
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
            // เมื่อได้เหตุผลแล้ว
            frm.set_value("reject_reason", values.reject_reason);
            frm.save("Update", () => {
              var negative = "frappe.validated = false";
              resolve(negative);
            });
            // ดำเนินการ workflow action ต่อ
            // frm.selected_workflow_action = "Reject";
            // //frm.save('Update');
            // console.log(frm.doc);

            // var negative = 'frappe.validated = false';
            // resolve(negative);
          },
          __("ระบุเหตุผลในการ Reject"),
          __("ยืนยัน")
        );
      });
    }
  },
  auto_expense(frm) {
    frm.clear_table("expense_item");
    
    // ตรวจสอบและกำหนดค่าเริ่มต้น
    let distance_depart = frm.get_field("distance_depart").value || 0;
    let distance_return = frm.get_field("distance_return").value || 0;
    let config_taxi_rate = frm.doc.config_taxi_rate || 0;
    let config_taxi_init = frm.doc.config_taxi_init || 0;
    
    // เพิ่มรายการค่าใช้จ่าย EP001
    let ep001 = frm.add_child("expense_item", {
      input_expense_types: "EP001",
      expense_type: "EP001",
      taxi_depart_distance: distance_depart,
      cal_taxi_depart_distance: distance_depart,
      rate_per_km: config_taxi_rate,
      taxi_initial: config_taxi_init,
      receipt_date: frm.doc.service_date,
    });
    ep001.total_cost = config_taxi_init + (distance_depart * config_taxi_rate);

    // เพิ่มรายการค่าใช้จ่าย EP002
    let ep002 = frm.add_child("expense_item", {
      input_expense_types: "EP002",
      expense_type: "EP002",
      taxi_return_distance: distance_return,
      cal_taxi_return_distance: distance_return,
      rate_per_km: config_taxi_rate,
      taxi_initial: config_taxi_init,
      receipt_date: frm.doc.service_date,
    });
    ep002.total_cost = config_taxi_init + (distance_return * config_taxi_rate);

    // เพิ่มรายการค่าใช้จ่าย EP004 ถ้า over_night เป็น true
    if (frm.doc.is_holiday) {
      let ep004 = frm.add_child("expense_item", {
        input_expense_types: "EP004",
        expense_type: "EP004",
        total_cost: frm.doc.ot_rate,
        receipt_date: frm.doc.service_date,
        from_date: frm.doc.service_date,
        to_date: frm.doc.finish_date,
      });
    }

    // รีเฟรชฟิลด์ expense_item เพื่อแสดงรายการที่เพิ่ม
    frm.refresh_field("expense_item");
    frm.trigger("cal_total");
  },
  before_save: function(frm) {
    return new Promise((resolve, reject) => {
      frappe.db.get_single_value('Smart Office Setting', 'open_date')
        .then(open_date => {
          if (open_date) {
            if (frm.doc.service_date && frappe.datetime.str_to_obj(frm.doc.service_date) < frappe.datetime.str_to_obj(open_date)) {
              frappe.throw({
                title: 'ข้อผิดพลาด',
                message: `วันที่ให้บริการต้องไม่น้อยกว่า ${open_date}`
              });
              reject();
              return;
            }
            
            if (frm.doc.finish_date && frappe.datetime.str_to_obj(frm.doc.finish_date) < frappe.datetime.str_to_obj(open_date)) {
              frappe.throw({
                title: 'ข้อผิดพลาด',
                message: `วันที่สิ้นสุดต้องไม่น้อยกว่า ${open_date}`
              });
              reject();
              return;
            }
          }

          // ... existing before_save logic ...
          resolve();
        })
        .catch(err => {
          reject(err);
        });
    });
  },
});

frappe.ui.form.on("SMO Expense Item", {
  refresh(frm) {},
  expense_item_add: function (frm, cdt, cdn) {
    let taxi_rate = frm.doc.config_taxi_rate;
    let taxi_initial = frm.doc.config_taxi_init;
    // เข้าถึงแถวที่ถูกเพิ่ม (child row)
    let row = locals[cdt][cdn];
    row.receipt_date = frappe.datetime
      .get_datetime_as_string(frm.doc.service_date)
      .substr(0, 10);
    // ตั้งค่าฟิลด์ใน child row ด้วยค่าเริ่มต้น
    row.rate_per_km = taxi_rate;
    row.taxi_initial = taxi_initial;
    // รีเฟรช Child Table เพื่อให้เห็นการเปลี่ยนแปลง
    // row.set_query("expense_type", () => {
    //   return {
    //     filters: {
    //       for_expense: 1,
    //     },
    //   };
    // });
    frm.trigger("cal_total");
    frm.refresh_field("expense_item");
  },
  expense_item_remove: function (frm, cdt, cdn) {
    frm.trigger("cal_total");
  },

  // expense_type: function (frm, cdt, cdn) {
  //   let row = locals[cdt][cdn];
  //   if (row.rate_per_km == 0) {
  //     let taxi_rate = frm.get_field("config_taxi_rate").value;
  //     let taxi_initial = frm.get_field("config_taxi_init").value;
  //     row.rate_per_km = taxi_rate;
  //     row.taxi_initial = taxi_initial;
  //   }
  //   if (row.expense_type == "EP001") {
  //     row.taxi_depart_distance = frm.get_field("distance_depart").value;
  //     row.total_cost =
  //       row.taxi_initial + row.taxi_depart_distance * row.rate_per_km;
  //   }

  //   if (row.expense_type == "EP002") {
  //     row.taxi_return_distance = frm.get_field("distance_return").value;
  //     row.total_cost =
  //       row.taxi_initial + row.taxi_return_distance * row.rate_per_km;
  //   }
  //   if (row.expense_type == "EP004") {
  //     row.total_cost = cur_frm.doc.ot_rate;
  //   }
  //   frm.trigger("cal_total");
  //   frm.refresh_field("expense_item");
  // },
  input_expense_types: function (frm, cdt, cdn) {
    let row = locals[cdt][cdn];
    row.expense_type = row.input_expense_types;

    if (row.rate_per_km == 0) {
      let taxi_rate = frm.doc.config_taxi_rate;
      let taxi_initial = frm.doc.config_taxi_init;
      row.rate_per_km = taxi_rate;
      row.taxi_initial = taxi_initial;
    }
    
    // ตรวจสอบและกำหนดค่าเริ่มต้นสำหรับการคำนวณ
    let taxi_initial = row.taxi_initial || 0;
    let rate_per_km = row.rate_per_km || 0;
    
    if (row.expense_type == "EP001") {
      row.taxi_depart_distance = frm.get_field("distance_depart").value;
      row.cal_taxi_depart_distance = frm.get_field("distance_depart").value;
      let taxi_depart_distance = row.taxi_depart_distance || 0;
      row.total_cost = taxi_initial + (taxi_depart_distance * rate_per_km);
    }

    if (row.expense_type == "EP002") {
      row.taxi_return_distance = frm.get_field("distance_return").value;
      row.cal_taxi_return_distance = frm.get_field("distance_return").value;
      let taxi_return_distance = row.taxi_return_distance || 0;
      row.total_cost = taxi_initial + (taxi_return_distance * rate_per_km);
    }
    if (row.expense_type == "EP004") {
      row.total_cost = frm.doc.ot_rate;
    }
    if (row.expense_type == "EP009") {
      row.total_cost = frm.doc.over_night_rate;
      row.from_date = frm.doc.service_date;
      row.to_date = frm.doc.finish_date;
    }
    frm.trigger("cal_total");
    frm.refresh_field("expense_item");
  },
  taxi_depart_distance: function (frm, cdt, cdn) {
    let row = locals[cdt][cdn];

    // ตรวจสอบและกำหนดค่าเริ่มต้นถ้าเป็น null หรือ undefined
    let taxi_initial = row.taxi_initial || 0;
    let taxi_depart_distance = row.taxi_depart_distance || 0;
    let rate_per_km = row.rate_per_km || 0;

    row.total_cost = taxi_initial + (taxi_depart_distance * rate_per_km);
    frm.trigger("cal_total");
    frm.refresh_field("expense_item");
  },
  taxi_return_distance: function (frm, cdt, cdn) {
    let row = locals[cdt][cdn];

    // ตรวจสอบและกำหนดค่าเริ่มต้นถ้าเป็น null หรือ undefined
    let taxi_initial = row.taxi_initial || 0;
    let taxi_return_distance = row.taxi_return_distance || 0;
    let rate_per_km = row.rate_per_km || 0;

    row.total_cost = taxi_initial + (taxi_return_distance * rate_per_km);
    frm.trigger("cal_total");
    frm.refresh_field("expense_item");
  },
  total_cost: function (frm, cdt, cdn) {
    frm.trigger("cal_total");
  },
  overnight_trip: function (frm, cdt, cdn) {
    let row = locals[cdt][cdn];
    if (row.overnight_trip == 1) {
      row.total_cost = frm.doc.over_night_rate;
    } else {
      row.total_cost = 0;
    }
    frm.trigger("cal_total");
    frm.refresh_field("expense_item");
  },
  
});
