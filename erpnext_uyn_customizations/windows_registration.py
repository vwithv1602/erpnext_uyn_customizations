from __future__ import unicode_literals
import frappe
from frappe import _
import frappe.model
import frappe.utils
import json
import os
import re
import ast
import requests
import lxml
from bs4 import BeautifulSoup
import codecs
from erpnext_ebay.vlog import vwrite

@frappe.whitelist(allow_guest=True)
def registration(info):
    info = ast.literal_eval(info)

    if info["order_id"]:
        # Getting the sales order id for the order id provided.
        amazon_sales_order_id = frappe.db.get_value("Sales Order", {'amazon_order_id':info["order_id"]}, 'name')
        flipkart_sales_order_id = frappe.db.get_value("Sales Order", {'flipkart_order_id':info["order_id"]}, 'name')
        if amazon_sales_order_id or flipkart_sales_order_id:
            sales_order_doc = frappe.get_doc("Sales Order", amazon_sales_order_id or flipkart_sales_order_id)
            customer_address_doc_name = sales_order_doc.customer_address
            if customer_address_doc_name:
                return {
                    'status':True,
                    'customer_address_doc': customer_address_doc_name
                }

    customer_addres_doc_name_from_serial_no_query = """select so.customer_address from `tabDelivery Note Item`  as dni inner join `tabDelivery Note` as dn on dn.name = dni.parent inner join `tabSales Order` as so on so.name = dni.against_sales_order where dni.serial_no like "%%{0}%%" and dn.status = "Completed" order by dni.creation DESC LIMIT 1"""
    check_for_upper_case = customer_addres_doc_name_from_serial_no_query.format(info['serial_no'].strip())

    customer_address_doc_name_dict = frappe.db.sql(customer_addres_doc_name_from_serial_no_query, as_dict=1)
    customer_address_doc_name = customer_address_doc_name_dict[0]['customer_address']
    if customer_address_doc_name:
        return {
            'status':True,
            'customer_address_doc':customer_address_doc_name
        }
    check_for_upper_case = customer_addres_doc_name_from_serial_no_query.format(info['serial_no'].strip().lower())

    customer_address_doc_name_dict = frappe.db.sql(customer_addres_doc_name_from_serial_no_query, as_dict=1)
    customer_address_doc_name = customer_address_doc_name_dict[0]['customer_address']
    if customer_address_doc_name:
        return {
            'status':True,
            'customer_address_doc':customer_address_doc_name
        }
    else:
        return {
            'status': False,
            'error': "Address Could not be found"
        }