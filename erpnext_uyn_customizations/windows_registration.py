from __future__ import unicode_literals
import frappe
from frappe import _
import frappe.model
import frappe.utils
import json
import os
import re
import ast
from erpnext_ebay.vlog import vwrite

@frappe.whitelist(allow_guest=True)
def registration(info):
    vwrite(info)
    if not validate(info):
        return {
                'status':False
            }
    
    amazon_sales_order_id = frappe.db.get_value("Sales Order", {'amazon_order_id':info["order_id"]}, 'name')
    flipkart_sales_order_id = frappe.db.get_value("Sales Order", {'flipkart_order_id':info["order_id"]}, 'name')

    if not amazon_sales_order_id or flipkart_sales_order_id:
        return {
            'status': False,
            'error': "Sales Order Not Found."
        }
    sales_order_doc = frappe.get_doc("Sales Order", amazon_sales_order_id or flipkart_sales_order_id)
    customer_address_doc_name = sales_order_doc.customer_address
    if not customer_address_doc_name:
        return {
            'status':False,
            'error': "Address not found"
        }
    customer_address_doc = frappe.get_doc("Address", customer_address_doc_name)
    customer_address_doc.email_id = info['email_id']
    customer_address_doc.phone = info['phone']
    customer_address_doc.save()
    
def validate(info):
    key_to_function_map = {
        "phone": validate_phone_number,
        "email_id": validate_email_id
    }
    for key in info:
        if key in key_to_function_map:
            is_validated = key_to_function_map[key](info[key])
            if not is_validated:
                return False
    
    return True

def validate_phone_number(phone):
    validator = re.compile("^\d{10}$")
    return bool(validator.match(phone))

def validate_email_id(email_id):
    validator = re.compile("[^@]+@[^@]+\.[^@]+")
    return bool(validator.match(email_id))
