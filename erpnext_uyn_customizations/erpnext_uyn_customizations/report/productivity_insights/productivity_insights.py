# Copyright (c) 2015, Frappe Technologies Pvt. Ltd. and Contributors
# License: GNU General Public License v3. See license.txt

from __future__ import unicode_literals
import frappe
from frappe.utils import flt
from frappe import msgprint, _
import operator
from erpnext_ebay.vlog import vwrite
from erpnext_uyn_customizations.erpnext_uyn_customizations.doctype.rejects.rejects import save_reject
from collections import defaultdict
	
class ProductivityInsights(object):
	from datetime import timedelta,datetime
	def __init__(self, filters=None):
		self.filters = frappe._dict(filters or {})
		self.selected_date_obj = self.datetime.strptime(self.datetime.today().strftime('%Y-%m-%d'), '%Y-%m-%d')
		# >> change date here for older dates
		# self.selected_date_obj = self.datetime.strptime('2018-11-18', '%Y-%m-%d')
		# << change date here for older dates
		self.selected_month = self.selected_date_obj.strftime('%B')
		self.today = str(self.selected_date_obj)[:10]
		from datetime import timedelta,datetime
		self.yesterday = self.selected_date_obj - self.timedelta(1)
		self.yesterday_str = str(self.yesterday)[:10]
		self.weekstartdate = self.week_range(self.selected_date_obj)[0]
		self.weekenddate = self.week_range(self.selected_date_obj)[1]
		print self.today
		print self.yesterday_str
		print self.weekstartdate
		print self.weekenddate
        
        
	def run(self, args):
		data = self.get_data()
		columns = self.get_columns()
		return columns, data
	def get_columns(self):
		"""return columns bab on filters"""
		columns = [
			_("Warehouse") + ":Data:180",
			_("Gross Daily") + ":Data:95",
			_("Net Daily") + ":Data:95",
			_("Rejects Daily") + ":Data:95",
			_("Gross Weekly") + ":Data:95",
			_("Net Weekly") + ":Data:95",
			_("Rejects Weekly") + ":Data:95",
			_("Gross Montly") + ":Data:95",
			_("Net Montly") + ":Data:95",
			_("Rejects Monthly") + ":Data:95",
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
		date = date - self.timedelta(1)
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
		warehouses_sql = """ select warehouse_name,warehouse_sequence_number,warehouse_inspection_type from `tabWarehouse` where warehouse_sequence_number <> '' order by warehouse_sequence_number """
		warehouses_res = frappe.db.sql(warehouses_sql,as_dict=1)
		# warehouses_res = [{u'warehouse_inspection_type': u'Chip Level In Process', u'warehouse_name': u'Chip Tech', u'warehouse_sequence_number': u'2'}]
		daily_gross_productivity = []
		daily_net_productivity = []
		weekly_gross_productivity = []
		weekly_net_productivity = []
		monthly_gross_productivity = []
		monthly_net_productivity = []
		unique_barcodes = []
		unique_qis = []
		inspection_type_gross = defaultdict(int)
		inspection_type_net = defaultdict(int)
		def get_rejects(emp,period,inspection_type):
			rejects = 0
			if period=='daily':
				reject_sql = """ select count(*) as count from `tabRejects` where rejected_date='{2}' and inspected_by='{0}' and inspection_type='{1}' and ste not in (select  name from `tabStock Entry` where docstatus<>'1')""".format(emp,inspection_type,self.yesterday_str)
				print reject_sql
				rejects = frappe.db.sql(reject_sql,as_dict=1)[0].get("count")
			elif period=='weekly':
				reject_sql = """ select count(*) as count from `tabRejects` where rejected_date>'{1}' and rejected_date<='{2}' and inspected_by='{0}'  and inspection_type='{3}' and ste not in (select  name from `tabStock Entry` where docstatus<>'1') and MONTH(rejected_date)=MONTH('{4}') and YEAR(rejected_date)=YEAR('{4}')""".format(emp,self.weekstartdate,self.weekenddate,inspection_type,self.today)
				rejects = frappe.db.sql(reject_sql,as_dict=1)[0].get("count")
			elif period=='monthly':
				reject_sql = """ select count(*) as count from `tabRejects` where MONTH(rejected_date)=MONTH('{2}') and YEAR(rejected_date)=YEAR('{2}') and inspected_by='{0}' and inspection_type='{1}' and ste not in (select  name from `tabStock Entry` where docstatus<>'1')""".format(emp,inspection_type,self.today)
				rejects = frappe.db.sql(reject_sql,as_dict=1)[0].get("count")
			return rejects
		for warehouse in warehouses_res:
			######### DAILY
			if warehouse.get("warehouse_inspection_type"):
				# DAILY GROSS PRODUCTIVITY CALCULATION
				qi_sql = """ select name,inspected_by,inspection_type,barcode,report_date from `tabQuality Inspection` where report_date='{1}' and inspection_type='{0}' and docstatus=1 """.format(warehouse.get("warehouse_inspection_type"),self.yesterday_str)
				qi_res = frappe.db.sql(qi_sql,as_dict=1)
				emps_gross = defaultdict(int)
				for qi in qi_res:
					# print "%s %s" %(qi.get("inspected_by"),qi.get("inspection_type"))
					if qi.get("barcode") not in unique_barcodes:
						unique_barcodes.append(qi.get("barcode"))
					if qi.get("name") not in unique_qis:
						unique_qis.append(qi.get("name"))
						# print "%s %s" %(warehouse.get("warehouse_inspection_type"),qi.get("inspection_type"))
						emps_gross[qi.get("inspected_by")] += 1
						inspection_type_gross[qi.get("inspection_type")] = emps_gross
				# DAILY NET PRODUCTIVITY CALCULATION
				# >> Getting rejects
				rejects = []
				for qi in qi_res:
					rejects_sql = """ select serial_no from `tabRejects` where inspection_type='{0}' and rejected_date>'{1}' """.format(warehouse.get("warehouse_inspection_type"),qi.get("report_date"))
					for reject in frappe.db.sql(rejects_sql,as_dict=1):
						rejects.append(str(reject.get("serial_no")).lower())
				# << Getting rejects
				net_qi_res = []
				for qi in qi_res:
					if (str(qi.get("barcode")).lower() not in rejects) or (str(qi.get("barcode")).lower() not in unique_barcodes):
						net_qi_res.append(qi)
				emps_net = defaultdict(int)
				for qi in net_qi_res:
					emps_net[qi.get("inspected_by")] += 1
					inspection_type_net[qi.get("inspection_type")] = emps_net
			if len(emps_gross):
				daily_gross_productivity.append({"warehouse_name":warehouse.get("warehouse_name"),"prod_data":emps_gross})
			if len(emps_net):
				daily_net_productivity.append({"warehouse_name":warehouse.get("warehouse_name"),"prod_data":emps_net})
		unique_barcodes = []
		unique_qis = []
		inspection_type_gross = defaultdict(int)
		inspection_type_net = defaultdict(int)
		for warehouse in warehouses_res:
			######### WEEKLY
			if warehouse.get("warehouse_inspection_type"):
				# WEEKLY GROSS PRODUCTIVITY CALCULATION
				qi_sql = """ select name,inspected_by,inspection_type,barcode,report_date from `tabQuality Inspection` where report_date>'{1}' and report_date<='{2}' and inspection_type='{0}' and docstatus=1 and MONTH(report_date)=MONTH('{3}') and YEAR(report_date)=YEAR('{3}') """.format(warehouse.get("warehouse_inspection_type"),self.weekstartdate,self.weekenddate,self.today)
				qi_res = frappe.db.sql(qi_sql,as_dict=1)
				emps_gross = defaultdict(int)
				for qi in qi_res:
					# print "%s %s" %(qi.get("inspected_by"),qi.get("inspection_type"))
					if qi.get("barcode") not in unique_barcodes:
						unique_barcodes.append(qi.get("barcode"))
					if qi.get("name") not in unique_qis:
						unique_qis.append(qi.get("name"))
						# print "%s %s" %(warehouse.get("warehouse_inspection_type"),qi.get("inspection_type"))
						emps_gross[qi.get("inspected_by")] += 1
						inspection_type_gross[qi.get("inspection_type")] = emps_gross
				# WEEKLY NET PRODUCTIVITY CALCULATION
				# >> Getting rejects
				rejects = []
				for qi in qi_res:
					rejects_sql = """ select serial_no from `tabRejects` where inspection_type='{0}' and rejected_date>'{1}' """.format(warehouse.get("warehouse_inspection_type"),qi.get("report_date"))
					for reject in frappe.db.sql(rejects_sql,as_dict=1):
						rejects.append(str(reject.get("serial_no")).lower())
				# << Getting rejects
				net_qi_res = []
				for qi in qi_res:
					if (str(qi.get("barcode")).lower() not in rejects) or (str(qi.get("barcode")).lower() not in unique_barcodes):
						net_qi_res.append(qi)
				emps_net = defaultdict(int)
				for qi in net_qi_res:
					emps_net[qi.get("inspected_by")] += 1
					inspection_type_net[qi.get("inspection_type")] = emps_net
			if len(emps_gross):
				weekly_gross_productivity.append({"warehouse_name":warehouse.get("warehouse_name"),"prod_data":emps_gross})
			if len(emps_net):
				weekly_net_productivity.append({"warehouse_name":warehouse.get("warehouse_name"),"prod_data":emps_net})
		unique_barcodes = []
		unique_qis = []
		inspection_type_gross = defaultdict(int)
		inspection_type_net = defaultdict(int)
		for warehouse in warehouses_res:
			######### MONTHLY
			if warehouse.get("warehouse_inspection_type"):
				# MONTHLY GROSS PRODUCTIVITY CALCULATION
				qi_sql = """ select name,inspected_by,inspection_type,barcode,report_date from `tabQuality Inspection` where MONTH(report_date)=MONTH('{1}') and YEAR(report_date)=YEAR('{1}') and inspection_type='{0}' and docstatus=1 """.format(warehouse.get("warehouse_inspection_type"),self.today)
				qi_res = frappe.db.sql(qi_sql,as_dict=1)
				emps_gross = defaultdict(int)
				for qi in qi_res:
					# print "%s %s" %(qi.get("inspected_by"),qi.get("inspection_type"))
					if qi.get("barcode") not in unique_barcodes:
						unique_barcodes.append(qi.get("barcode"))
					if qi.get("name") not in unique_qis:
						unique_qis.append(qi.get("name"))
						# print "%s %s" %(warehouse.get("warehouse_inspection_type"),qi.get("inspection_type"))
						emps_gross[qi.get("inspected_by")] += 1
						inspection_type_gross[qi.get("inspection_type")] = emps_gross
				# MONTHLY NET PRODUCTIVITY CALCULATION
				# >> Getting rejects
				rejects = []
				for qi in qi_res:
					rejects_sql = """ select serial_no from `tabRejects` where inspection_type='{0}' and rejected_date>'{1}' """.format(warehouse.get("warehouse_inspection_type"),qi.get("report_date"))
					for reject in frappe.db.sql(rejects_sql,as_dict=1):
						rejects.append(str(reject.get("serial_no")).lower())
				# << Getting rejects
				net_qi_res = []
				for qi in qi_res:
					if (str(qi.get("barcode")).lower() not in rejects) or (str(qi.get("barcode")).lower() not in unique_barcodes):
						net_qi_res.append(qi)
				emps_net = defaultdict(int)
				for qi in net_qi_res:
					emps_net[qi.get("inspected_by")] += 1
					inspection_type_net[qi.get("inspection_type")] = emps_net
			if len(emps_gross):
				monthly_gross_productivity.append({"warehouse_name":warehouse.get("warehouse_name"),"prod_data":emps_gross})
			if len(emps_net):
				monthly_net_productivity.append({"warehouse_name":warehouse.get("warehouse_name"),"prod_data":emps_net})
		for warehouse in warehouses_res:
			warehouse_data = {}
			name = "<b>%s</b>" % warehouse.get("warehouse_name")
			data.append([name,"",""])
			for d in daily_gross_productivity:
				if(d.get("warehouse_name")==warehouse.get("warehouse_name")):
					for k,v in d.get("prod_data").iteritems():
						warehouse_data[k] = v
						# print "%s - %s" %(k,v)
			for d in daily_net_productivity:
				if(d.get("warehouse_name")==warehouse.get("warehouse_name")):
					for k,v in d.get("prod_data").iteritems():
						if warehouse_data.get(k):
							warehouse_data[k] = "%s,%s" %(warehouse_data[k],v)
						else:
							warehouse_data[k] = "0,%s" %(v)
			for d in weekly_gross_productivity:
				if(d.get("warehouse_name")==warehouse.get("warehouse_name")):
					for k,v in d.get("prod_data").iteritems():
						if warehouse_data.get(k):
							warehouse_data[k] = "%s,%s" %(warehouse_data[k],v)
						elif not warehouse_data.get(k):
							warehouse_data[k] = "0,0,%s" %(v)
						elif len(warehouse_data.get(k).split(','))<2:
							warehouse_data[k] = "%s,0,%s" %(warehouse_data[k],v)
			for d in weekly_net_productivity:
				if(d.get("warehouse_name")==warehouse.get("warehouse_name")):
					for k,v in d.get("prod_data").iteritems():
						if warehouse_data.get(k):
							warehouse_data[k] = "%s,%s" %(warehouse_data[k],v)
						else:
							warehouse_data[k] = "0,0,0,%s" %(v)
			for d in monthly_gross_productivity:
				if(d.get("warehouse_name")==warehouse.get("warehouse_name")):
					for k,v in d.get("prod_data").iteritems():
						if warehouse_data.get(k) and len(warehouse_data[k].split(','))==4:
							warehouse_data[k] = "%s,%s" %(warehouse_data[k],v)
						elif not warehouse_data.get(k):
							warehouse_data[k] = "0,0,0,0,%s" %(v)
						elif len(warehouse_data.get(k).split(','))<4:
							warehouse_data[k] = "%s,0,0,%s" %(warehouse_data[k],v)
						elif len(warehouse_data.get(k).split(','))<2:
							warehouse_data[k] = "0,0,0,0,%s" %(v)
			for d in monthly_net_productivity:
				if(d.get("warehouse_name")==warehouse.get("warehouse_name")):
					for k,v in d.get("prod_data").iteritems():
						if warehouse_data.get(k):
							warehouse_data[k] = "%s,%s" %(warehouse_data[k],v)
						else:
							warehouse_data[k] = "0,0,0,0,0,%s" %(v)
						# print "%s - %s" %(k,v)
			print warehouse_data
			for k,v in warehouse_data.iteritems():
				daily_rejects = get_rejects(k,'daily',warehouse.get("warehouse_inspection_type"))
				weekly_rejects = get_rejects(k,'weekly',warehouse.get("warehouse_inspection_type"))
				monthly_rejects = get_rejects(k,'monthly',warehouse.get("warehouse_inspection_type"))
				if len(v.split(','))==4:
					v = "%s,0,0" % v
				data.append([k,v.split(',')[0],v.split(',')[1],daily_rejects,v.split(',')[2],v.split(',')[3],weekly_rejects,v.split(',')[4],v.split(',')[5],monthly_rejects])
		data.append(["<b>Company Net Productivity</b>","","",""])
		net_today = """ 
            (select count(distinct sed.serial_no) as daily from `tabStock Entry` se inner join `tabStock Entry Detail` sed on sed.parent=se.name inner join tabItem i on i.item_code=sed.item_code where i.item_group='Laptops' and se.posting_date = '{1}' and sed.t_warehouse='G3 Ready To Ship - Uyn' and se.docstatus=1 and i.item_code not like '{0}' and se.purpose='Material Transfer')
            union
            (select count(distinct sed.serial_no) as daily from `tabStock Entry` se inner join `tabStock Entry Detail` sed on sed.parent=se.name inner join tabItem i on i.item_code=sed.item_code where i.item_group='Laptops' and se.posting_date = '{1}' and sed.t_warehouse='Amazon Warehouse - Uyn' and sed.s_warehouse<>'G3 Ready To Ship - Uyn' and se.docstatus=1 and i.item_code not like '{0}' and se.purpose='Material Transfer')
            union
            (select count(distinct dni.serial_no) as daily from `tabDelivery Note Item` dni inner join `tabDelivery Note` dn on dn.name=dni.parent inner join tabItem i on i.item_code=dni.item_code where i.item_group='Laptops' and dn.posting_date > '{1}' and dni.warehouse not in ('Amazon Warehouse - Uyn','G3 Ready To Ship - Uyn') and dn.is_return='0' and dni.item_code not like '{0}' and dn.docstatus='1')
        """.format("%Macbook%",self.yesterday_str)
		net_week = """
            (select count(distinct sed.serial_no) as weekly from `tabStock Entry` se inner join `tabStock Entry Detail` sed on sed.parent=se.name inner join tabItem i on i.item_code=sed.item_code where i.item_group='Laptops' and se.posting_date >='{0}' and se.posting_date <= '{1}' and sed.t_warehouse='G3 Ready To Ship - Uyn' and se.docstatus=1 and i.item_code not like '{2}' and se.purpose='Material Transfer' and MONTH(se.posting_date)=MONTH('{3}') and YEAR(se.posting_date)=YEAR('{3}'))
            union
            (select count(distinct sed.serial_no) as weekly from `tabStock Entry` se inner join `tabStock Entry Detail` sed on sed.parent=se.name inner join tabItem i on i.item_code=sed.item_code where i.item_group='Laptops' and se.posting_date >='{0}' and se.posting_date <= '{1}' and sed.t_warehouse='Amazon Warehouse - Uyn' and sed.s_warehouse<>'G3 Ready To Ship - Uyn' and se.docstatus=1 and i.item_code not like '{2}' and se.purpose='Material Transfer' and MONTH(se.posting_date)=MONTH('{3}') and YEAR(se.posting_date)=YEAR('{3}'))
            union
            (select count(distinct dni.serial_no) as weekly from `tabDelivery Note Item` dni inner join `tabDelivery Note` dn on dn.name=dni.parent inner join tabItem i on i.item_code=dni.item_code where i.item_group='Laptops' and dn.posting_date >='{0}' and dn.posting_date <= '{1}' and dni.warehouse not in ('Amazon Warehouse - Uyn','G3 Ready To Ship - Uyn') and dn.is_return='0' and dni.item_code not like '{2}' and dn.docstatus='1' and MONTH(dn.posting_date)=MONTH('{3}') and YEAR(dn.posting_date)=YEAR('{3}'))
        """.format(self.weekstartdate,self.weekenddate,"%Macbook%",self.today)
		net_month = """
            (select count(distinct sed.serial_no) as monthly from `tabStock Entry` se inner join `tabStock Entry Detail` sed on sed.parent=se.name inner join tabItem i on i.item_code=sed.item_code where i.item_group='Laptops' and MONTH(se.posting_date)=MONTH('{1}') and YEAR(se.posting_date) = YEAR('{1}') and sed.t_warehouse='G3 Ready To Ship - Uyn' and se.docstatus=1 and i.item_code not like '{0}' and se.purpose='Material Transfer')
            union
            (select count(distinct sed.serial_no) as monthly from `tabStock Entry` se inner join `tabStock Entry Detail` sed on sed.parent=se.name inner join tabItem i on i.item_code=sed.item_code where i.item_group='Laptops' and MONTH(se.posting_date)=MONTH('{1}') and YEAR(se.posting_date) = YEAR('{1}') and sed.t_warehouse='Amazon Warehouse - Uyn' and sed.s_warehouse<>'G3 Ready To Ship - Uyn' and se.docstatus=1 and i.item_code not like '{0}' and se.purpose='Material Transfer')
            union
            (select count(distinct dni.serial_no) as monthly from `tabDelivery Note Item` dni inner join `tabDelivery Note` dn on dn.name=dni.parent inner join tabItem i on i.item_code=dni.item_code where i.item_group='Laptops' and MONTH(dn.posting_date)=MONTH('{1}') and YEAR(dn.posting_date) = YEAR('{1}') and dni.warehouse not in ('Amazon Warehouse - Uyn','G3 Ready To Ship - Uyn') and dn.is_return='0' and dni.item_code not like '{0}' and dn.docstatus='1')
        """.format("%Macbook%",self.today)
		gross_today = """ 
            (select count(sed.serial_no) as daily from `tabStock Entry` se inner join `tabStock Entry Detail` sed on sed.parent=se.name inner join tabItem i on i.item_code=sed.item_code where i.item_group='Laptops' and se.posting_date = '{1}' and sed.t_warehouse='G3 Ready To Ship - Uyn' and se.docstatus=1 and i.item_code not like '{0}' and se.purpose='Material Transfer')
            union
            (select count(sed.serial_no) as daily from `tabStock Entry` se inner join `tabStock Entry Detail` sed on sed.parent=se.name inner join tabItem i on i.item_code=sed.item_code where i.item_group='Laptops' and se.posting_date = '{1}' and sed.t_warehouse='Amazon Warehouse - Uyn' and sed.s_warehouse<>'G3 Ready To Ship - Uyn' and se.docstatus=1 and i.item_code not like '{0}' and se.purpose='Material Transfer')
            union
            (select sum(dni.qty) as daily from `tabDelivery Note Item` dni inner join `tabDelivery Note` dn on dn.name=dni.parent inner join tabItem i on i.item_code=dni.item_code where i.item_group='Laptops' and dn.posting_date > '{1}' and dni.warehouse not in ('Amazon Warehouse - Uyn','G3 Ready To Ship - Uyn') and dn.is_return='0' and dni.item_code not like '{0}' and dn.docstatus='1')
        """.format("%Macbook%",self.yesterday_str)
		gross_week = """
            (select count(sed.serial_no) as weekly from `tabStock Entry` se inner join `tabStock Entry Detail` sed on sed.parent=se.name inner join tabItem i on i.item_code=sed.item_code where i.item_group='Laptops' and se.posting_date >='{0}' and se.posting_date <= '{1}' and sed.t_warehouse='G3 Ready To Ship - Uyn' and se.docstatus=1 and i.item_code not like '{2}' and se.purpose='Material Transfer' and MONTH(se.posting_date)=MONTH('{3}') and YEAR(se.posting_date)=YEAR('{3}'))
            union
            (select count(sed.serial_no) as weekly from `tabStock Entry` se inner join `tabStock Entry Detail` sed on sed.parent=se.name inner join tabItem i on i.item_code=sed.item_code where i.item_group='Laptops' and se.posting_date >='{0}' and se.posting_date <= '{1}' and sed.t_warehouse='Amazon Warehouse - Uyn' and sed.s_warehouse<>'G3 Ready To Ship - Uyn' and se.docstatus=1 and i.item_code not like '{2}' and se.purpose='Material Transfer' and MONTH(se.posting_date)=MONTH('{3}') and YEAR(se.posting_date)=YEAR('{3}'))
            union
            (select sum(dni.qty) as weekly from `tabDelivery Note Item` dni inner join `tabDelivery Note` dn on dn.name=dni.parent inner join tabItem i on i.item_code=dni.item_code where i.item_group='Laptops' and dn.posting_date >='{0}' and dn.posting_date <= '{1}' and dni.warehouse not in ('Amazon Warehouse - Uyn','G3 Ready To Ship - Uyn') and dn.is_return='0' and dni.item_code not like '{2}' and dn.docstatus='1' and MONTH(dn.posting_date)=MONTH('{3}') and YEAR(dn.posting_date)=YEAR('{3}'))
        """.format(self.weekstartdate,self.weekenddate,"%Macbook%",self.today)
		gross_month = """
            (select count(sed.serial_no) as monthly from `tabStock Entry` se inner join `tabStock Entry Detail` sed on sed.parent=se.name inner join tabItem i on i.item_code=sed.item_code where i.item_group='Laptops' and MONTH(se.posting_date)=MONTH('{1}') and YEAR(se.posting_date) = YEAR('{1}') and sed.t_warehouse='G3 Ready To Ship - Uyn' and se.docstatus=1 and i.item_code not like '{0}' and se.purpose='Material Transfer')
            union
            (select count(sed.serial_no) as monthly from `tabStock Entry` se inner join `tabStock Entry Detail` sed on sed.parent=se.name inner join tabItem i on i.item_code=sed.item_code where i.item_group='Laptops' and MONTH(se.posting_date)=MONTH('{1}') and YEAR(se.posting_date) = YEAR('{1}') and sed.t_warehouse='Amazon Warehouse - Uyn' and sed.s_warehouse<>'G3 Ready To Ship - Uyn' and se.docstatus=1 and i.item_code not like '{0}' and se.purpose='Material Transfer')
            union
            (select sum(dni.qty) as monthly from `tabDelivery Note Item` dni inner join `tabDelivery Note` dn on dn.name=dni.parent inner join tabItem i on i.item_code=dni.item_code where i.item_group='Laptops' and MONTH(dn.posting_date)=MONTH('{1}') and YEAR(dn.posting_date) = YEAR('{1}') and dni.warehouse not in ('Amazon Warehouse - Uyn','G3 Ready To Ship - Uyn') and dn.is_return='0' and dni.item_code not like '{0}' and dn.docstatus='1')
        """.format("%Macbook%",self.today)
		daily_net_prod_res = 0
		weekly_net_prod_res = 0
		montly_net_prod_res = 0
		daily_gross_prod_res = 0
		weekly_gross_prod_res = 0
		montly_gross_prod_res = 0
		for net_prod in frappe.db.sql(net_today,as_dict=1):
			if net_prod.get("daily"):
				daily_net_prod_res += net_prod.get("daily")
		for net_prod in frappe.db.sql(net_week,as_dict=1):
			if net_prod.get("weekly"):
				weekly_net_prod_res += net_prod.get("weekly")
		for net_prod in frappe.db.sql(net_month,as_dict=1):
			if net_prod.get("monthly"):
				montly_net_prod_res += net_prod.get("monthly")
		for gross_prod in frappe.db.sql(gross_today,as_dict=1):
			if gross_prod.get("daily"):
				daily_gross_prod_res += gross_prod.get("daily")
		for gross_prod in frappe.db.sql(gross_week,as_dict=1):
			if gross_prod.get("weekly"):
				weekly_gross_prod_res += gross_prod.get("weekly")
		for gross_prod in frappe.db.sql(gross_month,as_dict=1):
			if gross_prod.get("monthly"):
				montly_gross_prod_res += gross_prod.get("monthly")
		data.append(["",daily_gross_prod_res,daily_net_prod_res,"",weekly_gross_prod_res,weekly_net_prod_res,"",montly_gross_prod_res, montly_net_prod_res])
		return data

@frappe.whitelist()
def execute(filters=None):
    args = {

    }
    return ProductivityInsights(filters).run(args)

