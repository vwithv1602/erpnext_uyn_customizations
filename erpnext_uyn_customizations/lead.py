# -*- coding: utf-8 -*-
from __future__ import unicode_literals

__version__ = '1.1'

import frappe,json
from frappe import _
from vlog import vwrite

@frappe.whitelist()
def check_if_lead_exists(mobile=None,email=None):
    lead_doc = None
    if mobile:
        try:
            lead_doc = frappe.get_doc("Lead", {"mobile_no": mobile})
            if lead_doc:
                lead_doc.status = "Converted"
                lead_doc.flags.ignore_mandatory = True
                lead_doc.save(ignore_permissions=True)
        except Exception, e:
            vwrite("Exception raised in lead.py > check_if_lead_exists() - can't find mobile")
            vwrite(e.message)
    else:
        if email:
            try:
                lead_doc = frappe.get_doc("Lead", {"email_id": email})
                if lead_doc:
                    lead_doc.status = "Converted"
                    lead_doc.flags.ignore_mandatory = True
                    lead_doc.save(ignore_permissions=True)
            except Exception, e:
                vwrite("Exception raised in lead.py > check_if_lead_exists() - can't find email")
                vwrite(e.message)
    