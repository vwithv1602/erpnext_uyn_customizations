from __future__ import unicode_literals
import frappe
from frappe import _
from .flipkart_requests import get_request
from parse_erpnext_connector.parse_orders import parse_order
from .flipkart_utils import make_flipkart_log
from vlog import vwrite

def get_flipkart_orders(ignore_filter_conditions=False):
    flipkart_orders = []
    params = {}
    return [{u'subShipments': [{u'packages': [{u'packageSku': u'Very Good - L420', u'dimensions': {u'breadth': 30, u'length': 50, u'weight': 2, u'height': 10}, u'packageId': u'PKGCTFF8YNQ8UQGPMESANHZL9'}], u'subShipmentId': u'SS-1'}], u'dispatchByDate': u'2018-09-18T10:00:00.000+05:30', u'shipmentId': u'387b9edb-f31e-4ed6-995f-a523f29c495d', u'forms': [], u'shipmentType': u'NORMAL', u'locationId': u'LOCa4858b6869c6488c831139a59e5af401', u'dispatchAfterDate': u'2018-09-16T15:05:08.000+05:30', u'updatedAt': u'2018-09-17T17:52:29.000+05:30', u'hold': False, u'orderItems': [{u'orderId': u'OD113394499683187100', u'status': u'READY_TO_DISPATCH', u'packageIds': [u'PKGCTFF8YNQ8UQGPMESANHZL9'], u'orderItemId': u'11339449968318700', u'listingId': u'LSTCTFF8YNQ8UQGPMESANHZL9', u'title': u'Lenovo Thinkpad Core i5 2nd Gen - (4 GB/160 GB HDD/Windows 7 Professional) 7827 Business Laptop Black Grade B', u'serviceProfile': u'Seller_Fulfilment', u'hsn': u'84713010', u'cancellationGroupId': u'grp11339449968318700', u'paymentType': u'PREPAID', u'is_replacement': False, u'fsn': u'CTFF8YNQ8UQGPMES', u'sku': u'Very Good - L420', u'priceComponents': {u'shippingCharge': 0.0, u'customerPrice': 14999.0, u'totalPrice': 14999.0, u'flipkartDiscount': 0.0, u'sellingPrice': 14999.0}, u'orderDate': u'2018-09-16T15:00:08.000+05:30', u'quantity': 1}], u'mps': False}]
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
        params = {'shipmentId':flipkart_order.get("shipmentId")}
        # shipment_id_details = get_request('shipment_id_details',params)
        shipment_id_details = [{u'orderId': u'OD113394499683187100', u'subShipments': [{u'shipmentDimensions': {u'breadth': 30, u'length': 50, u'weight': 2, u'height': 10}, u'subShipmentId': u'SS-1', u'courierDetails': {u'pickupDetails': {u'vendorName': u'E-Kart Logistics', u'trackingId': u'FMPP0191313838'}, u'deliveryDetails': {u'vendorName': u'E-Kart Logistics', u'trackingId': u'FMPP0191313838'}}}], u'returnAddress': {u'city': None, u'contactNumber': None, u'firstName': None, u'lastName': None, u'pinCode': None, u'state': None, u'addressLine2': None, u'stateCode': None, u'addressLine1': None, u'landmark': None}, u'buyerDetails': {u'lastName': u'Ltd', u'firstName': u'SAWAN K Motors Pvt'}, u'shipmentId': u'387b9edb-f31e-4ed6-995f-a523f29c495d', u'locationId': u'LOCa4858b6869c6488c831139a59e5af401', u'billingAddress': {u'city': u'Panipat', u'contactNumber': u'9812038885', u'firstName': u'SAWAN K Motors Pvt', u'lastName': u'Ltd', u'pinCode': u'132103', u'state': u'Haryana', u'addressLine2': u'Sec 18 HUDA, Opp Toll Plaza, G.T.Road', u'stateCode': u'IN-HR', u'addressLine1': u'SAWAN Hyundai', u'landmark': u''}, u'deliveryAddress': {u'city': u'Panipat', u'contactNumber': u'9812038885', u'firstName': u'SAWAN K Motors Pvt', u'lastName': u'Ltd', u'pinCode': u'132103', u'state': u'Haryana', u'addressLine2': u'Sec 18 HUDA, Opp Toll Plaza, G.T.Road', u'stateCode': u'IN-HR', u'addressLine1': u'SAWAN Hyundai', u'landmark': u''}, u'sellerAddress': {u'city': u'HYDERABAD', u'sellerName': u'UsedYetNew', u'pinCode': u'500032', u'state': u'TELANGANA', u'addressLine2': u'Hyderabad', u'stateCode': None, u'addressLine1': u'Flat No 73, Marigold, L&T Serence County Gachibowli,', u'landmark': None}, u'orderItems': [{u'large': False, u'dangerous': True, u'fragile': True, u'id': u'11339449968318700'}]}]
        order_item_details = {
            'fsn':flipkart_order.get("orderItems")[0].get("fsn"),
            'shipment_id_details':shipment_id_details
        }
        parsed_order = parse_order("flipkart",order_item_details)
        if parsed_order:
            flipkart_item_id = parsed_order.get("item_details").get("item_id")
            is_item_in_sync = check_flipkart_sync_flag_for_item(flipkart_item_id)
            if(is_item_in_sync):
                vwrite("Item synced")
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
