from __future__ import unicode_literals
import frappe
from erpnext_ebay.vlog import vwrite
import requests
import json
@frappe.whitelist()
def test():
    print ("In whatsapp")
    url = 'https://eu8.chat-api.com/instance6736/message?token=jqlq35i2diewk7xi'
    payload = {
    "phone": "918801133454",
    "body": "WhatsApp API on chat-api.com works good"
    }
    headers = {'content-type': 'application/json'}
    r = requests.post(url, data=json.dumps(payload), headers=headers)
    print (r)
    print type(r)
    print r.json()

@frappe.whitelist()
def fetchMessages():
    url = 'https://eu8.chat-api.com/instance6736/sendFile?token=jqlq35i2diewk7xi'
    # url = 'https://eu8.chat-api.com/messages?token=jqlq35i2diewk7xi'
    headers = {'content-type': 'application/json'}
    payload = {
        "phone": "918801133454",
        "body": "https://cdn.tinybuddha.com/wp-content/uploads/2015/09/Success.png",
        "filename": "cover.jpg"
    }
    r = requests.get(url, data=json.dumps(payload), headers=headers)
    print (r)
    print type(r)
    print r.json()

@frappe.whitelist()
def groupMessage():
    url = 'https://eu8.chat-api.com/instance6736/group?token=jqlq35i2diewk7xi'
    headers = {'content-type': 'application/json'}
    payload = {
        "phones": ["918801133454","918106166857"],
        "messageText": "'group' api ki post request",
        "groupName": "Test Group With Space",
        "body": "https://cdn.tinybuddha.com/wp-content/uploads/2015/09/Success.png",
    }
    r = requests.get(url, data=json.dumps(payload), headers=headers)
    print (r)
    print type(r)
    print r.json()
