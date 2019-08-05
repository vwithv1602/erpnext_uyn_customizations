// Copyright (c) 2018, vavcoders and contributors
// For license information, please see license.txt

frappe.ui.form.on('Flipkart Settings', {
	refresh: function(frm) {
		if(!frm.doc.__islocal && frm.doc.enable_flipkart === 1){
            frm.add_custom_button(__('Sync Flipkart'), function() {
                frappe.msgprint("Reached here")
                frappe.call({
                    method:"erpnext_uyn_customizations.flipkart_api.sync_flipkart",
                })
            }).addClass("btn-primary");
        }
        frm.add_custom_button(__("Flipkart Log"), function(){
            frappe.set_route("List", "Flipkart Log");
        })
	}
});

