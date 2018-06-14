# Copyright (c) 2015, Frappe Technologies Pvt. Ltd. and Contributors
# License: GNU General Public License v3. See license.txt

from __future__ import unicode_literals
import frappe
from frappe.utils import flt
from frappe import msgprint, _
import operator
from erpnext_ebay.vlog import vwrite

class StockMovement(object):
    def __init__(self, filters=None):
        self.filters = frappe._dict(filters or {})
        self.selected_date_obj = self.datetime.strptime(self.datetime.today().strftime('%Y-%m-%d'), '%Y-%m-%d')
	self.selected_month = self.datetime.today().strftime('%B')
        # self.selected_date_obj = self.datetime.strptime("2018-04-28", '%Y-%m-%d')
        self.today = str(self.datetime.today())[:10]
        self.weekstartdate = self.week_range(self.selected_date_obj)[0]
        self.weekenddate = self.week_range(self.selected_date_obj)[1]
        
    def run(self, args):
        columns = self.get_columns()
        data = self.get_data()
        return columns, data

    def get_columns(self):
        """return columns bab on filters"""
        columns = [
            _("") + "::200", 
            _("for %s" % self.today) + ":Int:120",
            _("for week starting from %s" % self.weekstartdate) + ":Int:220",
            _(self.selected_month) + ":Int:120",
            _("> 3 days old") + ":Int:120",
            _("> 7 days old") + ":Int:120",
            _("> 10 days old") + ":Int:120",

        ]
        return columns

    from datetime import timedelta,datetime
    
    def week_range(self,date):
		"""Find the first/last day of the week for the given day.
		Assuming weeks start on Sunday and end on Saturday.
		Returns a tuple of ``(start_date, end_date)``.
		"""
		# isocalendar calculates the year, week of the year, and day of the week.
		# dow is Mon = 1, Sat = 6, Sun = 7
		year, week, dow = date.isocalendar()
		# Find the first day of the week.
		if dow == 7:
			# Since we want to start with Sunday, let's test for that condition.
			start_date = date
		else:
			# Otherwise, subtract `dow` number days to get the first day
			start_date = date - self.timedelta(dow)
		# Now, add 6 for the last day of the week (i.e., count up to Saturday)
		end_date = start_date + self.timedelta(7)
		return (start_date.strftime('%Y-%m-%d'), end_date.strftime('%Y-%m-%d'))
    
    

    def get_data(self):
        data = []
        
        stores_result = self.get_result_for_warehouse("Stores - Uyn")
        techteam_result = self.get_result_for_warehouse("Tech Team - Uyn")
        paint_result = self.get_result_for_warehouse("Painting - Uyn")
        materialissue_result = self.get_pending_materials()
        final_result = self.get_result_for_warehouse("Final QC & Packing - Uyn")

        for day,week,month,old3,old7,old10 in stores_result:
            data.append(["from Store"]+[day,week,month,old3,old7,old10])
        for day,week,month,old3,old7,old10 in techteam_result:
            data.append(["from Tech Team"]+[day,week,month,old3,old7,old10])
        for day,week,month,old3,old7,old10 in materialissue_result:
            data.append(["of Which Material Issue (Raib > 3 Days)"]+["","","",old3,old7,old10])
        for day,week,month,old3,old7,old10 in paint_result:
            data.append(["from Paint"]+[day,week,month,old3,old7,old10])
        for day,week,month,old3,old7,old10 in final_result:
            data.append(["from Final QC"]+[day,week,month,old3,old7,old10])
        
        return data
    def get_pending_materials(self):

        pending_materials_sql = """ 
        select
        (select sum(b.actual_qty) from `tabStock Ledger Entry` b inner join `tabMaterial Request Item` mri on mri.serial_no=b.serial_no inner join `tabItem` i on i.item_code=b.item_code inner join `tabMaterial Request` mr on mr.name=mri.parent where mr.status='Pending' and i.item_group='Laptops' and mri.creation like '{0}%') as day,
        (select sum(b.actual_qty) from `tabStock Ledger Entry` b inner join `tabMaterial Request Item` mri on mri.serial_no=b.serial_no inner join `tabItem` i on i.item_code=b.item_code inner join `tabMaterial Request` mr on mr.name=mri.parent where mr.status='Pending' and i.item_group='Laptops' and mri.creation >= '{1}' and mri.creation <= '{2}') as week,
        (select sum(b.actual_qty) from `tabStock Ledger Entry` b inner join `tabMaterial Request Item` mri on mri.serial_no=b.serial_no inner join `tabItem` i on i.item_code=b.item_code inner join `tabMaterial Request` mr on mr.name=mri.parent where mr.status='Pending' and i.item_group='Laptops' and MONTH(mri.creation) = MONTH('{0}') and YEAR(mri.creation) = YEAR('{0}')) as month,
        (select count(sle.serial_no) from `tabSerial No` sle where sle.item_group='Laptops' and sle.purchase_date < NOW() - INTERVAL 3 DAY and sle.warehouse='Tech Team - Uyn' and sle.serial_no  in (select serial_no from `tabMaterial Request Item`  mri inner join `tabMaterial Request` mr on mr.name=mri.parent where mr.status not in ('Submitted'))) as old3,
        (select count(sle.serial_no) from `tabSerial No` sle where sle.item_group='Laptops' and sle.purchase_date < NOW() - INTERVAL 7 DAY and sle.warehouse='Tech Team - Uyn' and sle.serial_no  in (select serial_no from `tabMaterial Request Item`  mri inner join `tabMaterial Request` mr on mr.name=mri.parent where mr.status not in ('Submitted'))) as old7,
        (select count(sle.serial_no) from `tabSerial No` sle where sle.item_group='Laptops' and sle.purchase_date < NOW() - INTERVAL 10 DAY and sle.warehouse='Tech Team - Uyn' and sle.serial_no  in (select serial_no from `tabMaterial Request Item`  mri inner join `tabMaterial Request` mr on mr.name=mri.parent where mr.status not in ('Submitted'))) as old10
        """.format(self.today,self.weekstartdate,self.weekenddate)
        return frappe.db.sql(pending_materials_sql)
    def get_result_for_warehouse(self,warehouse):

        store_sql = """ 
        select
        (select sum(sle.actual_qty*-1) from `tabStock Ledger Entry` sle inner join `tabItem` i on i.item_code=sle.item_code where sle.actual_qty<0 and sle.warehouse='{0}' and i.item_group='Laptops' and sle.posting_date='{1}') as day, 
        (select sum(sle.actual_qty*-1) from `tabStock Ledger Entry` sle inner join `tabItem` i on i.item_code=sle.item_code where sle.actual_qty<0 and sle.warehouse='{0}' and i.item_group='Laptops' and sle.posting_date > '{2}' and sle.posting_date < '{3}') as week, 
        (select sum(sle.actual_qty*-1) from `tabStock Ledger Entry` sle inner join `tabItem` i on i.item_code=sle.item_code where sle.actual_qty<0 and sle.warehouse='{0}' and i.item_group='Laptops' and MONTH(sle.posting_date) = MONTH('{1}') and YEAR(sle.posting_date) = YEAR('{1}')) as month,
        (select count(*) from `tabSerial No` sle where sle.item_group='Laptops' and sle.purchase_date < NOW() - INTERVAL 3 DAY and sle.warehouse='{0}') as old3,
        (select count(*) from `tabSerial No` sle where sle.item_group='Laptops' and sle.purchase_date < NOW() - INTERVAL 7 DAY and sle.warehouse='{0}') as old7,
        (select count(*) from `tabSerial No` sle where sle.item_group='Laptops' and sle.purchase_date < NOW() - INTERVAL 10 DAY and sle.warehouse='{0}') as old10
        """.format(warehouse,self.today,self.weekstartdate,self.weekenddate)
        return frappe.db.sql(store_sql)

def execute(filters=None):
    args = {

    }
    return StockMovement(filters).run(args)
    # data = []

    # rows = get_dataget_data()
    # for row in rows:
    #   data.append(row)
    # return columns,data



