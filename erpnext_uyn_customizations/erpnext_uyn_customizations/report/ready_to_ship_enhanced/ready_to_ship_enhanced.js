// Copyright (c) 2016, Frappe Technologies Pvt. Ltd. and contributors
// For license information, please see license.txt

frappe.query_reports["Ready To Ship Enhanced"] = {
	"filters": [
		// {
		// 	"fieldname":"company",
		// 	"label": __("Company"),
		// 	"fieldtype": "Link",
		// 	"options": "Company",
		// 	"default": frappe.defaults.get_user_default("Company")
		// },
		// {
		// 	"fieldname":"sales_type",
		// 	"label":__("Sales Type"),
		// 	"fieldtype":"Select",
		// 	"options":"" + NEWLINE + "GROSS" + NEWLINE + "CREDIT NOTES"
		// },
		{
			"fieldname":"group_by",
			"label":__("Group By"),
			"fieldtype":"Select",
			"options":"" + NEWLINE + "Variants",
			"default":"Variants"
		},
		{
			"fieldname":"item_group",
			"label":__("Item Group"),
			"fieldtype":"Link",
			"options":"Item Group",
			"default": "Laptops"
		},
		{
			"fieldname":"selected_date",
			"label":__("Date"),
			"fieldtype":"Date",
			"default":frappe.datetime.add_days(frappe.datetime.get_today(), -1)
		}
	],
	onload: function(report) {
		report.page.add_inner_button(__("Ready To Ship Enhanced"), function() {
			var filters = report.get_values();
			frappe.set_route('query-report', 'Ready To Ship Enhanced', {company: filters.company});
		});
	}
	// "formatter": function(row, cell, value, columnDef, dataContext, default_formatter) {
	// 	console.log('row:'+row)
	// 	console.log('cell:'+cell)
	// 	console.log('value:'+value)
	// 	console.log('columnDef:')
	// 	console.log(columnDef)
	// 	console.log('dataContext:'+dataContext)
	// 	console.log('default_formatter:'+default_formatter)
	// 	if(value=='Total'){
	// 		value = "<b>"+value+"</b>"
	// 		// value = value.wrap("<b></b>").parent().html();
	// 	}
	// 	// if (columnDef.df.fieldname=="account") {
	// 	// 	value = dataContext.account_name;

	// 	// 	columnDef.df.link_onclick =
	// 	// 		"erpnext.financial_statements.open_general_ledger(" + JSON.stringify(dataContext) + ")";
	// 	// 	columnDef.df.is_tree = true;
	// 	// }

	// 	// value = default_formatter(row, cell, value, columnDef, dataContext);

	// 	// if (!dataContext.parent_account) {
	// 	// 	var $value = $(value).css("font-weight", "bold");
	// 	// 	if (dataContext.warn_if_negative && dataContext[columnDef.df.fieldname] < 0) {
	// 	// 		$value.addClass("text-danger");
	// 	// 	}

	// 	// 	value = $value.wrap("<p></p>").parent().html();
	// 	// }

	// 	return value;
	// },
}


