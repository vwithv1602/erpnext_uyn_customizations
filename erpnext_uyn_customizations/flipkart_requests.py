import frappe
from frappe import _
from datetime import datetime,timedelta
from .flipkart_exceptions import FlipkartError

import requests,json
from requests.auth import HTTPBasicAuth

from .vlog import vwrite

urls = {
    'list_orders': 'https://api.flipkart.net/sellers/v3/shipments/filter/',
    'shipment_id_details': 'https://api.flipkart.net/sellers/v3/shipments/',
    'list_order_information': 'https://api.flipkart.net/sellers/listings/v3/',
    'update_inventory': 'https://api.flipkart.net/sellers/listings/v3/update/inventory'
}
def get_request(path,params={}):
    settings = get_flipkart_settings()
    lastSyncString = settings.last_sync_datetime
    lastSyncString = lastSyncString[:19]
    lastSyncObj = datetime.strptime(lastSyncString, '%Y-%m-%d %H:%M:%S')
    lastSync = (lastSyncObj + timedelta(-1)).isoformat()
    orders_response = None
    response = None

    access_token = get_access_token(settings)
    authorization = 'Bearer %s' % access_token
    if path == 'list_orders':
        payload = '{"filter" :{"type":"preDispatch","states":["APPROVED","PACKING_IN_PROGRESS","PACKED","FORM_FAILED","READY_TO_DISPATCH"]}}'
        headers = {"Content-Type": "application/json", "Authorization":authorization}
        r = requests.post(urls[path], data=payload, headers=headers)
        content = r.__dict__.get("_content")
        result = json.loads(content)
        response = result.get("shipments")
    elif path == 'shipment_id_details':
        payload = '{}'
        headers = {"Content-Type": "application/json", "Authorization":authorization}
        url = "%s%s" % (urls[path],params.get("shipmentId"))
        r = requests.get(url, headers=headers)
        content = r.__dict__.get("_content")
        result = json.loads(content)
        vwrite(result)
        response = result.get("shipments")
    elif path == 'list_order_information':
        headers = {"Content-Type": "application/json", "Authorization":authorization}
        url = "{0}{1}".format(urls[path],params.get('skuId'))
        r = requests.get(url,headers=headers)
        content = r.__dict__.get('_content')
        result = json.loads(content)
        response = result.get('available').get(params.get('skuId'))
    elif path == 'update_inventory':
        payload = {}
        skuId = params.get('skuId')
        payload[skuId] = {}
        payload[skuId]['product_id'] = params.get('productId')
        payload[skuId]['locations'] = []
        temp_location_value = {'id': params.get('locationId'),'inventory': params.get('inventory_value')}
        payload[skuId]['locations'].append(temp_location_value)
        payload = json.dumps(payload)
        vwrite(payload)
        payload = payload.replace('"{0}"'.format(params.get('inventory_value')), str(params.get('inventory_value')))
        headers = {"Content-Type": "application/json", "Authorization":authorization}
        r = requests.post(urls[path], data=payload, headers=headers)
        content = r.__dict__.get("_content")
        result = json.loads(content)
        response = result
    return response
    

def get_flipkart_settings():
    d = frappe.get_doc("Flipkart Settings")
    if d.username and d.password:
        if d.password:
            d.password = d.get_password()
        return d.as_dict()
    else:
        frappe.throw(_("Flipkart store Access Key Id is not configured on Flipkart Settings"), FlipkartError)

def get_access_token(settings):
    url = 'https://api.flipkart.net/oauth-service/oauth/token?grant_type=client_credentials&scope=Seller_Api'
    r = requests.get(url, auth=HTTPBasicAuth(settings.username, settings.password))
    raw_content = r.__dict__.get("_content")
    content = json.loads(raw_content)
    access_token = content.get("access_token")
    return access_token
