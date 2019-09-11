# Copyright (c) 2013, vavcoders and contributors
# For license information, please see license.txt
# Copyright (c) 2013, vavcoders and contributors
# For license information, please see license.txt

from __future__ import unicode_literals
import frappe
from frappe import _
from datetime import datetime,timedelta
from erpnext_ebay.vlog import vwrite

current_date = datetime.today()
weeks_first_day = current_date - timedelta(days=current_date.weekday())
weeks_last_day = weeks_first_day + timedelta(days=6)

def get_columns():
	"""return columns bab on filters"""
	columns = [

		_("DN exists and App installed") + ":Data:180",
		_("Registered within 2 days") + ":Data:180",
		_("Registered within 5 days") + ":Data:180",
		_("Registered within 8 days") + ":Data:180",
		_("Registered within 12 days") + ":Data:180",
	]
	return columns

def count_serial_numbers_with_app_installed_in_week():
	serial_numbers_with_app_installed_query = """
	select count(sn.name) as count from `tabSerial No` sn
	inner join `tabDelivery Note Item` dni on dni.serial_no like CONCAT('%%',sn.name,'%%')
	inner join `tabDelivery Note` dn on dn.name = dni.parent
	where
		dn.docstatus = 1 and
		sn.installation_time is not NULL and
		dn.posting_date > '{0}' and
		dn.posting_date <= '{1}'
	""".format(str(weeks_first_day),str(weeks_last_day))
	count_dict = frappe.db.sql(serial_numbers_with_app_installed_query,as_dict=1)
	return count_dict

def count_of_laptops_registered_within(lt_days,gt_days):
	
	count_of_laptops_registered_query = """
	select count(sn.name) as count from `tabSerial No` sn
	inner join `tabDelivery Note Item` dni on dni.serial_no like CONCAT('%%',sn.name,'%%')
	inner join `tabDelivery Note` dn on dn.name = dni.parent
	inner join `tabSales Order` so on so.name = dni.against_sales_order
	inner join `tabAddress` a on a.name = so.customer_address
	where
		dn.docstatus = 1 and
		dn.is_return = 0 and
		(sn.warehouse is NULL or sn.warehouse = '') and
		a.modified_by = 'it@usedyetnew.com' and
		sn.initiation_time is not NULL and
		a.modified > '{0}' and
		a.modified <= '{1}' and
		DATEDIFF(sn.initiation_time,a.modified) >= {2} and
		DATEDIFF(sn.initiation_time,a.modified) <= {3}
	""".format(weeks_first_day,weeks_last_day,gt_days, lt_days)
	count_dict = frappe.db.sql(count_of_laptops_registered_query,as_dict=1)
	return count_dict

def get_data():
	
	count_dict_of_items_dned = count_serial_numbers_with_app_installed_in_week()
	count_of_items_dned = count_dict_of_items_dned[0]['count']

	activated_within_two_days = count_of_laptops_registered_within(2,0)[0]['count']

	activated_within_five_days = count_of_laptops_registered_within(5,3)[0]['count']

	activated_within_eight_days = count_of_laptops_registered_within(8,6)[0]['count']

	activated_within_twelve_days = count_of_laptops_registered_within(12,9)[0]['count']

	return [[count_of_items_dned,activated_within_two_days,activated_within_five_days,activated_within_eight_days,activated_within_twelve_days]]



def execute(filters=None):
	columns, data = get_columns(), get_data()
	return columns, data
