# Copyright (c) 2015, Frappe Technologies Pvt. Ltd. and Contributors
# License: GNU General Public License v3. See license.txt

from __future__ import unicode_literals
import frappe
from frappe.utils import flt
from frappe import msgprint, _
import operator
from erpnext_ebay.vlog import vwrite

class ReadyToShipEnhancedDaily(object):
    def __init__(self, filters=None):
        self.filters = frappe._dict(filters or {})
        self.selected_date_obj = self.datetime.strptime(self.datetime.today().strftime('%Y-%m-%d'), '%Y-%m-%d')
        self.selected_month = self.datetime.today().strftime('%B')
        self.today = str(self.datetime.today())[:10]
        self.yesterday = self.datetime.strptime((self.datetime.today() + self.timedelta(-1)).strftime('%Y-%m-%d'), '%Y-%m-%d')
        
    def run(self, args):
        data = self.get_data()
        max_len = 0
        len2 = 0
        for d in data:
            if d[1]:
                if len(d[1]) > max_len:
                    max_len = len(d[1])
        for d in data:
            if d[0]:
                if len(d[0]) > len2:
                    len2 = len(d[0])
        columns = self.get_columns(max_len*6.66,len2*6.66)
        return columns, data

    def get_columns(self,max_len,len2):
        """return columns bab on filters"""
        columns = [
            _("Variant Of") + ":Data:%s" % len2,
            _("Item Code") + ":Data:%s" % max_len,
            _("Item Group") + ":Data:120",
            # _("Qty") + ":Data:80",
            _("RTS") + ":Data:80" 
        ]
        return columns

    from datetime import timedelta,datetime
    def prepare_conditions(self):
        conditions = [""]
        group_by = ""
        conditions.append(""" se.posting_date = '%s'""" % self.yesterday)
        conditions.append(""" i.item_group in ('Laptops','Desktops') """)
        group_by = " group by i.variant_of "
        conditions_string = " and ".join(conditions)
        return "%s %s" %(conditions_string,group_by)
    def get_data(self):
        data = []
        conditions = self.prepare_conditions()
        rts_sql = """ 
        select sum(sed.qty) as count,i.variant_of,sed.item_code,i.item_group,sed.qty,se.posting_date from `tabStock Entry` se inner join `tabStock Entry Detail` sed on sed.parent=se.name inner join `tabItem` i on i.item_code=sed.item_code where sed.t_warehouse = 'G3 Ready To Ship - UYN' and i.variant_of<>'' %s;
        """ % (conditions)
        for rts in frappe.db.sql(rts_sql,as_dict=1):
            data.append([rts.get("variant_of"),rts.get("item_code"),rts.get("item_group"),rts.get("count")])
        return data
    
def execute(filters=None):
    args = {

    }
    return ReadyToShipEnhancedDaily(filters).run(args)
