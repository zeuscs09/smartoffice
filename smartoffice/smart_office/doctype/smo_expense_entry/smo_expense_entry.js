// Copyright (c) 2024, beansx and contributors
// For license information, please see license.txt

frappe.ui.form.on("SMO Expense Entry", {
  refresh(frm) {
    frappe.call({
      method: "smartoffice.api.setting.get_taxi_rate", // API ที่สร้างไว้
      args: {},
      callback: function (r) {
        if (r.message) {

          console.log(frm.doc.config_taxi_rate);
          if (frm.doc.config_taxi_rate == 0) {
            frm.set_value("config_taxi_rate", r.message);
          }
          // frm.set_value("config_taxi_rate", r.message);
        }
      },
    });
  },
  cal_total(frm) {
    console.log("cal_total");
    let total_amount = 0;

    if (frm.doc.expense_item) {
      frm.doc.expense_item.forEach((e) => {
        
        total_amount += e.total_cost||0;
      });
    }
    console.log(total_amount);
    frm.set_value("total_amount", total_amount);
  },
});

frappe.ui.form.on("SMO Expense Item", {
  refresh(frm) {},
  expense_item_add: function (frm, cdt, cdn) {
    let taxi_rate = frm.get_field("config_taxi_rate").value;

    // เข้าถึงแถวที่ถูกเพิ่ม (child row)
    let row = locals[cdt][cdn];

    // ตั้งค่าฟิลด์ใน child row ด้วยค่าเริ่มต้น
    row.rate_per_km = taxi_rate;

    // รีเฟรช Child Table เพื่อให้เห็นการเปลี่ยนแปลง
    frm.trigger("cal_total");
    frm.refresh_field("expense_item");
  },
  expense_item_remove: function (frm, cdt, cdn) {
    frm.trigger("cal_total");
  },
  expense_type: function (frm, cdt, cdn) {
    let row = locals[cdt][cdn];
    if ( row.rate_per_km == 0) {
      let taxi_rate = frm.get_field("config_taxi_rate").value;
      row.rate_per_km = taxi_rate;
    }
    if (row.expense_type == "EP001") {
      row.taxi_depart_distance = frm.get_field("distance_depart").value;
      row.total_cost = row.taxi_depart_distance * row.rate_per_km;
    }

    if (row.expense_type == "EP002") {
      row.taxi_return_distance = frm.get_field("distance_return").value;
      row.total_cost = row.taxi_return_distance * row.rate_per_km;
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
