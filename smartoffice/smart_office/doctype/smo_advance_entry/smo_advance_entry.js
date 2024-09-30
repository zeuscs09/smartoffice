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
    frm.toggle_display("summary_tab", true);
    frappe.dom.freeze("Loading...");
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
    row.ref_code = frm.get_field("reference_code").value;

    row.paid_by = "เงินทดรอง";
    var df = frappe.meta.get_docfield(
      "SMO Expense Item",
      "paid_by",
      cur_frm.doc.name
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
    if (row.expense_type == "EP004") {
      row.total_cost = cur_frm.doc.ot_rate;
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
