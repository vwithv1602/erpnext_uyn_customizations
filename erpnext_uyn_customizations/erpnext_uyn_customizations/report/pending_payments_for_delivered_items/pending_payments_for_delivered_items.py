# Copyright (c) 2015, Frappe Technologies Pvt. Ltd. and Contributors
# License: GNU General Public License v3. See license.txt

from __future__ import unicode_literals
import frappe
from frappe.utils import flt
from frappe import msgprint, _
import operator
from erpnext_ebay.vlog import vwrite

class SalesSummary(object):
	def __init__(self, filters=None):
		self.filters = frappe._dict(filters or {})
	def run(self, args):
		columns = self.get_columns()
		data = self.get_data()
		return columns, data

	def get_columns(self):
		"""return columns based on filters"""
		columns = [
			_("Customer") + ":Link/Customer:160", 
			_("Amount to be received") + ":Currency:120",
		]
		return columns

	from datetime import timedelta,datetime
	def get_data(self):
		data = []
		
		customers = []
		# dn_sql = """ select distinct customer,sum(net_total) from `tabDelivery Note` where status not in ('Cancelled','Draft') group by customer """
		dn_sql = """ select distinct customer from `tabDelivery Note` where status not in ('Cancelled','Draft') and posting_date < NOW()-INTERVAL 1 MONTH group by customer """
		for customer in frappe.db.sql(dn_sql):
			customers.append(customer)
		sinv_sql = """ select distinct customer from `tabSales Invoice` where update_stock='1' and status not in ('Cancelled','Draft') and posting_date < NOW()-INTERVAL 1 MONTH group by customer """
		for customer in frappe.db.sql(sinv_sql):
			if customer not in customers:
				customers.append(customer)
		for customer in customers:
			try:
				pending_amount = 0
				dn_amt_sql = """ select sum(total) from `tabDelivery Note` where customer='%s' and status not in ('Cancelled','Draft') group by customer """ % customer[0].replace("'", r"\'").strip()
				for dn_amt in frappe.db.sql(dn_amt_sql):
					pending_amount = float(pending_amount) + float(dn_amt[0])
				sinv_amt_sql = """ select sum(total) from `tabSales Invoice` where customer='%s' and update_stock='1' and status not in ('Cancelled','Draft') group by customer """ % customer[0].replace("'", r"\'").strip()
				for sinv_amt in frappe.db.sql(sinv_amt_sql):
					pending_amount = float(pending_amount) + float(sinv_amt[0])
				
				# jv_excluding_reverse_payments_sql = """ select title,sum(total_credit) from `tabJournal Entry` where title='%s' and docstatus='1' and voucher_type='Bank Entry' group by title """ % customer[0].replace("'", r"\'").strip()
				jv_excluding_reverse_payments_sql = """ select je.title,sum(jea.debit),sum(jea.credit) from `tabJournal Entry` je inner join `tabJournal Entry Account` jea on jea.parent=je.name where je.docstatus='1' and jea.against_account='%s' """ %(customer[0].replace("'", r"\'").strip())
				for title,credit,debit in frappe.db.sql(jv_excluding_reverse_payments_sql):
					if not credit:
						credit=0
					if not debit:
						debit=0
					pending_amount = float(pending_amount) - float(credit) + float(debit)
				pe_excluding_reverse_payments_sql = """ select sum(pe.paid_amount) from `tabPayment Entry` pe where pe.party='%s' and pe.docstatus='1'  """ %(customer[0].replace("'",r"\'").strip())
				for credit in frappe.db.sql(pe_excluding_reverse_payments_sql):
					if not credit[0]:
						credit=0
					pending_amount = float(pending_amount) - float(credit)
				if pending_amount != 0:
					data.append([customer[0]] + [pending_amount])
			except Exception,e:
				vwrite("Exception raised in Pending Payments for Delivered Items Report")
				vwrite(e.message)
			
		
		# jv_sql = """ select title,sum(total_credit) from `tabJournal Entry` where docstatus='1' group by title """
		# for customer,credit in frappe.db.sql(jv_sql):
		# 	amount_to_be_received = float(amount_to_be_received) - float(credit)
			
		# 	if amount_to_be_received != 0:
		# 		data.append([customer]+[amount_to_be_received])
		return data

def execute(filters=None):
	args = {

	}
	return SalesSummary(filters).run(args)
	# data = []

	# rows = get_dataget_data()
	# for row in rows:
	# 	data.append(row)
	# return columns,data

