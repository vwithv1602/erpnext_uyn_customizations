# Copyright (c) 2015, Frappe Technologies Pvt. Ltd. and Contributors
# License: GNU General Public License v3. See license.txt

from __future__ import unicode_literals
import frappe
from frappe.utils import flt
from frappe import msgprint, _
import operator
from erpnext_ebay.vlog import vwrite

class StockAgainstMReq(object):
    def __init__(self, filters=None):
        self.filters = frappe._dict(filters or {})
        self.selected_date_obj = self.datetime.strptime(self.datetime.today().strftime('%Y-%m-%d'), '%Y-%m-%d')
        # >> change date here for older dates
        # self.selected_date_obj = self.datetime.strptime('2018-11-18', '%Y-%m-%d')
		# << change date here for older dates
        self.selected_month = self.selected_date_obj.strftime('%B')
        self.today = str(self.selected_date_obj)[:10]
        from datetime import timedelta,datetime
        self.yesterday = self.selected_date_obj - self.timedelta(1)
        self.yesterday_str = str(self.yesterday)[:10]
        self.weekstartdate = self.week_range(self.selected_date_obj)[0]
        self.weekenddate = self.week_range(self.selected_date_obj)[1]
        
    def run(self, args):
        data = self.get_data()
        columns = self.get_columns()
        return columns, data
    from datetime import timedelta,datetime
    
    def week_range(self,date):
		"""Find the first/last day of the week for the given day.
		Assuming weeks start on Sunday and end on Saturday.
		Returns a tuple of ``(start_date, end_date)``.
		"""
		# isocalendar calculates the year, week of the year, and day of the week.
		# dow is Mon = 1, Sat = 6, Sun = 7
		date = date - self.timedelta(1)
		year, week, dow = date.isocalendar()
		# Find the first day of the week.
		if dow == 7:
			# Since we want to start with Sunday, let's test for that condition.
			start_date = date
		else:
			# Otherwise, subtract `dow` number days to get the first day
			start_date = date - self.timedelta(dow)
		# Now, add 6 for the last day of the week (i.e., count up to Saturday)
		end_date = start_date + self.timedelta(7)
		return (start_date.strftime('%Y-%m-%d'), end_date.strftime('%Y-%m-%d'))

    def get_columns(self):
        """return columns bab on filters"""
        columns = [
	    _("Item Group") + ":Data:60",
	    _("Model Name") + ":Link/Item:60",
	    _("Serial No") + ":Link/Serial No:80",
            _("MReq No") + ":Link/Material Request:80",
	    _("MReq Status")+":Data:60",
            _("Item Code") + ":Link/Item:100",
	    _("Actual Qty") + ":Float:50",
            _("Warehouse") + ":Data:80",
            _("Requestor Comment") + ":Data:100",
            _("IBM Sheet same issue") + ":Data:40",
            _("QC Remarks") + ":Data:50",
            _("Adapter") + ":Data:50",
            _("Battery") + ":Data:50",
            _("Display") + ":Data:50",
            _("A") + ":Data:20",
            _("B") + ":Data:20",
            _("C") + ":Data:20",
            _("D") + ":Data:20",
            _("HeatSinkGrill") + ":Data:50",
	    _("Date") + ":Data:80"


        ]
        return columns

    from datetime import timedelta,datetime
    def get_data(self):
        data = []
        # def get_stock_balance(item_code):
        #     sql = """ SELECT sum(actual_qty) as stock_bal from `tabStock Ledger Entry` WHERE item_code='{0}' """.format(item_code)

        #     res = frappe.db.sql(sql,as_dict=1)
        #     if len(res)>0:
        #         return res[0].get("stock_bal")
        #     else:
        #         return 0
            # return frappe.db.sql(sql,as_dict=1)[0]
        # sql = """ select sn.item_code as against_item_code,sn.warehouse as current_warehouse,sn.initial_odd,sn.initial_web_cam,sn.initial_qc_remarks,sn.initial_keyboard_received,sn.initial_adapter__received,sn.initial_battery,sn.initial_display,sn.initial_body_a,sn.initial_body_b,sn.initial_body_c,sn.initial_body_d,sn.initial_heat_sink_grill,a.name as mreq_name,a.status as mreq_status,b.warehouse as warehouse,a.company as company,a.transaction_date,b.item_code,b.serial_no,a.status,b.requestor_comment,b.ibm_sheet_same_issue from `tabMaterial Request` as a  inner join `tabMaterial Request Item` as b on b.parent=a.name left join `tabSerial No` sn on sn.name=b.serial_no where a.status in ('Pending','Partially Ordered') group by b.serial_no,b.item_code """
	sql = """ select i.item_group,a.against_item_code as against_item_code,a.current_warehouse as current_warehouse,a.initial_odd,a.initial_web_cam,a.initial_qc_remarks,a.initial_keyboard_received,a.initial_adapter__received,a.initial_battery,a.initial_display,a.initial_body_a,a.initial_body_b,a.initial_body_c,a.initial_body_d,a.initial_heat_sink_grill,a.mreq_name as mreq_name,a.mreq_status as mreq_status,a.warehouse as warehouse,a.company as company,a.transaction_date,a.item_code,a.serial_no,a.status,a.requestor_comment,a.ibm_sheet_same_issue 
from (select sn.item_code as against_item_code,sn.warehouse as current_warehouse,sn.initial_odd,sn.initial_web_cam,sn.initial_qc_remarks,sn.initial_keyboard_received,sn.initial_adapter__received,sn.initial_battery,sn.initial_display,sn.initial_body_a,sn.initial_body_b,sn.initial_body_c,sn.initial_body_d,sn.initial_heat_sink_grill,mr.name as mreq_name,mr.status as mreq_status,mri.warehouse as warehouse,mr.company as company,mr.transaction_date,mri.item_code,mri.serial_no,mr.status,mri.requestor_comment,mri.ibm_sheet_same_issue from `tabMaterial Request` as mr  inner join `tabMaterial Request Item` as mri on mri.parent=mr.name left join `tabSerial No` sn on sn.name=mri.serial_no where mr.status in ('Pending','Partially Ordered') group by mri.serial_no,mri.item_code) as a left join `tabItem` i on i.name=a.item_code """
        from erpnext.stock.report.stock_balance.stock_balance import get_stock_balance
        for rec in frappe.db.sql(sql,as_dict=1):
	    stock_bal_in_stores = get_stock_balance(rec.get("company"),rec.get("item_code"),"Stores - Uyn")
	    stock_bal_in_iqc = get_stock_balance(rec.get("company"),rec.get("item_code"),"IQC Store - Uyn")
	    stock_bal = stock_bal_in_stores + stock_bal_in_iqc
            # stock_bal = get_stock_balance(rec.get("company"),rec.get("item_code"),"Stores - Uyn")
            data.append([rec.get("item_group"),rec.get("against_item_code"),rec.get("serial_no"),rec.get("mreq_name"),rec.get("mreq_status"),rec.get("item_code"),stock_bal,rec.get("current_warehouse"),rec.get("requestor_comment"),rec.get("ibm_sheet_same_issue"),rec.get("initial_qc_remarks"),rec.get("initial_adapter__received"),rec.get("initial_battery"),rec.get("initial_display"),rec.get("initial_body_a"),rec.get("initial_body_b"),rec.get("initial_body_c"),rec.get("initial_body_d"),rec.get("initial_heat_sink_grill"),str(rec.get("transaction_date"))])
        return data
@frappe.whitelist()
def execute(filters=None):
    args = {

    }
    return StockAgainstMReq(filters).run(args)
    

