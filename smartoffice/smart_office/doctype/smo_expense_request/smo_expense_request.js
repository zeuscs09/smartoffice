// Copyright (c) 2024, beansx and contributors
// For license information, please see license.txt

frappe.ui.form.on("SMO Expense Request", {
	refresh(frm) {

	},
    get_data: function (frm) {
        frappe.dom.freeze("Load Data")
        frappe.dom.unfreeze();
        // alert("hello");
        // frappe.call({
        //     method: "smartoffice.api.setting.get_date",
        //     args: {},
        //     callback: function (r) {
        //         if (r.message) {
        //             frm.set_value("date", r.message);
        //         }
        //     },
        // });
    },
});
