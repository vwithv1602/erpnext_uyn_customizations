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
            _("Supplier") + ":Link/Supplier:160", 
            _("Amount to be received") + ":Currency:120",
        ]
        return columns

    from datetime import timedelta,datetime
    def get_data(self):
        data = []
        jv_sql = """ select je.title,sum(je.total_credit) from `tabJournal Entry` je inner join `tabSupplier` s on s.name=je.title where je.docstatus='1' group by je.title """
        for title,credit in frappe.db.sql(jv_sql):
            amount_to_be_received = float(credit)
            # considering purchase receipt
            pr_sql = """ select supplier,sum(net_total) from `tabPurchase Receipt` where supplier='%s' and status not in ('Cancelled','Draft') group by supplier """ % title.replace("'", r"\'").strip()
            for supplier,total in frappe.db.sql(pr_sql):
                amount_to_be_received = float(amount_to_be_received) - float(total)
            # considering purchase invoice with update stock
            pinv_sql = """ select title,sum(net_total) from `tabPurchase Invoice` where title='%s' and update_stock='1' and status not in ('Cancelled','Draft','Return') group by title """ % title.replace("'", r"\'").strip()
            for supplier,total in frappe.db.sql(pinv_sql):
                amount_to_be_received = float(amount_to_be_received) - float(total)
            # considering purchase invoice with update stock
            pinv_exl_sql = """ select pi.title,sum(pi.net_total) from `tabPurchase Invoice` pi inner join `tabPurchase Invoice Item` pii on pii.parent=pi.name where pii.item_code='' and pi.title='%s' and pi.status not in ('Cancelled','Draft','Return') group by pi.title """ % title.replace("'", r"\'").strip()
            for supplier,total in frappe.db.sql(pinv_exl_sql):
                amount_to_be_received = float(amount_to_be_received) - float(total)
            if amount_to_be_received != 0:
                data.append([title]+[amount_to_be_received])
        return data

def execute(filters=None):
    args = {

    }
    return SalesSummary(filters).run(args)
    # data = []

    # rows = get_dataget_data()
    # for row in rows:
    #   data.append(row)
    # return columns,data
