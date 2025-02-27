// Copyright (c) 2025, beansx and contributors
// For license information, please see license.txt

// frappe.ui.form.on("SMO Timesheet", {
// 	refresh(frm) {

// 	},
// });

frappe.ui.form.on("SMO Timesheet", {
    onload: function(frm) {
        // รับปีและเดือนปัจจุบัน
        const currentDate = new Date();
        const currentYear = currentDate.getFullYear();
        const months = [
            'January', 'February', 'March', 'April',
            'May', 'June', 'July', 'August',
            'September', 'October', 'November', 'December'
        ];
        const currentMonth = months[currentDate.getMonth()];

        // สร้างตัวเลือกปีปัจจุบันและปีที่แล้ว
        const yearOptions = [currentYear, currentYear - 1].join('\n');
        
        // ตั้งค่าตัวเลือกปี
        frm.set_df_property('year', 'options', yearOptions);
        
        // ถ้าเป็นเอกสารใหม่
        if (frm.is_new()) {
            // ตั้งค่าเริ่มต้นเป็นปีปัจจุบัน
            frm.set_value('year', currentYear.toString());
            // ตั้งค่าเริ่มต้นเป็นเดือนปัจจุบัน
            frm.set_value('month', currentMonth);
            
            // ดึง Employee ID จาก User ที่ login
            frappe.call({
                method: 'frappe.client.get_value',
                args: {
                    doctype: 'Employee',
                    filters: { user_id: frappe.session.user },
                    fieldname: 'name'
                },
                callback: function(r) {
                    if (r.message && r.message.name) {
                        frm.set_value('employee', r.message.name);
                    }
                }
            });
        }
    },
    get_data: function(frm) {
        if (!frm.doc.employee || !frm.doc.year || !frm.doc.month) {
            frappe.msgprint('กรุณาระบุ Employee, Year และ Month');
            return;
        }
        
        frappe.call({
            method: 'smartoffice.smart_office.doctype.smo_timesheet.smo_timesheet.get_timesheets',
            args: {
                employee: frm.doc.employee,
                year: frm.doc.year,
                month: frm.doc.month
            },
            freeze: true,
            freeze_message: 'กำลังดึงข้อมูล...',
            callback: function(r) {
                if (r.message) {
                    // เคลียร์ข้อมูลเก่า
                    frm.clear_table('time_sheets');
                    
                    // เพิ่มข้อมูลใหม่
                    r.message.forEach(item => {
                        const row = frm.add_child('time_sheets');
                        row.from_time = item.from_time;
                        row.to_time = item.to_time;
                        row.working_hours = item.working_hours;
                        row.link_from_doc = item.link_from_doc;
                        row.doc_number = item.doc_number;
                        row.project_code = item.project_code;
                        row.customer = item.customer;
                        row.customer_name = item.customer_name;
                    });
                    
                    frm.refresh_field('time_sheets');
                    frappe.msgprint(`ดึงข้อมูลสำเร็จ: ${r.message.length} รายการ`);
                }
            }
        });
    }
});
