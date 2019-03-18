# Copyright (c) 2015, Frappe Technologies Pvt. Ltd. and Contributors
# MIT License. See license.txt
# UYN Created & Modified
from __future__ import unicode_literals
import frappe
from frappe import _
import frappe.model
import frappe.utils
import json, os
import ast
from erpnext_ebay.vlog import vwrite
def get_all_material_requests():
    sql = """ select mr.name,mr.schedule_date,mri.item_code,mri.qty from `tabMaterial Request` mr inner join `tabMaterial Request Item` mri on mri.parent=mr.name where mr.status='Pending' and mr.docstatus=1 """
    mrs = []
    for mr in frappe.db.sql(sql,as_dict=1):
        mrs.append({
            'schedule_date':str(mr.get("schedule_date")),
            'name':mr.get("name"),
            'qty':mr.get("qty"),
	    'item_code':mr.get("item_code")
        })
    return mrs
