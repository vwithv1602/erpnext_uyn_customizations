// Copyright (c) 2016, Frappe Technologies Pvt. Ltd. and contributors
// For license information, please see license.txt

frappe.query_reports["Detailed Supplier Payments"] = {
	"filters": [
		{
			"fieldname":"company",
			"label": __("Company"),
			"fieldtype": "Link",
			"options": "Company",
			"default": frappe.defaults.get_user_default("Company")
		},
		{
			"fieldname":"supplier",
			"label": __("Supplier"),
			"fieldtype": "Link",
			"options": "Supplier",
			"default": frappe.defaults.get_user_default("Supplier")
		},
	],
	onload: function(report) {
		report.page.add_inner_button(__("Detailed Supplier Payments"), function() {
			var filters = report.get_values();
			frappe.set_route('query-report', 'Detailed Supplier Payments', {company: filters.company});
		});
	}
}


