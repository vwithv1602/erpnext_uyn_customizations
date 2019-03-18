 # Copyright (c) 2013, vavcoders and contributors
# For license information, please see license.txt
# bench execute erpnext.selling.report.vamc_script_report___do_not_use.vamc_script_report___do_not_use.execute
###

# sudo chown -R vamc:vamc . && echo "" > sites/vebaylogfile_2019-01-28.txt && sudo chown -R frappe:frappe . && bench restart

# sudo chown -R vamc:vamc . && echo "" > sites/vebaylogfile_2019-01-28.txt


###

from __future__ import unicode_literals
import frappe
from frappe import msgprint, _
from datetime import datetime,timedelta
from erpnext_ebay.vlog import vwrite

class ProductivityInsightsDaily(object):
    def __init__(self, filters=None):
        self.selected_date_obj = datetime.strptime(datetime.today().strftime('%Y-%m-%d'), '%Y-%m-%d')
        self.selected_date_obj = self.selected_date_obj - timedelta(1)
        self.selected_date_str = str(self.selected_date_obj)[:10]

        self.yesterday_date_obj = self.selected_date_obj - timedelta(1)
        self.yesterday_date_str = str(self.yesterday_date_obj)[:10]

        self.tomorrow_date_obj = self.selected_date_obj + timedelta(1)
        self.tomorrow_date_str = str(self.tomorrow_date_obj)[:10]

        self.weekstartstr = self.week_range(self.selected_date_obj)[0]
        self.weekendstr = self.week_range(self.selected_date_obj)[1]

        self.monthdate = self.get_month_day_range(self.selected_date_obj)
        self.monthstartstr = str(self.monthdate[0])
        self.monthendstr = str(self.monthdate[1]+timedelta(1))
    
    def run(self, args):
		data = self.get_data()
		columns = self.get_columns()
		return columns, data
    
    def get_columns(self):
        """return columns bab on filters"""
        columns = [
            # _("Warehouse") + ":Link/Purchase Order:90",
            _("Warehouse<br>Employee") + ":Data:180",
            _("Gross Day") + ":Data:90",
            _("Net Day") + ":Data:90",
            _("Day Rejects") + ":Data:90",
            _("Gross Week") + ":Data:90",
            _("Net Week") + ":Data:90",
            _("Week Rejects") + ":Data:90",
            _("Gross Month") + ":Data:90",
            _("Net Month") + ":Data:90",
            _("Month Rejects") + ":Data:100",
        ]
        return columns

    def get_data(self):
        data = []
        # Get employees
        employees_sql = """ select user_id from `tabEmployee` where status='Active' """
        employees_res = frappe.db.sql(employees_sql,as_dict=1)
        
        # Get warehouses and sequence numbers
        warehouse_sequence_sql = """ select warehouse_name,warehouse_sequence_number,warehouse_inspection_type from `tabWarehouse` where warehouse_sequence_number<>'' """
        warehouse_sequence_res = frappe.db.sql(warehouse_sequence_sql,as_dict=1)
        for warehouse in warehouse_sequence_res:
            employees = {}
            active_employees = []
            for employee in employees_res:
                employees[employee.get('user_id')] = {}
                active_employees.append(employee.get('user_id'))
            data.append(["<b>"+warehouse.get("warehouse_name")+"</b>"])

            # Gross Daily
            gross_day_sql = """ select A.owner,count(A.item_serial_no) as count,A.creation,A.name
                from `tabQuality Inspection` as A 
                where A.creation > '{0}' and A.creation < '{1}' and A.docstatus = 1 and A.inspection_type='{2}'
                Group By A.owner """.format(self.selected_date_str,self.tomorrow_date_str,warehouse.get("warehouse_inspection_type"))
            gross_day_res = frappe.db.sql(gross_day_sql,as_dict=1)
            for row in gross_day_res:
                if row.get("owner") in active_employees:
                    employees[row.get("owner")] = {'gross_day': row.get("count")}

            # Net Daily
            net_day_sql = """ select A.owner,count(A.item_serial_no) as count,A.creation,A.name
                from `tabQuality Inspection` as A 
                inner join 
                (select item_serial_no,min(creation) as min_creation from `tabQuality Inspection` where docstatus =1 and inspection_type = '{2}' group by item_serial_no ) as B on (A.item_serial_no= B.item_serial_no and A.creation = B.min_creation)
                where A.creation > '{0}' and A.creation < '{1}' and A.docstatus = 1
                Group By A.owner """.format(self.selected_date_str,self.tomorrow_date_str,warehouse.get("warehouse_inspection_type"))
            net_day_res = frappe.db.sql(net_day_sql,as_dict=1)
            for row in net_day_res:
                if row.get("owner") in active_employees:
                    employees[row.get("owner")]['net_day'] = row.get("count")

            # Gross Weekly
            gross_week_sql = """ select A.owner,count(A.item_serial_no) as count,A.creation,A.name
                from `tabQuality Inspection` as A 
                where A.creation >= '{0}' and A.creation <= '{1}' and A.docstatus = 1 and A.inspection_type='{2}'
                Group By A.owner """.format(self.weekstartstr,self.weekendstr,warehouse.get("warehouse_inspection_type"))
            gross_week_res = frappe.db.sql(gross_week_sql,as_dict=1)
            for row in gross_week_res:
                if row.get("owner") in active_employees:
                    employees[row.get("owner")]['gross_week'] = row.get("count")

            # Net Weekly
            net_week_sql = """ select A.owner,count(A.item_serial_no) as count,A.creation,A.name
                from `tabQuality Inspection` as A 
                inner join 
                (select item_serial_no,min(creation) as min_creation from `tabQuality Inspection` where docstatus =1 and inspection_type = '{2}' group by item_serial_no ) as B on (A.item_serial_no= B.item_serial_no and A.creation = B.min_creation)
                where A.creation >= '{0}' and A.creation <= '{1}' and A.docstatus = 1
                Group By A.owner """.format(self.weekstartstr,self.weekendstr,warehouse.get("warehouse_inspection_type"))
            net_week_res = frappe.db.sql(net_week_sql,as_dict=1)
            for row in net_week_res:
                if row.get("owner") in active_employees:
                    employees[row.get("owner")]['net_week'] = row.get("count")
            # Gross Monthly
            gross_month_sql = """ select A.owner,count(A.item_serial_no) as count,A.creation,A.name
                from `tabQuality Inspection` as A 
                where A.creation > '{0}' and A.creation < '{1}' and A.docstatus = 1 and A.inspection_type='{2}'
                Group By A.owner """.format(self.monthstartstr,self.monthendstr,warehouse.get("warehouse_inspection_type"))
            gross_month_res = frappe.db.sql(gross_month_sql,as_dict=1)
            for row in gross_month_res:
                if row.get("owner") in active_employees:
                    employees[row.get("owner")]['gross_month'] = row.get("count")

            # Net Monthly
            net_month_sql = """ select A.owner,count(A.item_serial_no) as count,A.creation,A.name
                from `tabQuality Inspection` as A 
                inner join 
                (select item_serial_no,min(creation) as min_creation from `tabQuality Inspection` where docstatus =1 and inspection_type = '{2}' group by item_serial_no ) as B on (A.item_serial_no= B.item_serial_no and A.creation = B.min_creation)
                where A.creation > '{0}' and A.creation < '{1}' and A.docstatus = 1
                Group By A.owner """.format(self.monthstartstr,self.monthendstr,warehouse.get("warehouse_inspection_type"))
            net_month_res = frappe.db.sql(net_month_sql,as_dict=1)
            for row in net_month_res:
                if row.get("owner") in active_employees:
                    employees[row.get("owner")]['net_month'] = row.get("count")
            
            employees = dict((k, v) for k, v in employees.iteritems() if v!={})
            for employee,productivity in employees.iteritems():
                daily_rejects = self.get_rejects(employee,'daily',warehouse.get("warehouse_inspection_type"))
                weekly_rejects = self.get_rejects(employee,'weekly',warehouse.get("warehouse_inspection_type"))
                monthly_rejects = self.get_rejects(employee,'monthly',warehouse.get("warehouse_inspection_type"))
                data.append([employee,productivity.get("gross_day"),productivity.get("net_day"),daily_rejects,productivity.get("gross_week"),productivity.get("net_week"),weekly_rejects,productivity.get("gross_month"),"<b>"+str(productivity.get("net_month"))+"</b>",monthly_rejects])
        data.append(["<b>PAINTING PRODUCTIVITY</b>","","",""])
        painting_productivity = self.get_painting_productivity()
        data.append(painting_productivity)
        data.append(["<b>CUSTOMER RETURNS PRODUCTIVITY</b>","","",""])
        customer_returns_productivity = self.get_customer_returns_productivity()
        data.append(customer_returns_productivity)
        data.append(["<b>COMPANY NET PRODUCTIVITY</b>","","",""])
        company_net_productivity = self.get_company_net_productivity()
        data.append(company_net_productivity)
        

        return data

    def get_rejects(self,emp,period,inspection_type):
        rejects = 0
        if period=='daily':
            reject_sql = """ select count(*) as count from `tabRejects` where rejected_date='{2}' and inspected_by='{0}' and inspection_type='{1}' and ste not in (select  name from `tabStock Entry` where docstatus<>'1')""".format(emp,inspection_type,self.selected_date_str)
            rejects = frappe.db.sql(reject_sql,as_dict=1)[0].get("count")
        elif period=='weekly':
            reject_sql = """ select count(*) as count from `tabRejects` where rejected_date>'{1}' and rejected_date<='{2}' and inspected_by='{0}'  and inspection_type='{3}' and ste not in (select  name from `tabStock Entry` where docstatus<>'1') and MONTH(rejected_date)=MONTH('{4}') and YEAR(rejected_date)=YEAR('{4}')""".format(emp,self.weekstartstr,self.weekendstr,inspection_type,self.selected_date_str)
            print reject_sql
            rejects = frappe.db.sql(reject_sql,as_dict=1)[0].get("count")
        elif period=='monthly':
            reject_sql = """ select count(*) as count from `tabRejects` where MONTH(rejected_date)=MONTH('{2}') and YEAR(rejected_date)=YEAR('{2}') and inspected_by='{0}' and inspection_type='{1}' and ste not in (select  name from `tabStock Entry` where docstatus<>'1')""".format(emp,inspection_type,self.selected_date_str)
            rejects = frappe.db.sql(reject_sql,as_dict=1)[0].get("count")
        return rejects
    def week_range(self,date):
        """Find the first/last day of the week for the given day.
        Assuming weeks start on Sunday and end on Saturday.
        Returns a tuple of ``(start_date, end_date)``.
        """
        # isocalendar calculates the year, week of the year, and day of the week.
        # dow is Mon = 1, Sat = 6, Sun = 7
        date = date - timedelta(1)
        year, week, dow = date.isocalendar()
        # Find the first day of the week.
        if dow == 7:
            # Since we want to start with Sunday, let's test for that condition.
            start_date = date
        else:
            # Otherwise, subtract `dow` number days to get the first day
            start_date = date - timedelta(dow)
        # Now, add 6 for the last day of the week (i.e., count up to Saturday)
        end_date = start_date + timedelta(7)
        return (start_date.strftime('%Y-%m-%d'), end_date.strftime('%Y-%m-%d'))


    def get_month_day_range(self,date):
        from dateutil.relativedelta import relativedelta
        """
        For a date 'date' returns the start and end date for the month of 'date'.
        Month with 31 days:
        >>> date = datetime.date(2011, 7, 27)
        >>> get_month_day_range(date)
        (datetime.date(2011, 7, 1), datetime.date(2011, 7, 31))
        Month with 28 days:
        >>> date = datetime.date(2011, 2, 15)
        >>> get_month_day_range(date)
        (datetime.date(2011, 2, 1), datetime.date(2011, 2, 28))
        """

        last_day = date + relativedelta(day=1, months=+1, days=-1)
        first_day = date + relativedelta(day=1)
        return first_day, last_day

    def get_company_net_productivity(self):
        net_today = """ 
            (select count(distinct sed.serial_no) as daily from `tabStock Entry` se inner join `tabStock Entry Detail` sed on sed.parent=se.name inner join tabItem i on i.item_code=sed.item_code where i.item_group in ('Laptops','Desktops') and se.posting_date = '{1}' and sed.t_warehouse='G3 Ready To Ship - Uyn' and se.docstatus=1 and se.purpose='Material Transfer')
            union
            (select count(distinct sed.serial_no) as daily from `tabStock Entry` se inner join `tabStock Entry Detail` sed on sed.parent=se.name inner join tabItem i on i.item_code=sed.item_code where i.item_group in ('Laptops','Desktops') and se.posting_date = '{1}' and sed.t_warehouse='Amazon Warehouse - Uyn' and sed.s_warehouse<>'G3 Ready To Ship - Uyn' and se.docstatus=1 and se.purpose='Material Transfer')
            union
            (select count(distinct dni.serial_no) as daily from `tabDelivery Note Item` dni inner join `tabDelivery Note` dn on dn.name=dni.parent inner join tabItem i on i.item_code=dni.item_code where i.item_group in ('Laptops','Desktops') and dn.posting_date = '{1}' and dni.warehouse not in ('Amazon Warehouse - Uyn','G3 Ready To Ship - Uyn') and dn.is_return='0' and dn.docstatus='1')
        """.format("%Macbook%",self.selected_date_str)
        net_week = """
            (select count(distinct sed.serial_no) as weekly from `tabStock Entry` se inner join `tabStock Entry Detail` sed on sed.parent=se.name inner join tabItem i on i.item_code=sed.item_code where i.item_group in ('Laptops','Desktops') and se.posting_date >='{0}' and se.posting_date <= '{1}' and sed.t_warehouse='G3 Ready To Ship - Uyn' and se.docstatus=1 and se.purpose='Material Transfer' and MONTH(se.posting_date)=MONTH('{3}') and YEAR(se.posting_date)=YEAR('{3}'))
            union
            (select count(distinct sed.serial_no) as weekly from `tabStock Entry` se inner join `tabStock Entry Detail` sed on sed.parent=se.name inner join tabItem i on i.item_code=sed.item_code where i.item_group in ('Laptops','Desktops') and se.posting_date >='{0}' and se.posting_date <= '{1}' and sed.t_warehouse='Amazon Warehouse - Uyn' and sed.s_warehouse<>'G3 Ready To Ship - Uyn' and se.docstatus=1 and se.purpose='Material Transfer' and MONTH(se.posting_date)=MONTH('{3}') and YEAR(se.posting_date)=YEAR('{3}'))
            union
            (select count(distinct dni.serial_no) as weekly from `tabDelivery Note Item` dni inner join `tabDelivery Note` dn on dn.name=dni.parent inner join tabItem i on i.item_code=dni.item_code where i.item_group in ('Laptops','Desktops') and dn.posting_date >='{0}' and dn.posting_date <= '{1}' and dni.warehouse not in ('Amazon Warehouse - Uyn','G3 Ready To Ship - Uyn') and dn.is_return='0' and dn.docstatus='1' and MONTH(dn.posting_date)=MONTH('{3}') and YEAR(dn.posting_date)=YEAR('{3}'))
        """.format(self.weekstartstr,self.weekendstr,"%Macbook%",self.selected_date_str)
        net_month = """
            (select count(distinct sed.serial_no) as monthly from `tabStock Entry` se inner join `tabStock Entry Detail` sed on sed.parent=se.name inner join tabItem i on i.item_code=sed.item_code where i.item_group in ('Laptops','Desktops') and MONTH(se.posting_date)=MONTH('{1}') and YEAR(se.posting_date) = YEAR('{1}') and sed.t_warehouse='G3 Ready To Ship - Uyn' and se.docstatus=1 and se.purpose='Material Transfer')
            union
            (select count(distinct sed.serial_no) as monthly from `tabStock Entry` se inner join `tabStock Entry Detail` sed on sed.parent=se.name inner join tabItem i on i.item_code=sed.item_code where i.item_group in ('Laptops','Desktops') and MONTH(se.posting_date)=MONTH('{1}') and YEAR(se.posting_date) = YEAR('{1}') and sed.t_warehouse='Amazon Warehouse - Uyn' and sed.s_warehouse<>'G3 Ready To Ship - Uyn' and se.docstatus=1 and se.purpose='Material Transfer')
            union
            (select count(distinct dni.serial_no) as monthly from `tabDelivery Note Item` dni inner join `tabDelivery Note` dn on dn.name=dni.parent inner join tabItem i on i.item_code=dni.item_code where i.item_group in ('Laptops','Desktops') and MONTH(dn.posting_date)=MONTH('{1}') and YEAR(dn.posting_date) = YEAR('{1}') and dni.warehouse not in ('Amazon Warehouse - Uyn','G3 Ready To Ship - Uyn') and dn.is_return='0' and dn.docstatus='1')
        """.format("%Macbook%",self.selected_date_str)
        gross_today = """ 
            (select count(sed.serial_no) as daily from `tabStock Entry` se inner join `tabStock Entry Detail` sed on sed.parent=se.name inner join tabItem i on i.item_code=sed.item_code where i.item_group in ('Laptops','Desktops') and se.posting_date = '{1}' and sed.t_warehouse='G3 Ready To Ship - Uyn' and se.docstatus=1 and se.purpose='Material Transfer')
            union
            (select count(sed.serial_no) as daily from `tabStock Entry` se inner join `tabStock Entry Detail` sed on sed.parent=se.name inner join tabItem i on i.item_code=sed.item_code where i.item_group in ('Laptops','Desktops') and se.posting_date = '{1}' and sed.t_warehouse='Amazon Warehouse - Uyn' and sed.s_warehouse<>'G3 Ready To Ship - Uyn' and se.docstatus=1 and se.purpose='Material Transfer')
            union
            (select sum(dni.qty) as daily from `tabDelivery Note Item` dni inner join `tabDelivery Note` dn on dn.name=dni.parent inner join tabItem i on i.item_code=dni.item_code where i.item_group in ('Laptops','Desktops') and dn.posting_date = '{1}' and dni.warehouse not in ('Amazon Warehouse - Uyn','G3 Ready To Ship - Uyn') and dn.is_return='0' and dn.docstatus='1')
        """.format("%Macbook%",self.selected_date_str)
        gross_week = """
            (select count(sed.serial_no) as weekly from `tabStock Entry` se inner join `tabStock Entry Detail` sed on sed.parent=se.name inner join tabItem i on i.item_code=sed.item_code where i.item_group in ('Laptops','Desktops') and se.posting_date >='{0}' and se.posting_date <= '{1}' and sed.t_warehouse='G3 Ready To Ship - Uyn' and se.docstatus=1 and se.purpose='Material Transfer' and MONTH(se.posting_date)=MONTH('{3}') and YEAR(se.posting_date)=YEAR('{3}'))
            union
            (select count(sed.serial_no) as weekly from `tabStock Entry` se inner join `tabStock Entry Detail` sed on sed.parent=se.name inner join tabItem i on i.item_code=sed.item_code where i.item_group in ('Laptops','Desktops') and se.posting_date >='{0}' and se.posting_date <= '{1}' and sed.t_warehouse='Amazon Warehouse - Uyn' and sed.s_warehouse<>'G3 Ready To Ship - Uyn' and se.docstatus=1 and se.purpose='Material Transfer' and MONTH(se.posting_date)=MONTH('{3}') and YEAR(se.posting_date)=YEAR('{3}'))
            union
            (select sum(dni.qty) as weekly from `tabDelivery Note Item` dni inner join `tabDelivery Note` dn on dn.name=dni.parent inner join tabItem i on i.item_code=dni.item_code where i.item_group in ('Laptops','Desktops') and dn.posting_date >='{0}' and dn.posting_date <= '{1}' and dni.warehouse not in ('Amazon Warehouse - Uyn','G3 Ready To Ship - Uyn') and dn.is_return='0' and dn.docstatus='1' and MONTH(dn.posting_date)=MONTH('{3}') and YEAR(dn.posting_date)=YEAR('{3}'))
        """.format(self.weekstartstr,self.weekendstr,"%Macbook%",self.selected_date_str)
        gross_month = """
            (select count(sed.serial_no) as monthly from `tabStock Entry` se inner join `tabStock Entry Detail` sed on sed.parent=se.name inner join tabItem i on i.item_code=sed.item_code where i.item_group in ('Laptops','Desktops') and MONTH(se.posting_date)=MONTH('{1}') and YEAR(se.posting_date) = YEAR('{1}') and sed.t_warehouse='G3 Ready To Ship - Uyn' and se.docstatus=1 and se.purpose='Material Transfer')
            union
            (select count(sed.serial_no) as monthly from `tabStock Entry` se inner join `tabStock Entry Detail` sed on sed.parent=se.name inner join tabItem i on i.item_code=sed.item_code where i.item_group in ('Laptops','Desktops') and MONTH(se.posting_date)=MONTH('{1}') and YEAR(se.posting_date) = YEAR('{1}') and sed.t_warehouse='Amazon Warehouse - Uyn' and sed.s_warehouse<>'G3 Ready To Ship - Uyn' and se.docstatus=1 and se.purpose='Material Transfer')
            union
            (select sum(dni.qty) as monthly from `tabDelivery Note Item` dni inner join `tabDelivery Note` dn on dn.name=dni.parent inner join tabItem i on i.item_code=dni.item_code where i.item_group in ('Laptops','Desktops') and MONTH(dn.posting_date)=MONTH('{1}') and YEAR(dn.posting_date) = YEAR('{1}') and dni.warehouse not in ('Amazon Warehouse - Uyn','G3 Ready To Ship - Uyn') and dn.is_return='0' and dn.docstatus='1')
        """.format("%Macbook%",self.selected_date_str)
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

        return ["",daily_gross_prod_res,daily_net_prod_res,"",weekly_gross_prod_res,weekly_net_prod_res,"",montly_gross_prod_res, "<b>"+str(montly_net_prod_res)+"</b>"]

    def get_painting_productivity(self):
        net_today_sql = """
            (select count(distinct sed.serial_no) as daily from `tabStock Entry` se inner join `tabStock Entry Detail` sed on sed.parent=se.name inner join tabItem i on i.item_code=sed.item_code where i.item_group in ('Laptops','Desktops') and se.posting_date = '{1}' and sed.t_warehouse='Final QC - Uyn' and sed.s_warehouse='Painting - Uyn' and se.docstatus=1 and se.purpose='Material Transfer')
        """.format("%Macbook%",self.selected_date_str)
        gross_today_sql = """
            (select count(sed.serial_no) as daily from `tabStock Entry` se inner join `tabStock Entry Detail` sed on sed.parent=se.name inner join tabItem i on i.item_code=sed.item_code where i.item_group in ('Laptops','Desktops') and se.posting_date = '{1}' and sed.t_warehouse='Final QC - Uyn' and sed.s_warehouse='Painting - Uyn' and se.docstatus=1 and se.purpose='Material Transfer')
        """.format("%Macbook%",self.selected_date_str)
        reject_today_sql = """
            (select count(sed.serial_no) as daily from `tabStock Entry` se inner join `tabStock Entry Detail` sed on sed.parent=se.name inner join tabItem i on i.item_code=sed.item_code where i.item_group in ('Laptops','Desktops') and se.posting_date = '{1}' and sed.t_warehouse='Painting - Uyn' and sed.s_warehouse='Final QC - Uyn' and se.docstatus=1 and se.purpose='Material Transfer')
        """.format("%Macbook%",self.selected_date_str)
        net_week_sql = """
            (select count(distinct sed.serial_no) as weekly from `tabStock Entry` se inner join `tabStock Entry Detail` sed on sed.parent=se.name inner join tabItem i on i.item_code=sed.item_code where i.item_group in ('Laptops','Desktops') and se.posting_date >='{0}' and se.posting_date <= '{1}' and sed.t_warehouse='Final QC - Uyn' and sed.s_warehouse='Painting - Uyn' and se.docstatus=1 and se.purpose='Material Transfer' and MONTH(se.posting_date)=MONTH('{3}') and YEAR(se.posting_date)=YEAR('{3}'))
        """.format(self.weekstartstr,self.weekendstr,"%Macbook%",self.selected_date_str)
        gross_week_sql = """
            (select count(sed.serial_no) as weekly from `tabStock Entry` se inner join `tabStock Entry Detail` sed on sed.parent=se.name inner join tabItem i on i.item_code=sed.item_code where i.item_group in ('Laptops','Desktops') and se.posting_date >='{0}' and se.posting_date <= '{1}' and sed.t_warehouse='Final QC - Uyn' and sed.s_warehouse='Painting - Uyn' and se.docstatus=1 and se.purpose='Material Transfer' and MONTH(se.posting_date)=MONTH('{3}') and YEAR(se.posting_date)=YEAR('{3}'))
        """.format(self.weekstartstr,self.weekendstr,"%Macbook%",self.selected_date_str)
        reject_week_sql = """
            (select count(sed.serial_no) as weekly from `tabStock Entry` se inner join `tabStock Entry Detail` sed on sed.parent=se.name inner join tabItem i on i.item_code=sed.item_code where i.item_group in ('Laptops','Desktops') and se.posting_date >='{0}' and se.posting_date <= '{1}' and sed.t_warehouse='Painting - Uyn' and sed.s_warehouse='Final QC - Uyn' and se.docstatus=1 and se.purpose='Material Transfer' and MONTH(se.posting_date)=MONTH('{3}') and YEAR(se.posting_date)=YEAR('{3}'))
        """.format(self.weekstartstr,self.weekendstr,"%Macbook%",self.selected_date_str)
        net_month_sql = """
            (select count(distinct sed.serial_no) as monthly from `tabStock Entry` se inner join `tabStock Entry Detail` sed on sed.parent=se.name inner join tabItem i on i.item_code=sed.item_code where i.item_group in ('Laptops','Desktops') and MONTH(se.posting_date)=MONTH('{1}') and YEAR(se.posting_date) = YEAR('{1}') and sed.t_warehouse='Final QC - Uyn' and sed.s_warehouse='Painting - Uyn' and se.docstatus=1 and se.purpose='Material Transfer')
        """.format("%Macbook%",self.selected_date_str)
        gross_month_sql = """
            (select count(sed.serial_no) as monthly from `tabStock Entry` se inner join `tabStock Entry Detail` sed on sed.parent=se.name inner join tabItem i on i.item_code=sed.item_code where i.item_group in ('Laptops','Desktops') and MONTH(se.posting_date)=MONTH('{1}') and YEAR(se.posting_date) = YEAR('{1}') and sed.t_warehouse='Final QC - Uyn' and sed.s_warehouse='Painting - Uyn' and se.docstatus=1 and se.purpose='Material Transfer')
        """.format("%Macbook%",self.selected_date_str)
        reject_month_sql = """
            (select count(sed.serial_no) as monthly from `tabStock Entry` se inner join `tabStock Entry Detail` sed on sed.parent=se.name inner join tabItem i on i.item_code=sed.item_code where i.item_group in ('Laptops','Desktops') and MONTH(se.posting_date)=MONTH('{1}') and YEAR(se.posting_date) = YEAR('{1}') and sed.t_warehouse='Painting - Uyn' and sed.s_warehouse='Final QC - Uyn' and se.docstatus=1 and se.purpose='Material Transfer')
        """.format("%Macbook%",self.selected_date_str)

        gross_today = frappe.db.sql(gross_today_sql,as_dict=1)[0].get("daily")
        net_today = frappe.db.sql(net_today_sql,as_dict=1)[0].get("daily")
        reject_today = frappe.db.sql(reject_today_sql,as_dict=1)[0].get("daily")
        gross_week = frappe.db.sql(gross_week_sql,as_dict=1)[0].get("weekly")
        net_week = frappe.db.sql(net_week_sql,as_dict=1)[0].get("weekly")
        reject_week = frappe.db.sql(reject_week_sql,as_dict=1)[0].get("weekly")
        gross_month = frappe.db.sql(gross_month_sql,as_dict=1)[0].get("monthly")
        net_month = frappe.db.sql(net_month_sql,as_dict=1)[0].get("monthly")
        reject_month = frappe.db.sql(reject_month_sql,as_dict=1)[0].get("monthly")
        return ["",gross_today,net_today,reject_today,gross_week,net_week,reject_week,gross_month,"<b>"+str(net_month)+"</b>",reject_month]
    def get_customer_returns_productivity(self):
		# Get stock movement to 'Customer Support - Uyn'
		gross_returns_today_sql = """ select count(sed.serial_no) as daily from `tabStock Entry` se inner join `tabStock Entry Detail` sed on sed.parent=se.name inner join tabItem i on i.item_code=sed.item_code where i.item_group in ('Laptops','Desktops') and se.posting_date = '{0}' and sed.s_warehouse='Customer Support - Uyn' and se.purpose='Material Transfer' and sed.t_warehouse='Final QC - Uyn' and se.docstatus=1 """.format(self.selected_date_str)
		net_returns_today_sql = """ select count(distinct sed.serial_no) as daily from `tabStock Entry` se inner join `tabStock Entry Detail` sed on sed.parent=se.name inner join tabItem i on i.item_code=sed.item_code where i.item_group in ('Laptops','Desktops') and se.posting_date = '{0}' and sed.s_warehouse='Customer Support - Uyn' and se.purpose='Material Transfer' and sed.t_warehouse='Final QC - Uyn' and se.docstatus=1 """.format(self.selected_date_str)
		rejected_returns_today_sql = """ select count(sed.serial_no) as daily from `tabStock Entry` se inner join `tabStock Entry Detail` sed on sed.parent=se.name inner join tabItem i on i.item_code=sed.item_code where i.item_group in ('Laptops','Desktops') and se.posting_date = '{0}' and sed.t_warehouse='Customer Support - Uyn' and se.purpose='Material Transfer' and sed.s_warehouse='Final QC - Uyn' and se.docstatus=1 """.format(self.selected_date_str)
		gross_returns = frappe.db.sql(gross_returns_today_sql,as_dict=1)[0].get("daily")
		net_returns = frappe.db.sql(net_returns_today_sql,as_dict=1)[0].get("daily")
		rejected_returns = frappe.db.sql(rejected_returns_today_sql,as_dict=1)[0].get("daily")

		gross_returns_week_sql = """ select count(sed.serial_no) as weekly from `tabStock Entry` se inner join `tabStock Entry Detail` sed on sed.parent=se.name inner join tabItem i on i.item_code=sed.item_code where i.item_group in ('Laptops','Desktops') and se.posting_date >='{0}' and se.posting_date <= '{1}' and sed.s_warehouse='Customer Support - Uyn' and se.purpose='Material Transfer' and sed.t_warehouse='Final QC - Uyn' and se.docstatus=1 and MONTH(se.posting_date)=MONTH('{2}') and YEAR(se.posting_date)=YEAR('{2}')""".format(self.weekstartstr,self.weekendstr,self.selected_date_str)
		net_returns_week_sql = """ select count(distinct sed.serial_no) as weekly from `tabStock Entry` se inner join `tabStock Entry Detail` sed on sed.parent=se.name inner join tabItem i on i.item_code=sed.item_code where i.item_group in ('Laptops','Desktops') and se.posting_date >='{0}' and se.posting_date <= '{1}' and sed.s_warehouse='Customer Support - Uyn' and se.purpose='Material Transfer' and sed.t_warehouse='Final QC - Uyn' and se.docstatus=1 and MONTH(se.posting_date)=MONTH('{2}') and YEAR(se.posting_date)=YEAR('{2}')""".format(self.weekstartstr,self.weekendstr,self.selected_date_str)
		rejected_returns_week_sql = """ select count(sed.serial_no) as weekly from `tabStock Entry` se inner join `tabStock Entry Detail` sed on sed.parent=se.name inner join tabItem i on i.item_code=sed.item_code where i.item_group in ('Laptops','Desktops') and se.posting_date >='{0}' and se.posting_date <= '{1}' and sed.t_warehouse='Customer Support - Uyn' and se.purpose='Material Transfer' and sed.s_warehouse='Final QC - Uyn' and se.docstatus=1 and MONTH(se.posting_date)=MONTH('{2}') and YEAR(se.posting_date)=YEAR('{2}')""".format(self.weekstartstr,self.weekendstr,self.selected_date_str)

		gross_returns_weekly = frappe.db.sql(gross_returns_week_sql,as_dict=1)[0].get("weekly")
		net_returns_weekly = frappe.db.sql(net_returns_week_sql,as_dict=1)[0].get("weekly")
		rejected_returns_weekly = frappe.db.sql(rejected_returns_week_sql,as_dict=1)[0].get("weekly")

		gross_returns_month_sql = """ select count(sed.serial_no) as monthly from `tabStock Entry` se inner join `tabStock Entry Detail` sed on sed.parent=se.name inner join tabItem i on i.item_code=sed.item_code where i.item_group in ('Laptops','Desktops') and MONTH(se.posting_date)=MONTH('{0}') and YEAR(se.posting_date) = YEAR('{0}') and sed.s_warehouse='Customer Support - Uyn' and se.purpose='Material Transfer' and sed.t_warehouse='Final QC - Uyn' and se.docstatus=1 """.format(self.selected_date_str)
		net_returns_month_sql = """ select count(distinct sed.serial_no) as monthly from `tabStock Entry` se inner join `tabStock Entry Detail` sed on sed.parent=se.name inner join tabItem i on i.item_code=sed.item_code where i.item_group in ('Laptops','Desktops') and MONTH(se.posting_date)=MONTH('{0}') and YEAR(se.posting_date) = YEAR('{0}') and sed.s_warehouse='Customer Support - Uyn' and se.purpose='Material Transfer' and sed.t_warehouse='Final QC - Uyn' and se.docstatus=1 """.format(self.selected_date_str)
		rejected_returns_month_sql = """ select count(sed.serial_no) as monthly from `tabStock Entry` se inner join `tabStock Entry Detail` sed on sed.parent=se.name inner join tabItem i on i.item_code=sed.item_code where i.item_group in ('Laptops','Desktops') and MONTH(se.posting_date)=MONTH('{0}') and YEAR(se.posting_date) = YEAR('{0}') and sed.t_warehouse='Customer Support - Uyn' and se.purpose='Material Transfer' and sed.s_warehouse='Final QC - Uyn' and se.docstatus=1 """.format(self.selected_date_str)

		gross_returns_monthly = frappe.db.sql(gross_returns_month_sql,as_dict=1)[0].get("monthly")
		net_returns_monthly = frappe.db.sql(net_returns_month_sql,as_dict=1)[0].get("monthly")
		rejected_returns_monthly = frappe.db.sql(rejected_returns_month_sql,as_dict=1)[0].get("monthly")
		return ["Pankaj",gross_returns,net_returns,rejected_returns,gross_returns_weekly,net_returns_weekly,rejected_returns_weekly,gross_returns_monthly,net_returns_monthly,rejected_returns_monthly]

@frappe.whitelist(allow_guest=True)
def execute(filters=None):
    args = {

    }
    return ProductivityInsightsDaily().run(args)





