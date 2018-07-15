// Copyright (c) 2018, vavcoders and contributors
// For license information, please see license.txt

frappe.provide("erpnext.stock");

frappe.ui.form.on('Tech Repack', {
	refresh: function(frm) {

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
