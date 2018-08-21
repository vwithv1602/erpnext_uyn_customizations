# Copyright (c) 2013, vavcoders and contributors
# For license information, please see license.txt

from __future__ import unicode_literals
import frappe
from frappe.utils import flt
from frappe import msgprint, _
import operator
from erpnext_ebay.vlog import vwrite
from datetime import timedelta,datetime
import calendar
from dateutil.relativedelta import relativedelta

def execute(filters=None):
	columns, data = [], []
	data = []
	columns = [_("Month") + "::220",_("Defects in that month") + "::220",_("Total Sales in last 6 months") + "::220",_("Issue Rate") + "::120"]
	# get oldest date from Defects
	start_date_sql = """ select MIN(date) as start_date from `tabDefects` """
	start_date_res = frappe.db.sql(start_date_sql, as_dict=1)
	start_date = start_date_res[0].get("start_date")
	start_date = start_date + relativedelta(day=1)
	next_date = start_date + relativedelta(day=1, months=+1, days=-1)
	# next_date = start_date

	from collections import OrderedDict
	dates = [str(start_date), str(datetime.now().date())]
	start, end = [datetime.strptime(x, "%Y-%m-%d") for x in dates]
	months = OrderedDict(((start + timedelta(x)).strftime(r"%Y-%m-01"), None) for x in xrange((end - start).days)).keys()
	for month in months:
		start_date = datetime.strptime(month, "%Y-%m-%d").date()
		next_date =  start_date + relativedelta(day=1, months=+1, days=-1)
		month_name = datetime.strptime(str(start_date), "%Y-%m-%d").strftime("%B")
		year = datetime.strptime(str(start_date), "%Y-%m-%d").strftime("%Y")
		defects_count_sql = """ select count(*) as count from `tabDefects` where date between '%s' and '%s' """ %(month,next_date)
		defects_count_res = frappe.db.sql(defects_count_sql,as_dict=1)
		defects_count = defects_count_res[0].count

		sold_count_sql = """ 
		select sum(sii.qty) as count from `tabSales Invoice` si 
		inner join `tabSales Invoice Item` sii on sii.parent=si.name 
		inner join `tabDelivery Note Item` dni on dni.si_detail=sii.name
		inner join `tabDelivery Note` dn on dni.parent=dn.name
		where sii.item_group in ('Laptops','Desktops')
		and dni.docStatus=1 and dn.status='Completed' and si.docStatus not in (0,2) and si.creation <= '%s' and (si.creation >= '%s' - INTERVAL 6 MONTH) and si.update_stock=0 and si.status not in ('Cancelled','Credit Note Issued') order by si.creation """ % (next_date,next_date)
		sold_count_res = frappe.db.sql(sold_count_sql,as_dict=1)
		sold_in_last_six_months = sold_count_res[0].count
		sold_count_sql_us = """ 
		select sum(sii.qty) as count from `tabSales Invoice` si 
		inner join `tabSales Invoice Item` sii on sii.parent=si.name 
		where sii.item_group in ('Laptops','Desktops')
		and si.docStatus not in (0,2) and si.creation <= '%s' and (si.creation >= '%s' - INTERVAL 6 MONTH) and si.update_stock=1 and si.status not in ('Cancelled','Credit Note Issued') order by si.creation """ % (next_date,next_date)
		sold_count_res_us = frappe.db.sql(sold_count_sql_us,as_dict=1)
		sold_in_last_six_months_us = sold_count_res_us[0].count
		sold_in_last_six_months = sold_in_last_six_months + sold_in_last_six_months_us
		# sold_count_sql and sold_count_sql_us is wrong
		sold_count_sql_modified = """ select sum(sii.qty) as count from `tabSales Invoice` si inner join `tabSales Invoice Item` sii on sii.parent=si.name where  sii.item_group in ('Laptops','Desktops') and si.posting_date <= '%s' and (si.posting_date >= '%s' - INTERVAL 5 MONTH) and si.status not in ('Cancelled','Credit Note Issued') """ %(next_date,next_date)
		print sold_count_sql_modified
		sold_count_res_modified = frappe.db.sql(sold_count_sql_modified,as_dict=1)
		sold_in_last_six_months = sold_count_res_modified[0].count
		if not defects_count:
			print next_date
			print "defects_count"
		if not sold_in_last_six_months:
			print next_date
			print sold_count_sql_modified
		rate = float(float(defects_count)/float(sold_in_last_six_months))*100
		# print "%s - %s :: %.2f%s" %(defects_count,sold_in_last_six_months,rate,"%")
		rate = "%.2f%s" %(rate,"%")
		data.append(["%s, %s" % (month_name,year),defects_count,sold_in_last_six_months,rate])





	return columns, data

def get_columns():
	# columns = [
	# 	_("Item Group") + "::120"
	# ]
	return []

@frappe.whitelist()
def get_data():
	return []
