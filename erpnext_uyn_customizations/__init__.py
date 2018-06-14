# -*- coding: utf-8 -*-
from __future__ import unicode_literals

__version__ = '1.1'

import frappe,json
from frappe import _
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