from __future__ import unicode_literals
import frappe
from frappe import _
import frappe.model
import frappe.utils
import json
import os
import datetime
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

    if info["order_id"] and info['order_id'] != "":
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

    customer_addres_doc_name_from_serial_no_query = """select so.customer_address from `tabDelivery Note Item`  as dni inner join `tabDelivery Note` as dn on dn.name = dni.parent inner join `tabSales Order` as so on so.name = dni.against_sales_order where dni.serial_no like "%%{0}%%" and dn.docstatus = 1 order by dni.creation DESC LIMIT 1""".format(info['serial_no'].strip())
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

@frappe.whitelist(allow_guest=True)
def is_item_with_customer(info):
    info = ast.literal_eval(info)
    if info["serial_no"] != "":
        check_query = """select warehouse from `tabSerial No` where name = '{0}'""".format(info['serial_no'])
        warehouse_name = frappe.db.sql(check_query,as_dict=1)
        if warehouse_name and warehouse_name[0]['warehouse'] is None:
            return {
                "status": True
            }
        else:
            return {
                "status": False            
            }

    else:
        return {
            "status":False,
            "Error":"No serial Number provided"
        }
@frappe.whitelist(allow_guest=True)
def useractioninfo(info):
    import datetime
    # Indian time is ahead of UTC by 5 hours and 30 minutes.
    current_time = str(datetime.datetime.now() + datetime.timedelta(hours = 5, minutes=30))
    info = ast.literal_eval(info)
    # info['process']  = ["Installation", "Initiation","Uninstallation"]
    if info['process'] == "":
        return {
            "Status": False,
            "Serial Number": info["serial_no"]
        }
    if info['serial_no'] != "":
       update_table(current_time,info['serial_no'],info['process'])
    return {
        "Status":info['process'].upper(),
        "Serial Number": info["serial_no"]
    }

def update_table(current_time, serial_no, process):
    process_to_column_map = {
        "installation" : "installation_time",
        "initiation" : "initiation_time",
        "uninstallation" : "uninstallation_time"
    }
    # info['process']  = ["Installation", "Initiation","Uninstallation"]
    update_query = """update `tabSerial No` set {0} = '{1}' where name = '{2}'""".format(process_to_column_map[process],current_time,serial_no)
    frappe.db.sql(update_query,as_dict=1)
    frappe.db.commit()