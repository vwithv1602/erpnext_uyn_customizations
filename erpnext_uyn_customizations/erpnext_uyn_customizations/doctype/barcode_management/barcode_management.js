// Copyright (c) 2018, vavcoders and contributors
// For license information, please see license.txt

frappe.ui.form.on('Barcode Management', {
	refresh: function(frm) {

	},
	generate_barcodes: function(frm){
		frappe.call({
			method: "erpnext_uyn_customizations.erpnext_uyn_customizations.doctype.barcode_management.barcode_management.generate_barcodes",
			args: {
				barcodes: frm.doc.barcodes,
				file_name: "bulk"
			},
			async:false,
			callback: function(r) {
				window.open(r.message);
			}
		});
	}
});
