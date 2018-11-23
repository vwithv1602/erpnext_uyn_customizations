// Copyright (c) 2018, vavcoders and contributors
// For license information, please see license.txt

frappe.ui.form.on('ReGrade', {
	refresh: function(frm) {

	},
	set_default_grade: function(frm){
		$.each(frm.doc.grade_detail, function(key, value){
			frappe.model.set_value(value.doctype, value.name, "grade", frm.doc.default_grade)
		});
	},
	barcode: function(frm, cdt, cdn){
		var d = locals[cdt][cdn];
		barcode = frm.doc.barcode;
		is_exists = false;
		$.each(frm.doc.grade_detail, function(key, value){
			var existing_barcode = frappe.model.get_value("barcode")
			if(value.barcode==barcode){
				is_exists = true;
				frm.set_value("barcode", "");
				$("[data-fieldname=barcode]").focus();
			}
				
		});
		if(barcode!="" && !is_exists){
			frappe.call({
				method: "erpnext.stock.get_item_details.get_item_code",
				args: {"barcode": d.barcode },
				async:false,
				callback: function(r) {
					if(typeof r.message=='string'){
						var item_code = r.message;
					}else{
						var item_code = r.message.item_code;
					} 
					var idx = cur_frm.fields_dict['grade_detail'].grid.grid_rows.length
					var new_row = cur_frm.add_child("grade_detail")
					frappe.model.set_value(new_row.doctype, new_row.name)
					cur_frm.refresh_field("grade_detail");
					var grid_row = cur_frm.fields_dict['grade_detail'].grid.grid_rows_by_docname[new_row.name],
					field = frappe.utils.filter_dict(grid_row.docfields, {fieldname: "barcode"})[0];
					grid_row.grid.grid_rows[idx].doc.barcode = barcode;
					grid_row.grid.grid_rows[idx].doc.item = item_code;
					if(d.default_grade!=''){
						grid_row.grid.grid_rows[idx].doc.grade = d.default_grade;
					}
					idx++;
					cur_frm.refresh_field("barcode");
					cur_frm.refresh_field("grade_detail");
					frm.set_value("barcode", "");
					$("[data-fieldname=barcode]").focus();
				}
			});
			
		}
	},
});

