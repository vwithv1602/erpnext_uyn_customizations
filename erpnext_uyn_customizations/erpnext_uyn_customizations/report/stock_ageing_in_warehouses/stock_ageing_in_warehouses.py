# Copyright (c) 2013, vavcoders and contributors
# For license information, please see license.txt

from __future__ import unicode_literals
import frappe
from frappe import _
from sets import Set
from operator import itemgetter
from erpnext_ebay.vlog import vwrite

def get_columns():
	"""return columns bab on filters"""
	columns = [

		_("Serial No") + ":Link/Serial No:120",
		_("Item Code") + ":Data:120",
		_("Purchase Receipt Date") + ":Data:120",
		_("Total Age in ERP") + ":Float:120",
		_("Current Warehouse") + ":Data:120",
		_("Last Transfer Date") + ":Data:120",
		_("Warehouse Ageing") + ":Float:120"
	]
	return columns

def get_stock_purchase_receipt_details():
	stock_purchase_details = {}
	stock_purchase_receipt_details_query = """select a.name,a.item_code,min(b.creation),DateDiff(NOW(),min(b.creation)) from `tabSerial No` a inner join `tabStock Ledger Entry` b on b.serial_no like CONCAT("%%",a.name,"%%") where a.warehouse not like "" and a.warehouse not in (select name from `tabWarehouse` where parent_warehouse="Team Members - Uyn") and a.item_group in ("Laptops") group by a.name"""

	for stock_entry in frappe.db.sql(stock_purchase_receipt_details_query):
		stock_purchase_details[stock_entry[0]] = [stock_entry[1],stock_entry[2],stock_entry[3]]
	#vwrite(stock_purchase_details)
	return stock_purchase_details

def get_stock_current_warehouse_details():
	stock_current_warehouse_details = {}
	stock_current_warehouse_details_query = """select a.name,a.item_code,max(b.creation),DateDiff(NOW(),max(b.creation)),a.warehouse from `tabSerial No` a inner join `tabStock Ledger Entry` b on b.serial_no like CONCAT("%%",a.name,"%%") where a.warehouse not like "" and a.warehouse not in (select name from `tabWarehouse` where parent_warehouse="Team Members - Uyn") and a.item_group in ("Laptops") group by a.name"""

	for stock_entry in frappe.db.sql(stock_current_warehouse_details_query):
		stock_current_warehouse_details[stock_entry[0]] = [stock_entry[1],stock_entry[2],stock_entry[3],stock_entry[4]]

	return stock_current_warehouse_details

def get_data():
	
	stock_purchase_details = get_stock_purchase_receipt_details()
	stock_current_warehouse_details = get_stock_current_warehouse_details()

	serial_no_list =  []
	serial_no_list.extend(stock_current_warehouse_details.keys())
	serial_no_list.extend(stock_purchase_details.keys())

	serial_no_list = list(set(serial_no_list))

	data = []
	# Serial No,Item code,Purchase receipt date, total age in ERP, Current Warehouse, material receipt date, Ageing 
	for serial_no in serial_no_list:
		item_code = None
		if serial_no in stock_purchase_details:
			item_code = stock_purchase_details.get(serial_no)[0]
		else:
			item_code = stock_current_warehouse_details.get(serial_no)[0]
		
		purchase_receipt_date = stock_purchase_details.get(serial_no, None)
		if purchase_receipt_date:
			purchase_receipt_date = purchase_receipt_date[1]
		else:
			purchase_receipt_date = "Unknown"
		
		total_age_in_erp = stock_purchase_details.get(serial_no, None)
		if total_age_in_erp:
			total_age_in_erp = int(total_age_in_erp[2])
		else:
			total_age_in_erp = 0
		
		current_warehouse = stock_current_warehouse_details.get(serial_no,None)
		if current_warehouse:
			current_warehouse = current_warehouse[3]
		else:
			current_warehouse = "Unknown"
		
		material_receipt_date = stock_current_warehouse_details.get(serial_no, None)
		if material_receipt_date:
			material_receipt_date = material_receipt_date[1]
		else:
			material_receipt_date = "Unknown"
		
		current_warehouse_ageing = stock_current_warehouse_details.get(serial_no, None)
		if current_warehouse_ageing:
			current_warehouse_ageing = int(current_warehouse_ageing[2])
		else:
			current_warehouse_ageing = 0
		
		if total_age_in_erp < 90:
			continue
		
		data.append([serial_no, item_code, purchase_receipt_date, total_age_in_erp, current_warehouse, material_receipt_date, current_warehouse_ageing])
	data = sorted(data, key=itemgetter(3), reverse=True)
	return data


def execute(filters=None):
	columns, data = get_columns(), get_data()
	return columns, data
