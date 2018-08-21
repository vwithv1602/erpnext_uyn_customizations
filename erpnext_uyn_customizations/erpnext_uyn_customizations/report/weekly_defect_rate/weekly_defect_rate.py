# Copyright (c) 2013, vavcoders and contributors
# For license information, please see license.txt

from __future__ import unicode_literals
import frappe
from frappe.utils import flt
from frappe import msgprint, _
import operator
from erpnext_ebay.vlog import vwrite
from datetime import timedelta,datetime

def execute(filters=None):
	columns, data = [], []
	data = []
	columns = [_("Date Range (weekly)") + "::220",_("Count") + "::120"]
	# get oldest date from Defects
	start_date_sql = """ select MIN(date) as start_date from `tabDefects` """
	start_date_res = frappe.db.sql(start_date_sql, as_dict=1)
	start_date = start_date_res[0].get("start_date")
	next_date = start_date
	while next_date < datetime.now().date():
		next_date = start_date + timedelta(7)
		# print "start_date: %s, next_date: %s" %(start_date,next_date)
		# columns.append("for %s week" % next_date)
		count_sql = """ select count(*) as count from `tabDefects` where date between '%s' and '%s' """ %(start_date,next_date)
		count_res = frappe.db.sql(count_sql,as_dict=1)
		count = count_res[0].count
		data.append(["from %s to %s" % (start_date,next_date),count])
		start_date = next_date + timedelta(1)
	return columns, data

def get_columns():
	# columns = [
	# 	_("Item Group") + "::120"
	# ]
	return []

@frappe.whitelist()
def get_data():
	return []


	# bench execute erpnext_uyn_customizations.erpnext_uyn_customizations.report.weekly_defect_rate.weekly_defect_rate.get_data
