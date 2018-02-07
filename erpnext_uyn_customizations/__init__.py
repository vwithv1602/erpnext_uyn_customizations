# -*- coding: utf-8 -*-
from __future__ import unicode_literals

__version__ = '1.1'

import frappe,json
from frappe import _
from vlog import vwrite

@frappe.whitelist()
def lead_conversion(so,method):
    so = so.__dict__
    customer = so.get("customer")
    address_res = frappe.get_doc("Address", {"address_title": customer})
    address = address_res.__dict__
    email = address.get("email_id")
    mobile = address.get("phone")
    from lead import check_if_lead_exists
    check_if_lead_exists(mobile,email)