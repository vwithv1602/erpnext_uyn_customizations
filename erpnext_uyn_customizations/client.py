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

@frappe.whitelist()
def get_doctype_details(doctype, fields=None, filters=None, order_by=None,limit_start=None, limit_page_length=20, parent=None):
    filters = ast.literal_eval(filters)
    where_string = ""
    for key,value in filters.iteritems():
        # vwrite("key: %s, value[0]: %s, value[1]: %s" %(key,value[0],value[1]))
        if value[0] == ' in ':
            where_string += " `%s` %s %s and" % (key,value[0],value[1])
        else:
            where_string += " `%s`%s'%s' and" % (key,value[0],value[1])
    
    where_string = where_string[:-3]
    # checks_sql = """ select %s from `tabItem Group Quality Checks` where %s and name in (select igqc.name from `tabQuality Check Inspection Type` qcit left join `tabItem Group Quality Checks` igqc on igqc.name=qcit.parent where qcit.inspection_type='%s')""" %(fields,where_string,inspection_type)
    checks_sql = """ select {0} from {1} where {2} """.format(fields,doctype,where_string)
    #vwrite(checks_sql)
    checks_result = frappe.db.sql(checks_sql, as_dict=1)
    # vwrite(checks_result)
    return checks_result
@frappe.whitelist()
def get_phone_number_from_address(address_dict):
    if not address_dict:
        return
    phone = frappe.db.sql(""" select phone from tabAddress where name='{0}' """.format(address_dict), as_dict=1)
    return phone[0].get("phone")
@frappe.whitelist()
def get_phone_number_and_email_from_address(address_dict):
    if not address_dict:
        return
    contact_details = frappe.db.sql(""" select phone,email_id from tabAddress where name='{0}' """.format(address_dict), as_dict=1)
    return {"phone":contact_details[0].get("phone"),"email":contact_details[0].get("email_id")}
@frappe.whitelist()
def get_final_check_result(doctype, fields=None, filters=None, order_by=None,limit_start=None, limit_page_length=20, parent=None,inspection_type=None):
    filters = ast.literal_eval(filters)
    where_string = ""
    for key,value in filters.iteritems():
        where_string += " `%s`%s'%s' and" % (key,value[0],value[1])
    where_string = where_string[:-3]
    checks_sql = """ select {0} from `{1}` where {2} """.format(fields,doctype,where_string)
    checks_result = frappe.db.sql(checks_sql, as_dict=1)
    return checks_result

@frappe.whitelist()
def get_phone_number_and_email_from_so(sales_order=None):
    res = {}
    if sales_order:
        res_sql = """ select customer_address from `tabSales Order` where name='%s' """ % (sales_order)
        address_dict = frappe.db.sql(res_sql,as_dict=1)
        res = get_phone_number_and_email_from_address(address_dict[0].get("customer_address"))
    return res

@frappe.whitelist()
def get_so_details_from_so(sales_order=None):
    res = {}
    #sales_order = "SO-Amazon-00631"
    if sales_order:
        res_sql = """ select soi.item_code as item_code,so.customer_address as customer_address from `tabSales Order` so inner join `tabSales Order Item` soi on soi.parent=so.name where so.name='%s' """ % (sales_order)
        address_dict = frappe.db.sql(res_sql,as_dict=1)
        res = get_phone_number_and_email_from_address(address_dict[0].get("customer_address"))
        res["item_code"] = address_dict[0].get("item_code")
    return res

@frappe.whitelist()
def get_matched_item(ram=None,hdd=None,item=None):
    if ram=='0 GB' and hdd=='0 GB':
	return item
    vwrite("In get_matched_item")
    vwrite("RAM: %s, HDD: %s" %(ram,hdd))
    # ram = "-2 GB"
    # hdd = "-160 GB"
    # item = "Refurbished Lenovo Thinkpad-L420-4 GB-320 GB"
    # item = """Refurbished Lenovo Thinkpad-L420-2 GB-160 GB"""
    # get variant attributes of item
    item_attr_sql = """ select iva.attribute,iva.attribute_value,i.variant_of from `tabItem Variant Attribute` iva inner join `tabItem` i on i.item_code=iva.parent where iva.parent='%s' """ % (item)
    item_attr_dict = frappe.db.sql(item_attr_sql,as_dict=1)
    variant_of = item_attr_dict[0].get("variant_of")
    condition = []
    hdd_value = 0
    for item_attr in item_attr_dict:
        if item_attr.get("attribute") in ["Choose Model","Processor Brand","Processor","ThinkPad Models"]:
            model = item_attr.get("attribute_value")
            abbr = get_item_attribute_abbr(item_attr.get("attribute"),item_attr.get("attribute_value"))
            condition.append(" `parent` like '%s'" %("%"+abbr+"%"))
            # condition.append(" `parent` like '%s'" %("%"+item_attr.get("attribute_value")+"%"))
        if item_attr.get("attribute") in ["Size"]:
            size = item_attr.get("attribute_value")
            condition.append(" `parent` like '%s'" %("%"+item_attr.get("attribute_value")+"%"))
        if item_attr.get("attribute") in ["Hard Disk Capacity","Storage","Harddisk","HardDisk (GB)"]:
            hdd_attr = item_attr.get("attribute")
            hdd_attr_value = item_attr.get("attribute_value")
	    if hdd_attr_value.split(" ")[1]=='TB':
		hdd_attr_value = int(hdd_attr_value.split(" ")[0]) * 1000
	    else:
		hdd_attr_value = hdd_attr_value.split(" ")[0]
            hdd_unit_value = 0
            if " TB" in hdd:
                hdd_arr = hdd.split(" ")
                hdd_unit_value = int(hdd_arr[0]) * 1000
            else:
                hdd_arr = hdd.split(" ")
                hdd_unit_value = hdd_arr[0]
            hdd_value = hdd_value + int(hdd_unit_value)
	    if hdd_attr_value=='NO' or hdd_attr_value=='No':
		hdd_attr_value = 0
            hdd_value = hdd_value + int(hdd_attr_value)
            if(hdd_value>=1000):
                hdd_value = hdd_value/1000
                hdd_value = str(hdd_value) + " TB"
            else:
                hdd_value = str(hdd_value) + " GB"
            total_hdd = hdd_value.split(" ")[0]
            if int(total_hdd)>0:
                condition.append(" `parent` like '%s' " %("%-"+str(hdd_value)+"%"))
            else:
                condition.append(" `parent` like '%NO HARD%' ")
        if item_attr.get("attribute") in ["RAM"]:
            ram_attr = item_attr.get("attribute")
            ram_attr_value = item_attr.get("attribute_value")
            ram_attr_value = ram_attr_value.split(" ")[0]
            ram_arr = ram.split(" ")
	    if ram_arr[0]=='NO' or ram_arr[0]=='No':
		ram_val = 0
	    else:
		ram_val = ram_arr[0]
	    if ram_attr_value=='NO' or ram_attr_value=='No':
		ram_attr_value=0
            total_ram = int(ram_attr_value) + int(ram_val)
            if total_ram>0:
                condition.append(" `parent` like '%s' " %("%-"+str(total_ram)+" GB%"))
            else:
                condition.append(" `parent` like '%NO RAM%' " )
    if len(condition):
        where_string = " where " + " and ".join(condition)
    # match_sql = """ select item_code from `tabItem` where item_code like '{0}' and variant_of='{1}'  """.format("%"+model+"%",variant_of)
    # print match_sql
    match_sql = """ select parent from `tabItem Variant Attribute` {0} """.format(where_string)
    vwrite("match_sql")
    vwrite(match_sql)
    match_dict = frappe.db.sql(match_sql,as_dict=1)
    for match in match_dict:
        match_variant = get_variant_of(match.get("parent"))
        input_variant = get_variant_of(item)
        if match_variant==input_variant:
            return match.get("parent")
    # print (match_dict[0].get("parent"))
    # return match_dict[0].get("parent")
    # print item_attr_dict

def get_variant_of(item):
    variant_sql = """ select variant_of from `tabItem` where item_code='{0}' """.format(item)
    variant_dict = frappe.db.sql(variant_sql,as_dict=1)
    return variant_dict[0].get("variant_of")

@frappe.whitelist()
def get_item_attribute_abbr(attr=None,attr_val=None):
    #attr='Processor'
    #attr_val = 'Intel Core I5'
    abbr_sql = """ select abbr from `tabItem Attribute Value` where attribute_value='{0}' and parent='{1}'""".format(attr_val,attr)
    abbr_dict = frappe.db.sql(abbr_sql,as_dict=1)
    abbr = abbr_dict[0].get("abbr")
    return abbr
