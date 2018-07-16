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

@frappe.whitelist()
def get_check_list_based_on_inspection_type(doctype, fields=None, filters=None, order_by=None,limit_start=None, limit_page_length=20, parent=None,inspection_type=None):
    '''Returns a list of records by filters, fields, ordering and limit
	:param doctype: DocType of the data to be queried
	:param fields: fields to be returned. Default is `name`
	:param filters: filter list by this dict
	:param order_by: Order by this fieldname
	:param limit_start: Start at this index
	:param limit_page_length: Number of records to be returned (default 20)

    UYN Requirement:
    get_list of `Item Group Quality Checks` depending on `Inspection Type`'''
    # fields = [x.encode('UTF8') for x in fields]
    filters = ast.literal_eval(filters)
    where_string = ""
    for key,value in filters.iteritems():
        where_string += " `%s`%s'%s' and" % (key,value[0],value[1])
    where_string = where_string[:-3]
    # checks_sql = """ select %s from `tabItem Group Quality Checks` where %s and name in (select igqc.name from `tabQuality Check Inspection Type` qcit left join `tabItem Group Quality Checks` igqc on igqc.name=qcit.parent where qcit.inspection_type='%s')""" %(fields,where_string,inspection_type)
    checks_sql = """ (select {0} from `tabItem Group Quality Checks` where {1} and name not in (select distinct parent from `tabQuality Check Inspection Type`)) union  (select {0} from `tabItem Group Quality Checks` where {1} and name in (select distinct parent from `tabQuality Check Inspection Type` where inspection_type='{2}')) """.format(fields,where_string,inspection_type)
    checks_result = frappe.db.sql(checks_sql, as_dict=1)
    return checks_result
