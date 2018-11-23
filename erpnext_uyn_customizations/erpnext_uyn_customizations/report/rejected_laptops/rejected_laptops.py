# Copyright (c) 2015, Frappe Technologies Pvt. Ltd. and Contributors
# License: GNU General Public License v3. See license.txt

from __future__ import unicode_literals
import frappe
from frappe.utils import flt
from frappe import msgprint, _
import operator
from erpnext_ebay.vlog import vwrite

class RejectedLaptops(object):
    def __init__(self, filters=None):
		self.filters = frappe._dict(filters or {})
		if "selected_date" in self.filters:
			self.selected_date = self.filters.get("selected_date")
			self.selected_date_obj = self.datetime.strptime(self.selected_date, '%Y-%m-%d')
		else:
			self.selected_date = self.datetime.today().strftime('%Y-%m-%d')
			self.selected_date_obj = self.datetime.strptime(self.datetime.today().strftime('%Y-%m-%d'), '%Y-%m-%d')
    def run(self, args):
        data = self.get_data()
        max_len = 0
        for d in data:
            if d[3]:
                if len(d[3]) > max_len:
                    max_len = len(d[3])
        
        columns = self.get_columns(max_len*5.66)
        return columns, data

    def get_columns(self,max_len):
        """return columns bab on filters"""
        columns = [
            _("STE") + ":Link/Stock Entry:80", 
            _("Item Code") + ":Data:350",
            _("Rejected Reason") + ":Data:310",
            _("Serial No") + ":Data:70",
            _("Source Warehouse") + ":Data:120",
            _("Target Warehouse") + ":Data:120",
            _("Inspected By") + ":Data:120",
            _("Rejected By") + ":Data:120"
        ]
        return columns

    from datetime import timedelta,datetime
    
    def get_data(self):
        data = []
        report_sql = """ 
        select se.name,max(qi.name) as qi_name,sed.item_code,se.rejected_reason,sed.serial_no,sed.s_warehouse,sed.t_warehouse,qi.inspected_by as inspected_by,se.owner as rejected_by from `tabStock Entry` se inner join `tabStock Entry Detail` sed on sed.parent=se.name inner join `tabQuality Inspection` qi on qi.barcode=sed.serial_no where se.is_rejected="Yes" and se.posting_date='{0}' and se.docstatus=1 and 
		(
			(sed.t_warehouse='Tech Team - Uyn' and qi.inspection_type='In Process') or
			(sed.t_warehouse='incoming & Dis-assebly - Uyn' and qi.inspection_type='Incoming') or 
			(sed.t_warehouse='Chip Tech - Uyn' and qi.inspection_type='Chip Level In Process') or
			(sed.t_warehouse='Final QC & Packing - Uyn' and qi.inspection_type='Final QC')
		) and se.posting_date>qi.report_date group by qi.barcode order by sed.t_warehouse
        """.format(self.selected_date)
        for report in frappe.db.sql(report_sql,as_dict=1):
            data.append([report.get("name"),report.get("item_code"),report.get("rejected_reason"),report.get("serial_no"),report.get("s_warehouse"),report.get("t_warehouse"),report.get("inspected_by"),report.get("rejected_by")])
        return data
    
def execute(filters=None):
    args = {

    }
    return RejectedLaptops(filters).run(args)
