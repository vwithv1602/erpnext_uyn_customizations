from __future__ import unicode_literals
from datetime import datetime,timedelta
import frappe
from frappe import _
from .flipkart_requests import get_request
from .flipkart_exceptions import FlipkartError
from parse_erpnext_connector.parse_orders import parse_order
from .flipkart_utils import make_flipkart_log
from .sync_flipkart_customers import create_customer,create_customer_address,create_customer_contact
from frappe.utils import flt, nowdate, cint
from .vlog import vwrite

flipkart_settings = frappe.get_doc("Flipkart Settings", "Flipkart Settings")
if flipkart_settings.last_sync_datetime:
    startTimeString = flipkart_settings.last_sync_datetime
    startTimeString = startTimeString[:19]
    startTimeObj = datetime.strptime(startTimeString, '%Y-%m-%d %H:%M:%S')
    startTime = (startTimeObj + timedelta(-1)).isoformat()
else:
    startTime = (datetime.now() + timedelta(-1)).isoformat()
endTime = datetime.now().isoformat()

def get_flipkart_orders(ignore_filter_conditions=False):
    flipkart_orders = []
    params = {}
    flipkart_orders = get_request('list_orders', params)
    return flipkart_orders

@frappe.whitelist()
def sync_flipkart_orders():
    # frappe.local.form_dict.count_dict["orders"] = 0
    get_flipkart_orders_array = get_flipkart_orders()
    if not len((get_flipkart_orders_array)):
        vwrite("No orders received")
        return False
    for flipkart_order in get_flipkart_orders_array:
        params = {'shipmentId':flipkart_order.get("shipmentId")}
        shipment_id_details = get_request('shipment_id_details',params)
        order_item_details = {
            'flipkart_order':flipkart_order,
            'shipment_id_details':shipment_id_details
        }
        parsed_order = parse_order("flipkart",order_item_details)
        if parsed_order:
            flipkart_item_id = parsed_order.get("item_details").get("item_id")
            is_item_in_sync = check_flipkart_sync_flag_for_item(flipkart_item_id)
            if(is_item_in_sync):
                if valid_customer_and_product(parsed_order):
                    try:
                        create_order(parsed_order, flipkart_settings)
                        # frappe.local.form_dict.count_dict["orders"] += 1
                    except FlipkartError, e:
                        vwrite("FlipkartError raised in create_order")
                        make_flipkart_log(status="Error", method="sync_flipkart_orders", message=frappe.get_traceback(),request_data=flipkart_order.get("OrderID"), exception=True)
                    except Exception, e:
                        vwrite("Exception raised in create_order")
                        vwrite(e)
                        vwrite(parsed_order)
                        if e.args and e.args[0]:
                            raise e
                        else:
                            make_flipkart_log(title=e.message, status="Error", method="sync_flipkart_orders", message=frappe.get_traceback(), request_data=flipkart_order.get("OrderID"), exception=True)
                else:
                    vwrite("Not valid customer and product")
            else:
                vwrite("Item not in sync: %s" % flipkart_item_id)
                make_flipkart_log(title="%s" % flipkart_item_id, status="Error", method="sync_flipkart_orders", request_data=flipkart_order,message="Sales order item is not in sync with erp. Sales Order: %s " % flipkart_order.get("orderItems")[0].get("orderId"))
        else:
            vwrite("Parsing failed for %s" % flipkart_order.get("orderItems")[0].get("orderId"))
            make_flipkart_log(title="%s" % flipkart_order.get("orderItems")[0].get("orderId"), status="Error", method="sync_flipkart_orders",request_data=flipkart_order,message="Parsing failed for Sales Order: %s " % flipkart_order.get("orderItems")[0].get("orderId"))

@frappe.whitelist()
def sync_flipkart_qty():
    vwrite("Im in sync_flipkart_qty")

def check_flipkart_sync_flag_for_item(flipkart_product_id):
    sync_flag = False
    sync_flag_query = """select sync_with_flipkart from tabItem where flipkart_product_id='%s' or flipkart_product_id like '%s' or flipkart_product_id like '%s' or flipkart_product_id like '%s'""" % (flipkart_product_id,flipkart_product_id+",%","%,"+flipkart_product_id+",%","%,"+flipkart_product_id)
    try:
        for item in frappe.db.sql(sync_flag_query, as_dict=1):
            if item.get("sync_with_flipkart"):
                sync_flag = True
            else:
                sync_flag = False
    except Exception, e:
        vwrite("Exception raised in check_flipkart_sync_flag_for_item")
        vwrite(e)
    return sync_flag

def valid_customer_and_product(parsed_order):
    flipkart_order = None
    customer_id = parsed_order.get("customer_details").get("buyer_id")
    if customer_id:
        if not frappe.db.get_value("Customer", {"flipkart_customer_id": customer_id}, "name"):
            create_customer(parsed_order, flipkart_customer_list=[])
        else:
            create_customer_address(parsed_order, customer_id)
            create_customer_contact(parsed_order, customer_id)

    else:
        raise _("Customer is mandatory to create order")

    warehouse = frappe.get_doc("Flipkart Settings", "Flipkart Settings").warehouse
    return True
    
def create_order(parsed_order, flipkart_settings, company=None):
    so = create_sales_order(parsed_order, flipkart_settings, company)
    # if flipkart_order.get("financial_status") == "paid" and cint(flipkart_settings.sync_sales_invoice):
    #     create_sales_invoice(flipkart_order, flipkart_settings, so)
    #
    # if flipkart_order.get("fulfillments") and cint(flipkart_settings.sync_delivery_note):
    #     create_delivery_note(flipkart_order, flipkart_settings, so)


def create_sales_order(parsed_order, flipkart_settings, company=None):
    so = frappe.db.get_value("Sales Order", {"flipkart_order_id": parsed_order.get("order_details").get("order_id")}, "name")
    if not so:
        order_date = parsed_order.get("order_details").get("order_date")
        transaction_date = datetime.strptime(str(order_date)[:10], "%Y-%m-%d")
        delivery_date = transaction_date + timedelta(days=4)
        # get oldest serial number and update in tabSales Order
        # serial_number = get_oldest_serial_number(parsed_order.get("item_details").get("item_id")) # sending flipkart_product_id
        serial_number = None
        try:
            if parsed_order.get("order_details").get("payment_method")=='COD':
                is_cod = True
            else:
                is_cod = False
            if 'fulfillment_channel' in parsed_order.get("order_details"):
                fulfillment_channel = parsed_order.get("order_details").get("fulfillment_channel")
            else:
                fulfillment_channel = ""
            if parsed_order.get("order_details").get("is_flipkart_replacement")=='true':
                is_flipkart_replacement = True
            else:
                is_flipkart_replacement = False
            so = frappe.get_doc({
                "doctype": "Sales Order",
                "naming_series": flipkart_settings.sales_order_series or "SO-Flipkart-",
                "is_cod": is_cod,
                "flipkart_order_id": parsed_order.get("order_details").get("order_id"),
		"flipkart_buyer_id": parsed_order.get("customer_details").get("buyer_id"),
                "customer": frappe.db.get_value("Customer",
                                                {"flipkart_customer_id": parsed_order.get("customer_details").get("buyer_id")}, "name"),
                "delivery_date": delivery_date,
                "transaction_date": parsed_order.get("order_details").get("order_date")[:10],
                "company": flipkart_settings.company,
                "selling_price_list": flipkart_settings.price_list,
                "ignore_pricing_rule": 1,
                "items": get_order_items(parsed_order.get("item_details").get("all_items"), flipkart_settings,parsed_order),                
                "item_serial_no": serial_number,
                "fulfillment_channel": fulfillment_channel,
                "is_flipkart_replacement":is_flipkart_replacement
                # "taxes": get_order_taxes(flipkart_order.get("TransactionArray").get("Transaction"), flipkart_settings),
                # "apply_discount_on": "Grand Total",
                # "discount_amount": get_discounted_amount(flipkart_order),
            })
            # if "Certified Refurbished" in so.__dict__.get("items")[0].__dict__.get("item_name"):
            #     so.update({
            #         "mail_to_flipkart_buyer":1
            #     })
            if company:
                so.update({
                    "company": company,
                    "status": "Draft"
                })
            so.flags.ignore_mandatory = True
            try:
                so.save(ignore_permissions=True)
            except Exception, e:
                vwrite("in exception")
                vwrite(e)
            return False
            if(parsed_order.get("order_details").get("parent_order_id") != 0):
                # variation_details = get_variation_details(flipkart_order.get("TransactionArray").get("Transaction")[0])
                variation_details = parsed_order.get("order_details").get("parent_order_id") # yet to find variation details parameter in flipkart
                created_so_id = frappe.db.get_value("Sales Order",{"flipkart_order_id": parsed_order.get("order_details").get("order_id")}, "name")
                update_wrnty_in_desc_query = """ update `tabSales Order Item` set description='%s' where parent='%s'""" % (variation_details,created_so_id)
                update_wrnty_in_desc_result = frappe.db.sql(update_wrnty_in_desc_query, as_dict=1)
            # so.submit()
        except FlipkartError, e:
            vwrite("FlipkartError raised in create_sales_order")
            make_flipkart_log(title=e.message, status="Error", method="create_sales_order", message=frappe.get_traceback(),
                          request_data=parsed_order.get("order_details").get("order_id"), exception=True)
        except Exception, e:
            vwrite("Exception raised in create_sales_order")
            vwrite(e)
            vwrite(parsed_order)
            if e.args and e.args[0]:
                raise e
            else:
                make_flipkart_log(title=e.message, status="Error", method="create_sales_order",
                              message=frappe.get_traceback(),
                              request_data=parsed_order.get("order_details").get("order_id"), exception=True)
    else:
        so = frappe.get_doc("Sales Order", so)
    frappe.db.commit()
    return so

def get_order_items(order_items, flipkart_settings,parsed_order):
    items = []
    for flipkart_item in order_items:
        # if('Variation' in flipkart_item):
        if False: # yet to find parameter to find varaint items
            item_code = get_variant_item_code(flipkart_item)
            if item_code == None:
                # check if item is mapped to non-variant item
                item_code = get_item_code(flipkart_item)
                if item_code == None:
                    make_flipkart_log(title="Variant Item not found", status="Error", method="get_order_items",
                              message="Variant Item not found for %s" %(flipkart_item.get("Item").get("ItemID")),request_data=flipkart_item.get("Item").get("ItemID"))
        else:
            item_code = get_item_code(flipkart_item)
            if item_code == None:
                make_flipkart_log(title="Item not found", status="Error", method="get_order_items",
                              message="Item not found for %s" %(flipkart_item.get("Item").get("ItemID")),request_data=flipkart_item.get("Item").get("ItemID"))
        try:
            if not parsed_order.get("order_details").get("amount"):
                rate = 0
            else:
                rate = float(parsed_order.get("order_details").get("amount"))/float(flipkart_item.get("quantity"))
        except Exception, e:
            vwrite("Exception raised in get_order_items")
            vwrite(e)
            vwrite(parsed_order.get("order_details").get("amount"))
        items.append({
            "item_code": item_code,
            "item_name": flipkart_item.get("title")[:140],
            "rate": float(parsed_order.get("order_details").get("amount"))/float(flipkart_item.get("quantity")),
            "qty": flipkart_item.get("quantity"),
            # "stock_uom": flipkart_item.get("sku"),
            "warehouse": flipkart_settings.warehouse
        })
    return items

def get_variant_item_code(flipkart_item):
    # item = frappe.get_doc("Item", {"flipkart_product_id": flipkart_item.get("Item").get("ItemID")})
    # item_code = item.get("item_code")
    item_id = flipkart_item.get("Item").get("ItemID")
    item_code_query = """ select item_code from `tabItem` where flipkart_product_id='%s' or flipkart_product_id like '%s' or flipkart_product_id like '%s' or flipkart_product_id like '%s'""" % (
    item_id, item_id+",%", "%,"+item_id+",%", "%,"+item_id)
    item_code_result = frappe.db.sql(item_code_query, as_dict=1)
    if len(item_code_result) > 1:
        # getting non-variant item - erpnext_flipkart/issue#4
        filter_query = """ select item_code from `tabItem` where variant_of is null and (flipkart_product_id='%s' or flipkart_product_id like '%s' or flipkart_product_id like '%s' or flipkart_product_id like '%s')""" % (
        item_id, item_id + ",%", "%," + item_id + ",%", "%," + item_id)
        filter_result = frappe.db.sql(filter_query, as_dict=1)
        item_code = filter_result[0].get("item_code")
    else:
        item_code = item_code_result[0].get("item_code")
    variant_items_query = """ select item_code from `tabItem` where variant_of='%s'""" % (item_code)
    variant_items_result = frappe.db.sql(variant_items_query, as_dict=1)
    all_variation_specifics = flipkart_item.get("Variation").get("VariationSpecifics").get("NameValueList")
    variation_specifics = []
    if (type(all_variation_specifics) is dict):
        if 'warranty' not in all_variation_specifics.get("Name").lower():
            variation_specifics.append(all_variation_specifics)
    else:
        for required_variation_specifics in all_variation_specifics:
            # if required_variation_specifics.get("Name").lower()!='warranty':
            if 'warranty' not in required_variation_specifics.get("Name").lower():
                variation_specifics.append(required_variation_specifics)
    for variant_item in variant_items_result:
        # get records from tabItemVariantAttributes where parent=variant_item
        variant_attributes_query = """ select * from `tabItem Variant Attribute` where parent='%s' and attribute != 'Warranty'""" % (variant_item.get("item_code"))
        variant_attributes_result = frappe.db.sql(variant_attributes_query, as_dict=1)
        # >> flipkart may have extra attributes which we won't consider in erp, so removing equal length condition
        # if len(variant_attributes_result)==len(variation_specifics):
        #     # for each variation specific, compare with result row
        #     matched = 0
        #     for variation_specific in variation_specifics:
        #         for variant_attributes_row in variant_attributes_result:
        #             if((variant_attributes_row.get("attribute").lower()==variation_specific.get("Name").lower()) and (variant_attributes_row.get("attribute_value").lower()==variation_specific.get("Value").lower())):
        #                 matched = matched+1
        #             if len(variation_specifics)==matched:
        #                 return variant_item.get("item_code")
        matched = 0
        for variant_attributes_row in variant_attributes_result:
            for variation_specific in variation_specifics:
                if ((variant_attributes_row.get("attribute").lower() == variation_specific.get("Name").lower()) and (
                    variant_attributes_row.get("attribute_value").lower() == variation_specific.get("Value").lower())):
                    matched = matched + 1
        if len(variant_attributes_result) == matched:
            return variant_item.get("item_code")
            # << flipkart may have extra attributes which we won't consider in erp, so removing equal length condition
    return None

def get_item_code(flipkart_item):
    # item_code = frappe.db.get_value("Item", {"flipkart_variant_id": flipkart_item.get("variant_id")}, "item_code")
    item_code = False
    if not item_code:
        # item_code = frappe.db.get_value("Item", {"flipkart_product_id": flipkart_item.get("Item").get("ItemID")}, "item_code")
        item_id = flipkart_item.get("fsn")
        item_code_query = """ select item_code from `tabItem` where flipkart_product_id='%s' or flipkart_product_id like '%s' or flipkart_product_id like '%s' or flipkart_product_id like '%s'""" % (item_id,item_id+",%","%,"+item_id+",%","%,"+item_id)
        item_code_result = frappe.db.sql(item_code_query, as_dict=1)
        if len(item_code_result)>1:
            # getting non-variant item - erpnext_flipkart/issue#4
            filter_query = """ select item_code from `tabItem` where variant_of is null and (flipkart_product_id='%s' or flipkart_product_id like '%s' or flipkart_product_id like '%s' or flipkart_product_id like '%s')""" % (item_id,item_id+",%","%,"+item_id+",%","%,"+item_id)
            filter_result = frappe.db.sql(filter_query, as_dict=1)
            item_code = filter_result[0].get("item_code")
        else:
            if len(item_code_result):
                item_code = item_code_result[0].get("item_code")
    return item_code
