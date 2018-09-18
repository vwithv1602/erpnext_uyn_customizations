from __future__ import unicode_literals
import frappe
from frappe import _
from .flipkart_requests import get_request

from vlog import vwrite

def get_flipkart_orders(ignore_filter_conditions=False):
    flipkart_orders = []
    params = {}
    flipkart_orders = get_request('list_orders', params)
    return flipkart_orders

@frappe.whitelist()
def sync_flipkart_orders():
    frappe.local.form_dict.count_dict["orders"] = 0
    get_flipkart_orders_array = get_flipkart_orders()
    if not len((get_flipkart_orders_array)):
        vwrite("No orders received")
        return False
    for flipkart_order in get_flipkart_orders_array:
        vwrite("flipkart_order")
        vwrite(flipkart_order)

@frappe.whitelist()
def sync_flipkart_qty():
    vwrite("Im in sync_flipkart_qty")
