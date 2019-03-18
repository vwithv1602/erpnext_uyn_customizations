# -*- coding: utf-8 -*-
from __future__ import unicode_literals

__version__ = '1.1'

import frappe,json
from frappe import _, _dict
from vlog import vwrite

@frappe.whitelist()
def lead_conversion(so,method):
    so = so.__dict__
    try:
        customer = so.get("customer")
        address_query = """ select * from tabAddress where address_title='%s' order by creation desc
        """ % customer
        address_result = frappe.db.sql(address_query, as_dict=1)
        if len(address_result)>0: 
            address = address_result[0]
            email = address.get("email_id")
            mobile = address.get("phone")
            from lead import check_if_lead_exists
            check_if_lead_exists(mobile,email)
        else:
            vwrite("No address found for customer: %s" % customer)
    except Exception, e:
        vwrite("Exception occurred in lead_conversion")
        vwrite(so)
        vwrite(e.message)

@frappe.whitelist(allow_guest=True)
def api():
    api_path = frappe.local.form_dict.get("api_path")
    # api_path = 'get_all_material_requests'
    from uyn_api import get_all_material_requests
    def f(api_path):
        paths = {
            'get_all_material_requests': get_all_material_requests()
        }
        if api_path in paths:
            result = paths[api_path]
        else:
            result = []
        return result
    return f(api_path)

@frappe.whitelist(allow_guest=True)
def default_api():
    raw_query = frappe.local.form_dict.get("raw_query")
    raw_query = raw_query.replace("&gt;", ">").replace("&lt;", "<")
    vwrite("default_api raw_query")
    vwrite(raw_query)
    if len(raw_query):
        return frappe.db.sql(raw_query,as_dict=1)
    doctype = frappe.local.form_dict.get("doctype")
    fields = frappe.local.form_dict.get("fields")
    filters = frappe.local.form_dict.get("filters")
    limit = frappe.local.form_dict.get("limit")
    order_by = frappe.local.form_dict.get("order_by")
    where_string = ""
    if len(filters):
        where_string = " where {0} ".format(filters)
    sql = """ select {0} from `tab{1}` {2} order by {3} limit {4} """.format(fields,doctype,where_string,order_by,limit)
    return frappe.db.sql(sql,as_dict=1)

@frappe.whitelist(allow_guest=True)
def test_stock_bal():
    from erpnext.stock.report.stock_balance.stock_balance import execute
    from datetime import timedelta,datetime
    today = datetime.strptime(datetime.today().strftime('%Y-%m-%d'), '%Y-%m-%d')
    last_month = today - timedelta(31)
    filters = {"from_date":str(last_month)[:10],"to_date":str(today)[:10]}
    result = execute(filters)
    return result


@frappe.whitelist(allow_guest=True)
def uyn_erp_dump_method(method_name,file_name,filters=None):
    myModule = __import__(file_name)
    myFile = myModule.__dict__.get(file_name.rsplit('.', 1)[-1])
    myMethod = myFile.__dict__.get(method_name)
    if filters:
        return myMethod(**filters)
    else:
        return myMethod()

@frappe.whitelist(allow_guest=True)
def get_general_ledger_report():
    from datetime import timedelta,datetime
    today = datetime.strptime(datetime.today().strftime('%Y-%m-%d'), '%Y-%m-%d')
    last_month = today - timedelta(31)
    to_date = str(today)[:10]
    from_date = str(last_month)[:10]
    sql = """ select
        posting_date, account, party_type, party,
        sum(debit) as debit, sum(credit) as credit,
        voucher_type, voucher_no, cost_center, project,
        against_voucher_type, against_voucher,
        remarks, against, is_opening
        from `tabGL Entry`
        where company='Usedyetnew' and posting_date >='%s'
        group by voucher_type, voucher_no, account, cost_center
        order by posting_date, account """ % from_date
    result = frappe.db.sql(sql,as_dict=1)
    i = 0
    from erpnext.accounts.report.general_ledger.general_ledger import get_result_as_list,get_balance
    balance, balance_in_account_currency = 0, 0
    
    result_list = []
    for r in result:
        if not r.get('posting_date'):
			balance, balance_in_account_currency = 0, 0
        balance = get_balance(r, balance, 'debit', 'credit')
        r['balance'] = balance
        if r.posting_date:
            result[i]['posting_date'] = str(r.posting_date)
        result[i]['balance'] = balance
        
        i = i+1
        dictlist = []
        for key, value in r.iteritems():
            dictlist.append(value)
        result_list.append(dictlist)
    col_list = []
    for key,value in result[0].iteritems():
        col_list.append(key)
    return [col_list,result_list]
