// Copyright (c) 2018, vavcoders and contributors
// For license information, please see license.txt

frappe.ui.form.on('Spreadsheet Import', {
	refresh: function(frm) {

	},
	get_data: function(frm){
		spreadsheet_id = frm.doc.spreadsheet_id
		sheet_name = frm.doc.sheet_name
		if (spreadsheet_id==undefined || sheet_name==undefined){
			frappe.msgprint({
				message: "SpreadsheetID and SheetName are mandatory",
				indicator: 'red',
				title: __('Mandatory fields missing')
			});
		}else{
			frappe.call({
				method: "erpnext_uyn_customizations.client.get_spreadsheet_data",
				args: {
					spreadsheet_id: spreadsheet_id,
					sheet_name: sheet_name
				},
				async:false,
				callback: function(r) {
					frm.set_value("detailed_error", JSON.stringify(r.message))
					if(r.message.error){
						frm.set_value("error_message", r.message.error.message)
					}else{
						frm.set_value("error_message","")
						var idx = 0
						$.each(frm.doc.mapper, function(key, value){
							frm.doc.mapper.splice(frm.doc.mapper[0], 1)
							frm.refresh_field('mapper')
						});
						$.each(r.message[0], function(key, value) {
							if(key!=""){
								var new_row = cur_frm.add_child("mapper")
								frappe.model.set_value(new_row.doctype, new_row.name)
								cur_frm.refresh_field("mapper");
								var grid_row = cur_frm.fields_dict['mapper'].grid.grid_rows_by_docname[new_row.name],
								field = frappe.utils.filter_dict(grid_row.docfields, {fieldname: "column_name"})[0];
								grid_row.grid.grid_rows[idx].doc.column_name = key
								cur_frm.refresh_field("column_name");
								idx++;
							}
						});
						cur_frm.refresh_field('mapper');
					}
				}
			});
		}
	},
	set_defaults: function(frm){
		$.each(frm.doc.mapper, function(key, value){
			frappe.model.set_value(value.doctype, value.name, "primary_key", frm.doc.default_primary_key)
			frappe.model.set_value(value.doctype, value.name, "foreign_key", frm.doc.default_foreign_key)
			frappe.model.set_value(value.doctype, value.name, "target_doctype", frm.doc.default_target_doctype)
			frappe.model.set_value(value.doctype, value.name, "foreign_doctype", frm.doc.default_foreign_doctype)
		});
	},
	import: function(frm){
		console.log("frm sending error")
		console.log(frm)
		console.log(frm.doc)
		frappe.call({
			method: "erpnext_uyn_customizations.client.import_data",
			args: {
				doc: JSON.stringify(frm.doc)
			},
			async:false,
			callback: function(r) {
				frappe.msgprint({
					message: "Data successfully imported",
					indicator: 'green',
					title: __('Success')
				});
			}
		});
	}
});

