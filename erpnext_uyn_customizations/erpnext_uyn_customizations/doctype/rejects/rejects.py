# -*- coding: utf-8 -*-
# Copyright (c) 2018, vavcoders and contributors
# For license information, please see license.txt

from __future__ import unicode_literals
import frappe
from frappe.model.document import Document
from frappe.utils import flt
from frappe import msgprint, _
from erpnext_ebay.vlog import vwrite

class Rejects(Document):
	pass
def get_warehouse_sequence(warehouse):
	seq_sql = """ select warehouse_sequence_number from `tabWarehouse` where warehouse_name='{0}' """.format(warehouse[:-6])
	return frappe.db.sql(seq_sql,as_dict=1)[0].get("warehouse_sequence_number")
def save_reject(rej_obj):
	# check if reject
	from_warehouse_sequence = get_warehouse_sequence(rej_obj.get("from_warehouse"))
	to_warehouse_sequence = get_warehouse_sequence(rej_obj.get("to_warehouse"))
	if from_warehouse_sequence!='' and to_warehouse_sequence!='' and from_warehouse_sequence>to_warehouse_sequence:
		rej_doc = frappe.get_doc({ 
			"doctype": "Rejects",
			"inspected_by": rej_obj.get("inspected_by"),
			"serial_no": rej_obj.get("serial_no"),
			"rejected_date": rej_obj.get("rejected_date"),
			"qc_date": rej_obj.get("qc_date"),
			"inspection_type": rej_obj.get("inspection_type"),
			"from_warehouse": rej_obj.get("from_warehouse"),
			"to_warehouse": rej_obj.get("to_warehouse"),
			"ste": rej_obj.get("ste_name"),
			"qc": rej_obj.get("qi_name")
		})
		rej_doc.flags.ignore_mandatory = True
		try:
			rej_doc.save(ignore_permissions=True)
		except Exception, e:
			print "Exception raised in saving reject"
			print e
			print e.message

def get_last_qc(serial_no,inspection_type):
	inspection_sql = """ select name,inspected_by,report_date,inspection_type from `tabQuality Inspection` where inspection_type = '{0}' and barcode='{1}' order by report_date desc """.format(inspection_type,serial_no)
	inspection_res = frappe.db.sql(inspection_sql,as_dict=1)
	return inspection_res[0] if len(inspection_res)>0 else None
@frappe.whitelist()
def test():
	print get_last_qc('R9WAN16','In Process')
def get_inspection_type(t_warehouse):
	warehouses_sql = """ select warehouse_name,warehouse_sequence_number,warehouse_inspection_type from `tabWarehouse` where warehouse_name = '{0}' """.format(t_warehouse[:-6])
	warehouses_res = frappe.db.sql(warehouses_sql,as_dict=1)
	return warehouses_res[0].get("warehouse_inspection_type") if len(warehouses_res)>0 else None


def log_reject(reject,method):
	items = reject.__dict__.get("items")
	if method == 'on_submit' and reject.__dict__.get("purpose")=='Material Transfer':
		for item in items:
			itm = item.__dict__
			vwrite(itm)
			inspection_type = get_inspection_type(itm.get("t_warehouse"))
			last_qc = get_last_qc(itm.get("serial_no"),inspection_type)
			if last_qc:
				obj = {
					"doctype": "Rejects",
					"inspected_by": last_qc.get("inspected_by"),
					"serial_no": itm.get("serial_no"),
					"rejected_date": reject.__dict__.get("posting_date"),
					"qc_date": str(last_qc.get("report_date")),
					"inspection_type": last_qc.get("inspection_type"),
					"from_warehouse": itm.get("s_warehouse"),
					"to_warehouse": itm.get("t_warehouse"),
					"ste_name": reject.__dict__.get("name"),
					"qi_name": last_qc.get("name"),
				}
				save_reject(obj)
