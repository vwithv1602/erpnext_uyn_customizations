// Copyright (c) 2016, Frappe Technologies Pvt. Ltd. and contributors
// For license information, please see license.txt

frappe.query_reports["Productivity Insights"] = {
	"filters": [
		{
			"fieldname":"company",
			"label": __("Company"),
			"fieldtype": "Link",
			"options": "Company",
			"default": frappe.defaults.get_user_default("Company")
		},
		{
			"fieldname":"selected_date",
			"label": __("Select Date"),
			"fieldtype": "Date"
		},
	],
	onload: function(report) {
		report.page.add_inner_button(__("Productivity Insights"), function() {
			var filters = report.get_values();
			frappe.set_route('query-report', 'Productivity Insights', {company: filters.company});
		});
	}
}



