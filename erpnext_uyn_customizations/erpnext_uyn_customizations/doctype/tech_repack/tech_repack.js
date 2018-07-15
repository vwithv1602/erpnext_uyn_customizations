// Copyright (c) 2018, vavcoders and contributors
// For license information, please see license.txt

frappe.provide("erpnext.stock");

frappe.ui.form.on('Tech Repack', {
	refresh: function(frm) {
		frm.add_custom_button(__("Repack"), function() {
			// var excise = frappe.model.make_new_doc_and_get_name('Journal Entry');
			// excise = locals['Journal Entry'][excise];
			// excise.voucher_type = 'Excise Entry';
			// frappe.set_route('Form', 'Stock Entry', "New Stock Entry");
			frappe.model.open_mapped_doc({
				method: "erpnext_uyn_customizations.erpnext_uyn_customizations.doctype.tech_repack.tech_repack.make_repack",
				frm: frm
			})
		}, __("Make"));
	},
	barcode: function(frm){
		if(frm.doc.barcode){
			frappe.call({
				method: "erpnext.stock.get_item_details.get_item_code",
				args: {"barcode": frm.doc.barcode },
				callback: function(r) {
					if (!r.exe){
						frm.set_value("item", r.message);
						if(typeof r.message=='string'){
							frm.set_value("item", r.message);
						}else{
							frm.set_value("item", r.message.item_code);
							setTimeout(function(){
								frm.set_value("warehouse", r.message.warehouse);
							},600);
						} 
					}
				}
			});
		}
	}
});
var default_source_warehouse = ""
var default_target_warehouse = ""
switch(user){
	case 'vwithv1602@gmail.com':
		default_source_warehouse = default_target_warehouse = "Stores - Uyn";
	break;
	case 'visheshhanda@usedyetnew.com':
		default_source_warehouse = default_target_warehouse = "vishesh - Uyn";
	break;
	case 'ravindrakathare@gmail.com':
	case 'pankaj.paswan@gmail.com':
	case 'abhinani8596@gmail.com':
		default_source_warehouse = default_target_warehouse = "Tech Team - Uyn";
	break;
	case 'ayyanamanidiot@gmail.com':
		default_source_warehouse = default_target_warehouse = "Ready To Ship - Uyn";
	break;
}
frappe.ui.form.on('Tech Repack Items', {
	barcode: function(doc,cdt,cdn){
		var barcode_val = frappe.model.get_value(cdt, cdn, "barcode");
		if(barcode_val){
			frappe.call({
				method: "erpnext.stock.get_item_details.get_item_code",
				args: {"barcode": barcode_val },
				callback: function(r) {
					if (!r.exe){
						frappe.model.set_value(cdt, cdn, "item", r.message);
						if(typeof r.message=='string'){
							frappe.model.set_value(cdt, cdn, "item", r.message);
						}else{
							frappe.model.set_value(cdt, cdn, "item", r.message.item_code);
							setTimeout(function(){
								frappe.model.set_value(cdt, cdn, "warehouse", r.message.warehouse);
							},600);
						} 
					}
				}
			});
		}
	}
});
frappe.ui.form.on('Tech Repack Taken Items', {
	item_code: function(doc,cdt,cdn){
		frappe.model.set_value(cdt, cdn, "source_warehouse", default_source_warehouse);
	},
});
frappe.ui.form.on('Tech Repack Given Items', {
	item_code: function(doc,cdt,cdn){
		frappe.model.set_value(cdt, cdn, "target_warehouse", default_target_warehouse);
	},
});	

