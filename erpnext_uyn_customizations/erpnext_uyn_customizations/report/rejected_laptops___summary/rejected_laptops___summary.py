# Copyright (c) 2015, Frappe Technologies Pvt. Ltd. and Contributors
# License: GNU General Public License v3. See license.txt

from __future__ import unicode_literals
import frappe
from frappe.utils import flt
from frappe import msgprint, _
import operator
from erpnext_ebay.vlog import vwrite
class RejectedLaptopsSummary(object):
    def __init__(self, filters=None):
		from datetime import timedelta,datetime
		self.filters = frappe._dict(filters or {})
		if "selected_date" in self.filters:
			self.selected_date = self.filters.get("selected_date")
			self.selected_date_obj = datetime.strptime(self.selected_date, '%Y-%m-%d')
		else:
			yesterday = datetime.today() - timedelta(1)
			self.selected_date = yesterday.strftime('%Y-%m-%d')
			self.selected_date_obj = datetime.strptime(datetime.today().strftime('%Y-%m-%d'), '%Y-%m-%d')
    def run(self, args):
        data = self.get_data()
        max_len = 0
        for d in data:
            if d[0]:
                if len(d[0]) > max_len:
                    max_len = len(d[0])
        
        columns = self.get_columns(1)
        return columns, data

    def get_columns(self,max_len):
		if "selected_date" in self.filters:
			ydayortoday = "{0} - Rejects".format(self.selected_date)
		else:
			ydayortoday = "Yesterday - Rejects"
		"""return columns bab on filters"""
		columns = [
            _("Warehouse") + ":Data:150",
            _(ydayortoday) + ":Data:150",
            _("This Week - Rejects") + ":Data:150",
            _("This Month - Rejects") + ":Data:150",
        ]
		return columns
	

    def get_data(self):
		from datetime import timedelta,datetime
		def week_range(date):
			"""Find the first/last day of the week for the given day.
			Assuming weeks start on Sunday and end on Saturday.
			Returns a tuple of ``(start_date, end_date)``.
			"""
			# isocalendar calculates the year, week of the year, and day of the week.
			# dow is Mon = 1, Sat = 6, Sun = 7
			year, week, dow = date.isocalendar()
			# Find the first day of the week.
			if dow == 7:
				# Since we want to start with Sunday, let's test for that condition.
				start_date = date
			else:
				# Otherwise, subtract `dow` number days to get the first day
				start_date = date - timedelta(dow)
			# Now, add 6 for the last day of the week (i.e., count up to Saturday)
			end_date = start_date + timedelta(6)
			return (start_date.strftime('%Y-%m-%d'), end_date.strftime('%Y-%m-%d'))
		if "selected_date" in self.filters:
			# selected_year,selected_month,selected_day = self.filters.get("selected_date").split('-')
			weekstartdate = week_range(self.selected_date_obj)[0]
			weekenddate = week_range(self.selected_date_obj)[1]
		else:
			weekstartdate = week_range(datetime.today())[0]
			weekenddate = week_range(datetime.today())[1]

		def get_reject_data(warehouse,period):
			if period == 'yesterday':
				period_condition = " and se.posting_date='{0}'".format(self.selected_date)
			elif period == 'week':
				period_condition = " and se.posting_date>='{0}' and se.posting_date<='{1}'".format(weekstartdate,weekenddate)
			elif period == 'month':
				period_condition = " and MONTH(se.posting_date)=MONTH('{0}') and YEAR(se.posting_date)=YEAR('{0}')".format(self.selected_date)
			report_sql = """ 
			select count(se.name),max(qi.name) as qi_name,sed.item_code,se.rejected_reason,sed.serial_no,sed.s_warehouse,sed.t_warehouse,qi.inspected_by as inspected_by,se.owner as rejected_by from `tabStock Entry` se inner join `tabStock Entry Detail` sed on sed.parent=se.name inner join `tabQuality Inspection` qi on qi.barcode=sed.serial_no where se.is_rejected="Yes" {0} and se.docstatus=1 and 
			(
				(sed.t_warehouse='Tech Team - Uyn' and qi.inspection_type='In Process') or
				(sed.t_warehouse='incoming & Dis-assebly - Uyn' and qi.inspection_type='Incoming') or 
				(sed.t_warehouse='Chip Tech - Uyn' and qi.inspection_type='Chip Level In Process') or
				(sed.t_warehouse='Final QC & Packing - Uyn' and qi.inspection_type='Final QC')
			) and se.posting_date>qi.report_date and t_warehouse='{1}' group by qi.barcode order by sed.t_warehouse
			""".format(period_condition,warehouse)
			return frappe.db.sql(report_sql,as_dict=1)
		data = []
		warehouses = ['incoming & Dis-assebly - Uyn','Tech Team - Uyn','Chip Tech - Uyn','Final QC & Packing - Uyn']
		for warehouse in warehouses:
			daily_tech_rejects = get_reject_data(warehouse,'yesterday')
			weekly_tech_rejects = get_reject_data(warehouse,'week')
			monthly_tech_rejects = get_reject_data(warehouse,'month')
			data.append([warehouse,len(daily_tech_rejects),len(weekly_tech_rejects),len(monthly_tech_rejects)])
		# for report in custom_data:
		# 	data.append([report.get("name"),report.get("item_code"),report.get("rejected_reason"),report.get("serial_no"),report.get("s_warehouse"),report.get("t_warehouse"),report.get("inspected_by"),report.get("rejected_by")])
		return data
	
    
def execute(filters=None):
    args = {

    }
    return RejectedLaptopsSummary(filters).run(args)
