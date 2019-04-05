 # Copyright (c) 2013, vavcoders and contributors
# For license information, please see license.txt

from __future__ import unicode_literals
import frappe
from frappe import _
from frappe.utils.background_jobs import enqueue
from erpnext_ebay.vlog import vwrite
from erpnext_uyn_customizations.report.stock_ageing_in_warehouses.stock_ageing_in_warehouses import get_stock_current_warehouse_details, get_stock_purchase_receipt_details

def update_serial_no_purchase_details(stock_purchase_details):
	
	serial_no_list = stock_purchase_details.keys()

	for serial_no in serial_no_list:
		query = """update `tabSerial No` set total_age={0} where name='{1}'""".format(int(stock_purchase_details[serial_no][2]), str(serial_no))
		frappe.db.sql(query)
		frappe.db.commit()


def update_serial_no_warehouse_age(stock_current_warehouse_details):

	serial_no_list = stock_current_warehouse_details.keys()

	for serial_no in serial_no_list:
		query = """update `tabSerial No` set age_in_warehouse={0} where name='{1}'""".format(int(stock_current_warehouse_details[serial_no][2]), str(serial_no))
		frappe.db.sql(query)
		frappe.db.commit()

@frappe.whitelist()
def sync_now():
    enqueue("erpnext_uyn_customizations.sync_age.sync_warehouse_and_total_age", queue='long')
    frappe.msgprint(_("Queued for syncing. It may take a few minutes to complete."))

def sync_warehouse_and_total_age():

    stock_purchase_details = get_stock_purchase_receipt_details()
    stock_current_warehouse_details = get_stock_current_warehouse_details()
    update_serial_no_purchase_details(stock_purchase_details)
    update_serial_no_warehouse_age(stock_current_warehouse_details)
