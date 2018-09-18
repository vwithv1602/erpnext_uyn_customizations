from __future__ import unicode_literals
import frappe
from frappe import _
from .sync_flipkart_orders import sync_flipkart_orders,sync_flipkart_qty
from .flipkart_utils import disable_flipkart_sync_on_exception, make_flipkart_log
from frappe.utils.background_jobs import enqueue
from datetime import datetime,timedelta

from vlog import vwrite

@frappe.whitelist()
def sync_flipkart():
    enqueue("erpnext_uyn_customizations.flipkart_api.sync_flipkart_resources", queue='long')
    frappe.msgprint(_("Queued for syncing. It may take a few minutes to an hour if this is your first sync."))

def sync_flipkart_resources():
    "Enqueue longjob for syncing flipkart"
    flipkart_settings = frappe.get_doc("Flipkart Settings")
    make_flipkart_log(title="Flipkart Sync Job Queued", status="Queued", method=frappe.local.form_dict.cmd,
                     message="Flipkart Sync Job Queued")
    if(flipkart_settings.enable_flipkart):
        try:
            now_time = frappe.utils.now()
            validate_flipkart_settings(flipkart_settings)
            frappe.local.form_dict.count_dict = {}
            vwrite("Sync Orders")
            sync_flipkart_orders()
            frappe.db.set_value("Flipkart Settings", None, "last_sync_datetime", now_time)
            make_flipkart_log(title="Sync Completed", status="Success", method=frappe.local.form_dict.cmd,
                             message="Flipkart sync successfully completed")
        except Exception, e:
            if e.args[0] and hasattr(e.args[0], "startswith") and e.args[0].startswith("402"):
                make_flipkart_log(title="Flipkart has suspended your account", status="Error",
                                 method="sync_flipkart_resources", message=_("""Flipkart has suspended your account till
            		you complete the payment. We have disabled ERPNext Flipkart Sync. Please enable it once
            		your complete the payment at Flipkart."""), exception=True)

                disable_flipkart_sync_on_exception()

            else:
                make_flipkart_log(title="sync has terminated", status="Error", method="sync_flipkart_resources",
                                 message=frappe.get_traceback(), exception=True)
    elif frappe.local.form_dict.cmd == "erpnext_flipkart.api.sync_flipkart":
        make_flipkart_log(
            title="Flipkart connector is disabled",
            status="Error",
            method="sync_flipkart_resources",
            message=_(
                """Flipkart connector is not enabled. Click on 'Connect to Flipkart' to connect ERPNext and your Flipkart store."""),
            exception=True)
    

def validate_flipkart_settings(flipkart_settings):
	"""
		This will validate mandatory fields and access token or app credentials
		by calling validate() of flipkart settings.
	"""
	try:
		flipkart_settings.save()
	except Exception, e:
		disable_flipkart_sync_on_exception()
