// Copyright (c) 2024, beansx and contributors
// For license information, please see license.txt

// frappe.ui.form.on("Smart Office Setting", {
// 	refresh(frm) {

// 	},
// });

frappe.ui.form.on("Smart Office Setting", {
	sync_project: function(frm) {
		frappe.call({
			method: 'smartoffice.api.setting.sync_project_from_vtiger',
			callback: function(r) {
				frappe.show_alert({
					message: __('Sync Project Started'),
					indicator: 'green'
				}, 5);
			}
		});
	},

	sync_customer: function(frm) {
		frappe.call({
			method: 'smartoffice.api.setting.sync_customer_from_vtiger',
			callback: function(r) {
				frappe.show_alert({
					message: __('Sync Customer Started'), 
					indicator: 'green'
				}, 5);
			}
		});
	},

	sync_opportunity: function(frm) {
		frappe.call({
			method: 'smartoffice.api.setting.sync_opportunity_from_vtiger',
			callback: function(r) {
				frappe.show_alert({
					message: __('Sync Opportunity Started'),
					indicator: 'green'
				}, 5);
			}
		});
	}
});
