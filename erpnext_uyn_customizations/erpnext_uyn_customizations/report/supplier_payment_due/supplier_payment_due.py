# Copyright (c) 2015, Frappe Technologies Pvt. Ltd. and Contributors
# License: GNU General Public License v3. See license.txt

from __future__ import unicode_literals
import frappe
from frappe.utils import flt
from frappe import msgprint, _
import operator
from erpnext_ebay.vlog import vwrite

class SupplierPaymentDue(object):
    def __init__(self, filters=None):
        test = "rest"
        # self.filters = frappe._dict(filters or {})
        # self.selected_date_obj = self.datetime.strptime(self.datetime.today().strftime('%Y-%m-%d'), '%Y-%m-%d')
        # self.selected_month = self.datetime.today().strftime('%B')
        # # self.selected_date_obj = self.datetime.strptime("2018-04-28", '%Y-%m-%d')
        # self.today = str(self.datetime.today())[:10]
        # self.weekstartdate = self.week_range(self.selected_date_obj)[0]
        # self.weekenddate = self.week_range(self.selected_date_obj)[1]

    def run(self, args):
        data = self.get_data()
        columns = self.get_columns()
        return columns, data
    from datetime import timedelta,datetime

    def get_columns(self):
        """return columns bab on filters"""
        columns = [
            _("Supplier") + ":Data:200",
            _("Total Amount Of Goods received Till date") + ":Currency:200",
            _("Total Amount Paid Till Date") + ":Currency:200",
            _("To Be Received") + ":Currency:200"
        ]
        return columns

    from datetime import timedelta,datetime

    def get_data(self):
        data = []
        sql = """
            select a.title,a.total_debit ,sum(pr.net_total) as net_total,(sum(pr.net_total) - total_debit) as to_be_received from 
            (
            select je.name,je.title,sum(je.total_debit) as total_debit from `tabJournal Entry` je inner join `tabJournal Entry Account` jea on jea.parent=je.name where jea.party_type='Supplier' and je.docstatus=1 group by je.title
            ) as a inner join `tabPurchase Receipt` pr on pr.title=a.title 
            where pr.docstatus=1 group by pr.title 
        """
        suppliers = []
        for row in frappe.db.sql(sql,as_dict=1):
            suppliers.append(row.title)
            data.append([row.title,row.net_total,row.total_debit,row.to_be_received])
        sql = """
            select a.title,a.total_debit ,sum(pi.net_total) as net_total,(sum(pi.total) - total_debit) as to_be_received from 
            (
            select je.name,je.title,sum(je.total_debit) as total_debit from `tabJournal Entry` je inner join `tabJournal Entry Account` jea on jea.parent=je.name where jea.party_type='Supplier' and je.docstatus=1 group by je.title
            ) as a inner join `tabPurchase Invoice` pi on pi.title=a.title 
            where pi.docstatus=1 and pi.update_stock=1 group by pi.title 
        """
        for row in frappe.db.sql(sql,as_dict=1):
            i = 0
            for d in data:
                if d[0]==row.title:
                    data[i][1] = data[i][1]+row.net_total
		    data[i][3] = data[i][3]+row.net_total
                i += 1
            if row.title not in suppliers:
                data.append([row.title,row.net_total,row.total_debit,row.to_be_received])
            # suppliers.append(row.title)
            # data.append([row.title,row.total_debit,row.net_total,row.to_be_received])
        return data
@frappe.whitelist()
def execute(filters=None):
    args = {

    }
    return SupplierPaymentDue(filters).run(args)
    # data = []

    # rows = get_dataget_data()
    # for row in rows:
    #   data.append(row)
    # return columns,data

