// Copyright (c) 2016, vavcoders and contributors
// For license information, please see license.txt
/* eslint-disable */

frappe.query_reports["Operations Productivity Report"] = {
	"filters": [

	],
	"formatter":function (row, cell, value, columnDef, dataContext, default_formatter) {
		value = default_formatter(row, cell, value, columnDef, dataContext);
		if (columnDef.id == "Employee") {
			if(jQuery.inArray(dataContext.Employee, ['Incoming Team','Tech Team','Chip Team','Final QC Team']) !== -1){
				value = "<span style='font-weight:bold'>" + value + "</span>";
			}
		}

		return value;
	}
}
