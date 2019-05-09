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
#from parse_erpnext_connector import parse_quality_inspection_report
from erpnext_ebay.vlog import vwrite

@frappe.whitelist()
def testping(allow_guest=True):
    return "testing ping response"
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
    # filters = ast.literal_eval(filters)
    filters = json.loads(filters)
    where_string = ""
    for filter_value in filters:
        for key,value in filter_value.iteritems():
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
		hdd_attr_value = float(hdd_attr_value.split(" ")[0]) * 1000
	    else:
		hdd_attr_value = hdd_attr_value.split(" ")[0]
            hdd_unit_value = 0
            if " TB" in hdd:
                hdd_arr = hdd.split(" ")
                hdd_unit_value = float(hdd_arr[0]) * 1000
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

@frappe.whitelist()
def get_stock_balance(warehouses=[],items=[]):
    # used to get stock balance for selected items with warehouse filter
    items = ast.literal_eval(items)
    from datetime import datetime,timedelta
    today = datetime.today()
    to_date = str(datetime.today())[:10]
    start_date = today - timedelta(365)
    from_date = str(start_date)[:10]
    filters = {'from_date':from_date,'to_date':to_date}
    from erpnext.stock.report.stock_balance.stock_balance import get_stock_ledger_entries,get_item_warehouse_map
    sle = get_stock_ledger_entries(filters,items)
    iwb_map = get_item_warehouse_map(filters,sle)
    result = {}
    for (company, item, warehouse) in sorted(iwb_map):
        qty_dict = iwb_map[(company, item, warehouse)]
        if qty_dict.get("bal_qty")>0:
            if not result.get(item):
                result[item] = []
            result[item].append({'warehouse':warehouse,'bal_qty':qty_dict.get("bal_qty")})
    return result

@frappe.whitelist()
def get_spreadsheet_data(spreadsheet_id=None,sheet_name=None):
    vwrite("in get_spreadsheet_data")
    vwrite("%s %s" %(spreadsheet_id,sheet_name))
    import gspread
    from oauth2client.service_account import ServiceAccountCredentials
    scope = ['https://spreadsheets.google.com/feeds','https://www.googleapis.com/auth/drive']
    credentials = ServiceAccountCredentials.from_json_keyfile_name("/home/frappe/frappe-bench/apps/erpnext_uyn_customizations/erpnext_uyn_customizations/usedyetnew-197716-ef945772629c.json",scope)

    gc = gspread.authorize(credentials)

    # wks = gc.open('gSpreadTest').sheet1
    try:
        # wks = gc.open_by_key('1kGiCe4CjMMduGvhCxOCVWgbsLmWVsCFTJOmGUiEpPO0').sheet1
        sh = gc.open_by_key(spreadsheet_id)
        wks = sh.worksheet(sheet_name)
        result = wks.get_all_records()
        return result
    except Exception, e:
        print "Exception raised in opening worksheet"
        error = ast.literal_eval(e.message)
        return error

@frappe.whitelist()
def import_data(doc):
    vwrite("inside import_data")
    vwrite("1")
    doc = ast.literal_eval(doc)
    vwrite("2")
    spreadsheet_id = doc.get("spreadsheet_id")
    vwrite("3")
    sheet_name = doc.get("sheet_name")
    vwrite("4")
    spreadsheet_data = get_spreadsheet_data(spreadsheet_id,sheet_name)
    vwrite("5")
    mapper = doc.get("mapper")
    for data in spreadsheet_data:
	vwrite(data)
        update_string = ""
        for map in mapper:
            if "field_name" in map:
                column_name = map.get("column_name").strip()
                field_name = map.get("field_name")
                target_doctype = map.get("target_doctype")
                foreign_key = map.get("foreign_key")
                primary_key = map.get("primary_key")
                formatted_data = {}
                for k,d in data.iteritems():
                    key = k.strip()
                    formatted_data[key] = d
                field_value = formatted_data[column_name]
                primary_key_value = formatted_data[primary_key]
                if field_name:
                    update_string += " `{0}`='{1}',".format(field_name,field_value)
        update_string = update_string[:-1]
        sql = "Update `tab{1}` set {0} where `{2}`='{3}'".format(update_string,target_doctype,foreign_key,primary_key_value)
	vwrite(sql)
        qry = frappe.db.sql(sql,as_dict=1)
    return "OK"

@frappe.whitelist()
def get_initial_condition(barcode):
    col_sql = """ SELECT GROUP_CONCAT(`COLUMN_NAME` SEPARATOR ', ') as req_cols FROM `INFORMATION_SCHEMA`.`COLUMNS` WHERE `TABLE_SCHEMA`='1bd3e0294da19198' AND `TABLE_NAME`='tabSerial No' and `COLUMN_NAME` like 'initial_%' """
    col_qry = frappe.db.sql(col_sql,as_dict=1)
    req_cols = col_qry[0].get("req_cols")
    sql = """ select {0} from `tabSerial No` where name='{1}' """.format(req_cols,barcode)
    qry = frappe.db.sql(sql, as_dict=1)
    initial_condition = ""
    for k,v in qry[0].iteritems():
        if v:
            initial_condition += "<b>{0}</b>: {1} <br>".format(k,v)
    initial_condition = initial_condition.replace('_',' ').upper()
    return initial_condition

@frappe.whitelist()
def filter_gst_non_gst_in_po(doc,supplier_quotation,po_for,is_gst):
    sql = """ select name,is_gst from `tabSupplier Quotation Item` where parent='{0}' """.format(supplier_quotation)
    items = []
    for item in frappe.db.sql(sql,as_dict=1):
        vwrite("%s - %s" %(int(is_gst),int(item.get("is_gst"))))
        if int(item.get("is_gst"))==int(is_gst):
            items.append(item.get("name"))
    return items

@frappe.whitelist()
def purchase_order_for_supplier_quotation(supplier_quotation):
    sql = """ select po.name,po.gst,po.docstatus from `tabPurchase Order` po inner join `tabPurchase Order Item` poi on poi.parent=po.name where poi.supplier_quotation='%s' """ % supplier_quotation
    return frappe.db.sql(sql,as_dict=1)

@frappe.whitelist()
def get_place_of_supply_for_si(so):
    place_of_supply_sql = """ select state from tabAddress where name=(select customer_address from `tabSales Order` where name='%s') """ %(so)
    place_of_supply_res = frappe.db.sql(place_of_supply_sql,as_dict=1)
    return place_of_supply_res[0].get("state")

@frappe.whitelist()
def can_save_mreq(logged_in_user,against_serial_no=None):
    vwrite("in can_save_mreq by: %s"%logged_in_user)
    # This function accepts logged_in_user,against_serial_no and will return true or false based on the below condition.
    # Irrespective of mreq status (closed/pending/ordered), if a material request is present against a serial no. block further requests.
    # Allow only authorized persons (having role - Material Request Manager) to raise material request
    if ('Material Request Manager' in frappe.get_roles(logged_in_user)):
        return {"access":""}
    mr_for_item_against_sno_sql = """ select mr.status,mri.name,mri.parent from `tabMaterial Request Item` mri inner join `tabMaterial Request` mr on mr.name=mri.parent where mri.serial_no='{0}' and mri.docstatus=1 and mr.status in ('Ordered','Partially Ordered','Stopped') """.format(against_serial_no)
    vwrite(mr_for_item_against_sno_sql)
    mr_for_item_against_sno_res = frappe.db.sql(mr_for_item_against_sno_sql,as_dict=1)
    if len(mr_for_item_against_sno_res):
        prev_mr = mr_for_item_against_sno_res[0].get("parent")
        msg = "You have already raised %s. So you can't raise another MR. Please contact your manager" % prev_mr
        return {"access":msg}
    return {"access":""}

def get_tech_repack_pending_doc(serial_no):
    return frappe.get_list("Tech Repack", filters={'docstatus': 1,'status': 'Pending', 'barcode': serial_no},fields=['name','owner'])

@frappe.whitelist()
def check_pending_tech_repack(serial_nos):

    serial_no_list = serial_nos.strip().split(',')
    result = []
    for serial_no in serial_no_list:
        tech_repack_pending_doc_list = get_tech_repack_pending_doc(serial_no)
        if not tech_repack_pending_doc_list:
            continue
        else:
            result.extend(tech_repack_pending_doc_list)
    
    return result

@frappe.whitelist()
def get_future_stock_entry(serial_nos, posting_date, posting_time):
    
    result = {}
    future_sle_query = """select name from `tabStock Ledger Entry` where serial_no like '%%{}%%' and posting_date >= '{}' and posting_time > '{}'"""
    for serial_no in serial_nos:
        current_serial_no_query = future_sle_query.format(serial_no, posting_date, posting_time)
        stock_ledger_entry_list = frappe.db.sql(current_serial_no_query, as_list=1)
        if len(stock_ledger_entry_list) > 0:
            result['status'] = False
            return result
    result['status'] = True
    return result