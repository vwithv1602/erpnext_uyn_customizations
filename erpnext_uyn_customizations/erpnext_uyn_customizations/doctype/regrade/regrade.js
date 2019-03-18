// Copyright (c) 2018, vavcoders and contributors
// For license information, please see license.txt

frappe.ui.form.on('ReGrade', {
	refresh: function(frm, cdt, cdn) {
		frm.page.set_secondary_action(__("Regrade"), function() {
			var is_valid_grade = true;
			var is_valid_grade_err_msg = "";
			var d = locals[cdt][cdn];
			// cur_frm.toggle_display("grade_detail_hidden", 1);
			$.each(frm.doc.grade_detail_hidden, function(key,value){
				cur_frm.get_field("grade_detail_hidden").grid.grid_rows[0].remove();
				cur_frm.refresh_field("grade_detail_hidden");
			})
			$.each(frm.doc.grade_detail, function(key,value){
				frappe.call({
					method: "erpnext_uyn_customizations.erpnext_uyn_customizations.doctype.regrade.regrade.validate_grades",
					args: {
						"item_code":value.item_code,"grade":value.grade
						// regrade_items: frm.doc.grade_detail
					},
					async:false,
					callback: function(r) {
						// frm.get_field("rename_log").$wrapper.html(r.message.join("<br>"));
						if(r.message!="OK"){
							is_valid_grade = false
							is_valid_grade_err_msg = r.message
						}
					}
				});
				if(is_valid_grade){
					var idx = cur_frm.fields_dict['grade_detail_hidden'].grid.grid_rows.length
					var new_row = cur_frm.add_child("grade_detail_hidden")
					frappe.model.set_value(new_row.doctype, new_row.name)
					cur_frm.refresh_field("grade_detail_hidden");
					var grid_row = cur_frm.fields_dict['grade_detail_hidden'].grid.grid_rows_by_docname[new_row.name],
					field = frappe.utils.filter_dict(grid_row.docfields, {fieldname: "barcode"})[0];
					grid_row.grid.grid_rows[idx].doc.barcode = value.barcode;
					grid_row.grid.grid_rows[idx].doc.item_code = value.item_code;
					grid_row.grid.grid_rows[idx].doc.grade = value.grade;
					grid_row.grid.grid_rows[idx].doc.warehouse = value.warehouse;
					if(value.warehouse==undefined || value.warehouse==''){
						frappe.msgprint("Warehouse not found",  title="Error");
						var indicator_el = document.querySelector("div.modal-dialog div.modal-content div.modal-header div.row div.col-xs-7 span.indicator.blue");
						indicator_el.className = "indicator red";
						is_valid_grade = false;
					}
					if(value.grade==undefined || value.grade==''){
						frappe.msgprint("Grade not found",  title="Error");
						var indicator_el = document.querySelector("div.modal-dialog div.modal-content div.modal-header div.row div.col-xs-7 span.indicator.blue");
						indicator_el.className = "indicator red";
						is_valid_grade = false;
					}
					idx++;
					cur_frm.refresh_field("barcode");
					cur_frm.refresh_field("item_code");
					cur_frm.refresh_field("grade_detail_hidden");
				}				
			});
			if(!is_valid_grade){
				frappe.msgprint(is_valid_grade_err_msg,  title="Error");
				var indicator_el = document.querySelector("div.modal-dialog div.modal-content div.modal-header div.row div.col-xs-7 span.indicator.blue");
				indicator_el.className = "indicator red";
				// cur_frm.toggle_display("grade_detail_hidden", 0);
				return false;
			}
			cur_frm.save();
			setTimeout(function(){
				frappe.model.open_mapped_doc({
					method: "erpnext_uyn_customizations.erpnext_uyn_customizations.doctype.regrade.regrade.test_repack",
					frm: frm
				})
			},600)
			// frappe.call({
			// 	method: "erpnext_uyn_customizations.erpnext_uyn_customizations.doctype.regrade.regrade.test_repack",
			// 	args: {
			// 		frm:frm
			// 		// regrade_items: frm.doc.grade_detail
			// 	},
			// 	callback: function(r) {
			// 		// frm.get_field("rename_log").$wrapper.html(r.message.join("<br>"));
			// 		console.log(r)
			// 	}
			// });
			// cur_frm.toggle_display("grade_detail_hidden", 0);
		});
	},
	set_default_grade: function(frm){
		$.each(frm.doc.grade_detail, function(key, value){
			frappe.model.set_value(value.doctype, value.name, "grade", frm.doc.default_grade)
		});
	},
	set_default_warehouse: function(frm){
		$.each(frm.doc.grade_detail, function(key, value){
			frappe.model.set_value(value.doctype, value.name, "warehouse", frm.doc.default_warehouse)
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
					grid_row.grid.grid_rows[idx].doc.item_code = item_code;
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


