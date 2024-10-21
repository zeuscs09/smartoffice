// Copyright (c) 2024, beansx and contributors
// For license information, please see license.txt

frappe.ui.form.on("SMO Expense Entry", {
  onload(frm) {
  
   
   
    frm.set_query("input_expense_types", "expense_item", function (doc, cdt, cdn) {
        console.log(frm.customer);
        return {
          filters: {
            for_expense:1
          },
        };
      });
  },
  refresh(frm) {
    if(frappe.utils.get_query_params().from){
      frappe.breadcrumbs.add("");
    }
    frm.add_custom_button(__('Back'), function() {
      
      history.back();
    });

    frappe.call({
      method: "smartoffice.api.setting.get_taxi", // API ที่สร้างไว้
      args: {},
      callback: function (r) {

        if (r.message) {
          let config = r.message;
          if (frm.doc.config_taxi_rate == 0) {
            frm.set_value("config_taxi_rate", config.taxi_rate);
          }
          if (frm.doc.config_taxi_init == 0) {
            frm.set_value("config_taxi_init", config.taxi_start);
          }
          if (frm.doc.over_night_rate == 0) {
            frm.set_value("over_night_rate", config.over_night_rate);
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
});

frappe.ui.form.on("SMO Expense Item", {
  refresh(frm) {},
  expense_item_add: function (frm, cdt, cdn) {
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
    row.expense_type=row.input_expense_types;
  
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
    if (row.expense_type == "EP004") {
      row.total_cost = cur_frm.doc.ot_rate;
    }
    if (row.expense_type == "EP009") {
      row.total_cost = cur_frm.doc.over_night_rate;
      row.from_date=cur_frm.doc.service_date
      row.to_date=cur_frm.doc.finish_date
    }
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
