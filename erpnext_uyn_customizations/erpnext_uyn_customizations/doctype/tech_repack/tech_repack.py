# -*- coding: utf-8 -*-
# Copyright (c) 2018, vavcoders and contributors
# For license information, please see license.txt

from __future__ import unicode_literals
import frappe
from frappe.model.document import Document
from frappe.utils import cstr, flt, getdate, comma_and, cint
from frappe.model.mapper import get_mapped_doc
from frappe.model.utils import get_fetch_values
from frappe.contacts.doctype.address.address import get_company_address
from erpnext_ebay.vlog import vwrite
class TechRepack(Document):
	pass
@frappe.whitelist()
def close_tech_repack(stock_entry,method):
	tr_no = stock_entry.__dict__.get("reference_tech_repack_no")
	if tr_no:
		tr_doc = frappe.get_doc("Tech Repack", tr_no)
		tr_doc.status = "Closed"
		tr_doc.save(ignore_permissions=True)
@frappe.whitelist()
def open_tech_repack(stock_entry,method):
	tr_no = stock_entry.__dict__.get("reference_tech_repack_no")
	if tr_no:
		tr_doc = frappe.get_doc("Tech Repack", tr_no)
		tr_doc.status = "Pending"
		tr_doc.save(ignore_permissions=True)
@frappe.whitelist()
def make_repack(source_name, target_doc=None, ignore_permissions=False):
	def postprocess(source, target):
		set_missing_values(source, target)
		#Get the advance paid Journal Entries in Sales Invoice Advance
		# target.set_advances()
		target.purpose = "Repack"
		target.reference_tech_repack_no = source_name

	def set_missing_values(source, target):
		target.is_pos = 0
		target.ignore_pricing_rule = 1
		target.flags.ignore_permissions = True
		target.run_method("set_missing_values")
		# target.run_method("set_po_nos")
		# target.run_method("calculate_taxes_and_totals")

		# set company address
		# target.update(get_company_address(target.company))
		# if target.company_address:
		# 	target.update(get_fetch_values("Sales Invoice", 'company_address', target.company_address))

	def update_item(source, target, source_parent):
		# target.amount = flt(source.amount) - flt(source.billed_amt)
		# target.base_amount = target.amount * flt(source_parent.conversion_rate)
		# target.qty = target.amount / flt(source.rate) if (source.rate and source.billed_amt) else source.qty

		# item = frappe.db.get_value("Item", target.item_code, ["item_group", "selling_cost_center"], as_dict=1)
		# target.cost_center = frappe.db.get_value("Project", source_parent.project, "cost_center") \
		# 	or item.selling_cost_center \
		# 	or frappe.db.get_value("Item Group", item.item_group, "default_cost_center")
		target.s_warehouse=source.warehouse
		target.item_code=source.item
		target.qty="1"
		target.uom='Nos'
		target.conversion_factor='1'
		target.serial_no=source.barcode
	def update_taken_item(source, target, source_parent):
		# target.amount = flt(source.amount) - flt(source.billed_amt)
		# target.base_amount = target.amount * flt(source_parent.conversion_rate)
		# target.qty = target.amount / flt(source.rate) if (source.rate and source.billed_amt) else source.qty

		# item = frappe.db.get_value("Item", target.item_code, ["item_group", "selling_cost_center"], as_dict=1)
		# target.cost_center = frappe.db.get_value("Project", source_parent.project, "cost_center") \
		# 	or item.selling_cost_center \
		# 	or frappe.db.get_value("Item Group", item.item_group, "default_cost_center")
		target.s_warehouse=source.source_warehouse
		target.item_code=source.item_code
		target.qty=source.qty
		target.uom='Nos'
		target.conversion_factor='1'
	def update_given_item(source, target, source_parent):
		# target.amount = flt(source.amount) - flt(source.billed_amt)
		# target.base_amount = target.amount * flt(source_parent.conversion_rate)
		# target.qty = target.amount / flt(source.rate) if (source.rate and source.billed_amt) else source.qty

		# item = frappe.db.get_value("Item", target.item_code, ["item_group", "selling_cost_center"], as_dict=1)
		# target.cost_center = frappe.db.get_value("Project", source_parent.project, "cost_center") \
		# 	or item.selling_cost_center \
		# 	or frappe.db.get_value("Item Group", item.item_group, "default_cost_center")
		target.t_warehouse=source.target_warehouse
		target.item_code=source.item_code
		target.qty=source.qty
		target.uom='Nos'
		target.conversion_factor='1'
	def check_if_ste_exists(source):
		try:
			ste = frappe.db.sql(" select name from `tabStock Entry` where docstatus!='2' and reference_tech_repack_no='%s'" % source)
			if len(ste) > 0:
				return True # returing false as repack already happened
		except Exception,e:
			vwrite("Exception raised in check_if_ste_exists for Tech Repack: %s" % source)
			return True
	ste_exists = check_if_ste_exists(source_name)	
	if ste_exists:
		return False

	doclist = get_mapped_doc("Tech Repack", source_name, {
		"Tech Repack": {
			"doctype": "Stock Entry",
			"field_map": {
				"item_code": "item_code"
			},
			"validation": {
				"docstatus": ["=", 1]
			}
		},
		# "Tech Repack": {
		# 	"doctype": "Stock Entry Detail",
		# 	"field_map": {
		# 		# "name": "so_detail",
		# 		# "item_code": "item_code",
		# 	},
		# 	"postprocess": update_item,
		# 	# "condition": lambda doc: doc.qty and (doc.base_amount==0 or abs(doc.billed_amt) < abs(doc.amount))
		# },
		"Tech Repack Items": {
			"doctype": "Stock Entry Detail",
			"field_map": {
				# "name": "so_detail",
				# "item_code": "item_code",
			},
			"postprocess": update_item,
			# "condition": lambda doc: doc.qty and (doc.base_amount==0 or abs(doc.billed_amt) < abs(doc.amount))
		},
		"Tech Repack Taken Items": {
			"doctype": "Stock Entry Detail",
			"field_map": {
				# "name": "so_detail",
				# "item_code": "item_code",
			},
			"postprocess": update_taken_item,
			# "condition": lambda doc: doc.qty and (doc.base_amount==0 or abs(doc.billed_amt) < abs(doc.amount))
		},
		"Tech Repack Given Items": {
			"doctype": "Stock Entry Detail",
			"field_map": {
				# "name": "so_detail",
				"item_code": "item_code",
			},
			"postprocess": update_given_item,
			# "condition": lambda doc: doc.qty and (doc.base_amount==0 or abs(doc.billed_amt) < abs(doc.amount))
		}
	}, target_doc, postprocess, ignore_permissions=ignore_permissions)

	return doclist

