# Copyright (c) 2015, Frappe Technologies Pvt. Ltd. and Contributors
# License: GNU General Public License v3. See license.txt

from __future__ import unicode_literals
import frappe
from frappe.utils import flt
from frappe import msgprint, _
import operator
from erpnext_ebay.vlog import vwrite
from erpnext_uyn_customizations.erpnext_uyn_customizations.doctype.rejects.rejects import save_reject
from collections import defaultdict
	
class MaterialStatus(object):
	from datetime import timedelta,datetime
	def __init__(self, filters=None):
		self.filters = frappe._dict(filters or {})
		self.selected_date_obj = self.datetime.strptime(self.datetime.today().strftime('%Y-%m-%d'), '%Y-%m-%d')
		# >> change date here for older dates
		#self.selected_date_obj = self.datetime.strptime('2018-10-20', '%Y-%m-%d')
		# << change date here for older dates
		self.selected_month = self.selected_date_obj.strftime('%B')
		self.today = str(self.selected_date_obj)[:10]
		from datetime import timedelta,datetime
		self.yesterday = self.selected_date_obj - self.timedelta(1)
		self.yesterday_str = str(self.yesterday)[:10]
		# self.weekstartdate = self.week_range(self.selected_date_obj)[0]
		# self.weekenddate = self.week_range(self.selected_date_obj)[1]
        
        
	def run(self, args):
		data = self.get_data()
		columns = self.get_columns()
		return columns, data
	def get_columns(self):
		"""return columns bab on filters"""
		columns = [
			_("Item Code") + ":Data:180",
			_("MR Qty") + ":Data:95",
			_("Actual Qty") + ":Data:95",
			_("PO raised to be received") + ":Data:95"
		]
		return columns
	def get_data(self):
            from erpnext.stock.report.stock_balance.stock_balance import get_stock_balance

            def get_mr_qty(item_code):
                count_sql = """ select sum(mri.qty) as count from `tabMaterial Request` mr inner join `tabMaterial Request Item` mri on mri.parent=mr.name where mr.status='Pending' and mr.docstatus=1 and mr.owner!='Administrator' and mri.item_code='{0}' """.format(item_code)
                print count_sql
                mr_count = 0
                for count in frappe.db.sql(count_sql,as_dict=1):
                    mr_count = count.get("count")
                return mr_count
            # Warehouses is mandatory for finding actual stock availability
            warehouses = []
            warehouses_sql = """ select name from `tabWarehouse` where company='Usedyetnew' """
            for warehouse in frappe.db.sql(warehouses_sql,as_dict=1):
                warehouses.append(warehouse.get("name"))

            def get_act_qty_in_store(item_code):
                stock_bal = 0
                for warehouse in warehouses:
                    stock_bal += get_stock_balance("Usedyetnew",item_code,warehouse)
                return stock_bal
            def get_po_raised_but_not_received(item_code):
                return "0"
            items_sql = """ select distinct mri.item_code,mr.name,mr.owner,mr.schedule_date from `tabMaterial Request` mr inner join `tabMaterial Request Item` mri on mri.parent=mr.name where mr.status='Pending' and mr.docstatus=1 and mr.owner!='Administrator' group by mri.item_code"""
            items_res = frappe.db.sql(items_sql,as_dict=1)
            data = []
            for item in items_res:
                item_code = item.get("item_code")
                mr_qty = get_mr_qty(item_code=item_code)
                act_qty = get_act_qty_in_store(item_code)
                po_pending_qty = get_po_raised_but_not_received(item_code)
                data.append([item_code,mr_qty,act_qty,po_pending_qty])
            return data
@frappe.whitelist()
def execute(filters=None):
    args = {

    }
    return MaterialStatus(filters).run(args)


