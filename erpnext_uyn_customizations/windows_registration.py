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
    info = ast.literal_eval(info)
    
    # Getting the product id for the fulfillment Channel.
    item_code_of_registering_serial_no = frappe.db.get_value("Serial No",{'name': info['serial_no']},'item_code')
    flipkart_product_id = frappe.db.get_value("Item", {'name':item_code_of_registering_serial_no},'flipkart_product_id')
    amazon_product_id = frappe.db.get_value("Item", {'name':item_code_of_registering_serial_no},'amazon_product_id')
    
    # Getting the sales order id for the order id provided.
    amazon_sales_order_id = frappe.db.get_value("Sales Order", {'amazon_order_id':info["order_id"]}, 'name')
    flipkart_sales_order_id = frappe.db.get_value("Sales Order", {'flipkart_order_id':info["order_id"]}, 'name')
    
    fulfillment_channel = frappe.db.get_value("Sales Order",{'name':flipkart_sales_order_id or amazon_sales_order_id},'fulfillment_channel') 
    if not amazon_sales_order_id or flipkart_sales_order_id:
        return {
            'status': False,
            'error': "Sales Order Not Found."
        }
    sales_order_doc = frappe.get_doc("Sales Order", amazon_sales_order_id or flipkart_sales_order_id)
    customer_address_doc_name = sales_order_doc.customer_address
    vwrite(customer_address_doc_name)
    if not customer_address_doc_name:
        return {
            'status':False,
            'error': "Address not found"
        }
    return {
        "status": True,
        "customer_address_doc":customer_address_doc_name,
        "amazon_product_id": amazon_product_id,
        "flipkart_product_id": flipkart_product_id
    }
   
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
