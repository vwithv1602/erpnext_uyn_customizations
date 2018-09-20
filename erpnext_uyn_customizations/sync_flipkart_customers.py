from __future__ import unicode_literals
import frappe
from frappe import _
import requests.exceptions
# from .amazon_requests import post_request, get_request
from .flipkart_utils import make_flipkart_log
from .vlog import vwrite

def create_customer(parsed_order, flipkart_customer_list):
	cust_id = parsed_order.get("customer_details").get("buyer_id")
	cust_name = parsed_order.get("customer_details").get("buyer_name")
	try:
		customer = frappe.get_doc({
			"doctype": "Customer",
			"name": cust_id,
			"customer_name" : cust_name,
			"flipkart_customer_id": cust_id,
			# "sync_with_flipkart": 1,
			# "customer_group": flipkart_settings.customer_group,
			# "territory": frappe.utils.nestedset.get_root_of("Territory"),
			"customer_type": _("Individual")
		})
		customer.flags.ignore_mandatory = True
		customer.insert()
		if customer:
			create_customer_address(parsed_order, cust_id)
			create_customer_contact(parsed_order, cust_id)
		flipkart_customer_list.append(parsed_order.get("customer_details").get("buyer_id"))
		frappe.db.commit()

			
	except Exception, e:
		vwrite("Exception raised in create_customer")
		vwrite(e.message)
		vwrite(parsed_order)
		if e.args[0] and e.args[0].startswith("402"):
			raise e
		else:
			make_flipkart_log(title=e.message, status="Error", method="create_customer", message=frappe.get_traceback(),
				request_data=parsed_order.get("BuyerUserID"), exception=True)

def create_customer_address(parsed_order, flipkart_customer):
	if not parsed_order.get("customer_details").get("buyer_name"):
		make_flipkart_log(title=parsed_order.get("customer_details").get("buyer_email"), status="Error", method="create_customer_address", message="No shipping address found for %s" % parsed_order.get("customer_details").get("email"),
					  request_data=parsed_order.get("customer_details").get("buyer_email"), exception=True)
	else:
		try:
			if parsed_order.get("customer_details").get("buyer_address_line1"):
				address_line1 = parsed_order.get("customer_details").get("buyer_address_line1").replace("'", "")
			else:
				address_line1 = 'NA'
			if parsed_order.get("customer_details").get("buyer_address_line2"):
				address_line2 = parsed_order.get("customer_details").get("buyer_address_line2").replace("'", "")
			else:
				address_line2 = 'NA'
			if not frappe.db.get_value("Address",
									   {"flipkart_address_id": parsed_order.get("customer_details").get("buyer_email")}, "name"):
				frappe.get_doc({
					"doctype": "Address",
					"flipkart_address_id": parsed_order.get("customer_details").get("buyer_address_id"),
					"address_title": parsed_order.get("customer_details").get("buyer_name"),
					"address_type": "Shipping",
					"address_line1": address_line1,
					"address_line2": address_line2,
					"city": parsed_order.get("customer_details").get("buyer_city"),
					"state": parsed_order.get("customer_details").get("buyer_state"),
					"pincode": parsed_order.get("customer_details").get("buyer_zipcode"),
					# "country": flipkart_order.get("ShippingAddress").get("Country"),
					"country": "India",
					"phone": parsed_order.get("customer_details").get("buyer_phone"),
					"email_id": parsed_order.get("customer_details").get("buyer_email"),
					"links": [{
						"link_doctype": "Customer",
						# "link_name": flipkart_order.get("BuyerUserID")
						"link_name": parsed_order.get("customer_details").get("buyer_name")
					}]
				}).insert()
			else:
				frappe.db.sql(
					"""update tabAddress set address_title='%s',address_type='Shipping',address_line1='%s',address_line2='%s',city='%s',state='%s',pincode='%s',country='%s',phone='%s',email_id='%s' where flipkart_address_id='%s' """
					% (parsed_order.get("customer_details").get("buyer_name"), parsed_order.get("customer_details").get("buyer_address_line1"),
					   parsed_order.get("customer_details").get("buyer_address_line2"),
					   parsed_order.get("customer_details").get("buyer_city"),
					   parsed_order.get("customer_details").get("buyer_state"), parsed_order.get("customer_details").get("buyer_zipcode"),
					   "India",
					   parsed_order.get("customer_details").get("buyer_phone"),
					   parsed_order.get("customer_details").get("buyer_email"),
					   parsed_order.get("customer_details").get("buyer_email")))
				frappe.db.commit()

		except Exception, e:
			vwrite('Exception raised in create_customer_address')
			vwrite(e)
			vwrite(e.message)
			vwrite(parsed_order)
			make_flipkart_log(title=e.message, status="Error", method="create_customer_address",
						  message=frappe.get_traceback(),
						  request_data=flipkart_customer, exception=True)


def create_customer_contact(parsed_order, flipkart_customer):
	cust_name = parsed_order.get("customer_details").get("buyer_name")
	email_id = parsed_order.get("customer_details").get("buyer_email")
	if not cust_name:
		make_flipkart_log(title=email_id, status="Error", method="create_customer_contact", message="Contact not found for %s" % email_id,
					  request_data=email_id, exception=True)
	else:
		try :
			if not frappe.db.get_value("Contact", {"first_name": flipkart_customer}, "name"):
				frappe.get_doc({
					"doctype": "Contact",
					"first_name": flipkart_customer,
					"email_id": email_id,
					"links": [{
						"link_doctype": "Customer",
						# "link_name": flipkart_order.get("BuyerUserID")
						"link_name": cust_name
					}]
				}).insert()
			# else:
			# 	frappe.get_doc({
			# 		"doctype": "Contact",
			# 		"first_name": flipkart_customer,
			# 		"email_id": email_id,
			# 		"links": [{
			# 			"link_doctype": "Customer",
			# 			# "link_name": flipkart_order.get("BuyerUserID")
			# 			"link_name": flipkart_order.get("ShippingAddress").get("Name")
			# 		}]
			# 	}).save()
		except Exception, e:
			vwrite("Exception raised in create_customer_contact")
			vwrite(e.message)
			vwrite(parsed_order)
			make_flipkart_log(title=e.message, status="Error", method="create_customer_contact", message=frappe.get_traceback(),
				request_data=email_id, exception=True)