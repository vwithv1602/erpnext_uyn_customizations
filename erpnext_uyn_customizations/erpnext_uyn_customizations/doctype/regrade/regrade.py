# -*- coding: utf-8 -*-
# Copyright (c) 2018, vavcoders and contributors
# For license information, please see license.txt

from __future__ import unicode_literals
import frappe
from frappe.model.document import Document
import json, os
from frappe.utils import cstr, flt, getdate, comma_and, cint
from frappe.model.mapper import get_mapped_doc
from frappe.model.utils import get_fetch_values

from erpnext_uyn_customizations.client import get_doctype_details
from erpnext.vlog import vwrite
from datetime import datetime

class ReGrade(Document):
	pass

@frappe.whitelist()
def regrade_items(regrade_items):
	regrade_items = json.loads(regrade_items)
	throw_error = False
	error = ""
	for regrade_item in regrade_items:
		filters = [{"parent":["=",regrade_item.get("item_code")]}]
		filters = json.dumps(filters)
		try:
			attr_res = get_doctype_details('`tabItem Variant Attribute`', '`attribute`,`attribute_value`', filters, None,None, None, None)
			where_str = ""
			for attr in attr_res:
				if attr.get("attribute") != 'Grade':
					where_str += " item_code like '%{0}%' and".format(attr.get("attribute_value"))
			# where_string = " where " + " and ".join(where_str)
		except Exception,e:
			vwrite("Exception raised in regrade_items")
			vwrite(e)
		where_str = " where {0} item_code like '%{1}%'".format(where_str,regrade_item.get("grade"))
		to_item_sql = """ select item_code from tabItem {0} """.format(where_str)
		to_item_res = frappe.db.sql(to_item_sql,as_dict=1)
		if len(to_item_res) == 0:
			throw_error = True
			error += "Can't convert <b>{0}</b> to <b>{1}</b> <br>".format(regrade_item.get("item_code"),regrade_item.get("grade"))
		# vwrite("find if %s is available for the same variant" % regrade_item.get("grade"))
	if throw_error:
		frappe.throw(error)
	return "in regrade_items"


def get_serial_no_warehouse(barcode):
	filters = [{"barcode":["=",barcode]}]
	filters = json.dumps(filters)
	try:
		warehouse_res = get_doctype_details('`tabSerial No`', '`warehouse`', filters, None,None, None, None)
		if len(warehouse_res)>0:
			return warehouse_res[0].get("warehouse")
	except Exception,e:
		vwrite(e)
@frappe.whitelist()
def get_item_code_with_grade(item_code,grade):
	new_grade_sql = """ select parent from `tabItem Variant Attribute` where attribute='Grade' and attribute_value='{0}' and parent in (select item_code from tabItem where variant_of=(select variant_of from tabItem where item_code='{1}')) """.format(grade,item_code)
	new_grade_res = frappe.db.sql(new_grade_sql,as_dict=1)
	return new_grade_res[0].get("parent")
@frappe.whitelist()
def validate_grades(item_code,grade):
	# item_code = 'Ref Lenovo Thinkpad-L412 - CORE I5 1ST GEN-4 GB-320 GB-GRADE B'
	# item_code = 'T430 MotherBoard'
	# grade = 'GRADE D'
	existing_grade_sql = """ select attribute,attribute_value from `tabItem Variant Attribute` where parent='{0}' and attribute='Grade'""".format(item_code)
	existing_grade_res = frappe.db.sql(existing_grade_sql,as_dict=1)
	if len(existing_grade_res)>0:
		new_grade_sql = """ select parent from `tabItem Variant Attribute` where attribute='Grade' and attribute_value='{0}' and parent in (select item_code from tabItem where variant_of=(select variant_of from tabItem where item_code='{1}')) """.format(grade,item_code)
		new_grade_res = frappe.db.sql(new_grade_sql,as_dict=1)
		if len(new_grade_res)==0:
			return "{0} is not available for {1}".format(grade,item_code)
	else:
		return "{0} is not a gradable item".format(item_code)
	return "OK"
total_source_rate = 0
total_target_rate = 0
@frappe.whitelist()
def test_repack(source_name,target_doc=None):
	def postprocess(source, target):
		set_missing_values(source, target)
		target.purpose = "Repack"
	def set_missing_values(source, target):
		target.is_pos = 0
		target.ignore_pricing_rule = 1
		target.flags.ignore_permissions = True
		target.run_method("set_missing_values")
	def update_item(source, target, source_parent):
		target.s_warehouse = get_serial_no_warehouse(source.__dict__.get("barcode"))
		# target.basic_rate = "6,106.21"
		target.serial_no=source.barcode
		target.s_warehouse=source.warehouse
		# target.item_code=source.item
		target.qty="1"
		target.uom='Nos'
		target.conversion_factor='1'
		
		# #target.basic_rate=get_basic_rate(source.item,'source')
		args = frappe._dict({"item_code":source.item_code,"qty":-1,"allow_zero_valuation":1,"warehouse":target.s_warehouse,"voucher_type":"Stock Entry","cost_center":"Main - Uyn","posting_date":str(datetime.now().isoformat())[:10],"posting_time":str(datetime.now().isoformat())[11:],"serial_no":source.barcode})
		from erpnext.stock.utils import get_incoming_rate
		target.basic_rate = get_incoming_rate(args)
		global total_source_rate
		total_source_rate = total_source_rate + target.basic_rate
	def update_target_item(source, target, source_parent):
		target.t_warehouse = get_serial_no_warehouse(source.__dict__.get("barcode"))
		# target.basic_rate = "6,106.21"
		target.serial_no = source.barcode
		target.barcode=""
		target.t_warehouse=source.warehouse
		# target.item_code="%s%s" %(source.item_code[:-7],source.grade)
		target.item_code = get_item_code_with_grade(source.item_code,source.grade)
		target.qty="1"
		target.uom='Nos'
		target.conversion_factor='1'
		
		# #target.basic_rate=get_basic_rate(source.item,'source')
		args = frappe._dict({"item_code":source.item_code,"qty":-1,"allow_zero_valuation":1,"warehouse":target.t_warehouse,"voucher_type":"Stock Entry","cost_center":"Main - Uyn","posting_date":str(datetime.now().isoformat())[:10],"posting_time":str(datetime.now().isoformat())[11:],"serial_no":source.barcode})
		from erpnext.stock.utils import get_incoming_rate
		target.basic_rate = get_incoming_rate(args)
		global total_source_rate
		total_source_rate = total_source_rate + target.basic_rate
	doclist = get_mapped_doc("ReGrade", source_name, {
		"ReGrade": {
			"doctype": "Stock Entry",
			"field_map": {
				"item_code": "item_code"
			},
			"validation": {
				"docstatus": ["=", 0]
			}
		},
		"Grade Detail": {
			"doctype": "Stock Entry Detail",
			"field_map": {
				# "name": "so_detail",
				# "item_code": "item_code",
			},
			"postprocess": update_item,
			# "condition": lambda doc: doc.qty and (doc.base_amount==0 or abs(doc.billed_amt) < abs(doc.amount))
		},
		"Grade Detail Hidden": {
			"doctype": "Stock Entry Detail",
			"field_map": {
				# "name": "so_detail",
				# "item_code": "item_code",
			},
			"postprocess": update_target_item,
			# "condition": lambda doc: doc.qty and (doc.base_amount==0 or abs(doc.billed_amt) < abs(doc.amount))
		}
	}, None, postprocess, ignore_permissions=True)
	return doclist
