# Copyright (c) 2015, Frappe Technologies Pvt. Ltd. and Contributors
# License: GNU General Public License v3. See license.txt

from __future__ import unicode_literals
import frappe
from frappe.utils import flt
from frappe import msgprint, _
import operator
from erpnext_ebay.vlog import vwrite
from datetime import datetime,timedelta
class ItemsNotInERP(object):
    def __init__(self, filters=None):
        self.filters = frappe._dict(filters or {})
        self.selected_date_obj = self.datetime.strptime(self.datetime.today().strftime('%Y-%m-%d'), '%Y-%m-%d')
	self.selected_month = self.datetime.today().strftime('%B')
        # self.selected_date_obj = self.datetime.strptime("2018-04-28", '%Y-%m-%d')
        self.today = str(self.datetime.today())[:10]
        
    def run(self, args):
        data = []
        

        columns = self.get_columns()
        data = self.get_data()
        # data = []
        return columns, data

    def get_columns(self):
        """return columns bab on filters"""
        columns = [
            _("Marketplace") + "::120", 
            _("Product ID") + ":Data:120",
            _("Link") + ":Data:320",
        ]
        return columns

    def is_duplicate_object(self,name_value_list,name_value):
        for ext_name_value in name_value_list:
            if ext_name_value[0]==name_value.get("item_group") and ext_name_value[1]==name_value.get("variant_of") and ext_name_value[2]==name_value.get("qty"):
                return False
        return True

    from datetime import timedelta,datetime
    
    def get_data(self):
        data = []
        ebay_data = self.get_ebay_data()
        ebaytwo_data = self.get_ebaytwo_data()
        amazon_data = self.get_amazon_data()
        data = ebay_data + ebaytwo_data + amazon_data
        return data
    def get_amazon_data(self):
        from erpnext_amazon.amazon_requests import get_request
        params = {'ReportType':"_GET_FLAT_FILE_OPEN_LISTINGS_DATA_"}
        report_result = get_request('request_report', params)
        i = 0
        amazon_prod_ids= []
        result=[]
        while True:
            i = i+1
            params = {'ReportRequestIdList':[report_result.RequestReportResult.ReportRequestInfo.ReportRequestId]}
            submission_list = get_request('get_report_request_list',params)
            import time
            info =  submission_list.GetReportRequestListResult.ReportRequestInfo[0]
            id = info.ReportRequestId
            status = info.ReportProcessingStatus
            vwrite('Submission Id: {}. Current status: {}'.format(id, status))

            if (status in ('_SUBMITTED_', '_IN_PROGRESS_', '_UNCONFIRMED_')):
                vwrite('Sleeping for 10s and check again....')
                time.sleep(10)
            elif (status == '_DONE_'):
                generated_report_id = info.GeneratedReportId
                reportResult = get_request('get_report',{'ReportId':generated_report_id})
                import re
                res_array = re.split(r'\n+', reportResult)
                i = 0
                for line in res_array:
                    if i > 0 and i < len(res_array)-1:
                        res_line = re.split(r'\t+', line)
                        amazon_prod_ids.append(res_line[1])
                    i = i+1
                break
            else:
                vwrite("Submission processing error. Quit.")
                break
            if i > 5:
                vwrite("Increment crossed 10")
                break
        erp_item_ids_sql = """ select GROUP_CONCAT(TRIM(amazon_product_id) SEPARATOR ', ') as amazon_product_ids from tabItem """
        for item_ids in frappe.db.sql(erp_item_ids_sql,as_dict=1):
            amazon_product_ids_in_erp = (item_ids.get("amazon_product_ids")).split(',')
        amazon_product_ids_in_erp = set(filter(None,map(unicode.strip, amazon_product_ids_in_erp)))
        res = [x for x in amazon_prod_ids if x not in amazon_product_ids_in_erp]
        for item in res:
            amazon_link = "https://www.amazon.in/dp/%s" % item
            result.append(["Amazon",item,amazon_link])
        vwrite("returning result of amazon data")
        vwrite(result)
        return result
    def get_ebay_data(self):
        result = []
        startTime = (datetime.now() + timedelta(-120)).isoformat()
        params = {
            "Pagination": {
                "EntriesPerPage": 200                
            },
            "StartTimeFrom": startTime,
            "StartTimeTo": datetime.now().isoformat()
        }
        from erpnext_ebay.ebay_requests import get_request
        seller_list_res = get_request('GetSellerList', 'trading', params)
        ebay_item_ids = []
        for item in seller_list_res.get("ItemArray").get("Item"):
            ebay_item_ids.append(item.get("ItemID"))
        ebay_item_ids = set(ebay_item_ids)
        # vwrite(ebay_item_ids)
        erp_item_ids_sql = """ select GROUP_CONCAT(TRIM(ebay_product_id) SEPARATOR ', ') as ebay_product_ids from tabItem """
        for item_ids in frappe.db.sql(erp_item_ids_sql,as_dict=1):
            ebay_product_ids_in_erp = (item_ids.get("ebay_product_ids")).split(',')
        ebay_product_ids_in_erp = set(filter(None,map(unicode.strip, ebay_product_ids_in_erp)))
        # vwrite(ebay_product_ids_in_erp)
        res = [x for x in ebay_item_ids if x not in ebay_product_ids_in_erp]
        for item in res:
            ebay_link = "http://www.ebay.in/itm/%s" %item
            result.append(["Ebay",item,ebay_link])
        return result
    
    def get_ebaytwo_data(self):
        result = []
        startTime = (datetime.now() + timedelta(-120)).isoformat()
        params = {
            "Pagination": {
                "EntriesPerPage": 200                
            },
            "StartTimeFrom": startTime,
            "StartTimeTo": datetime.now().isoformat()
        }
        from erpnext_ebaytwo.ebaytwo_requests import get_request
        seller_list_res = get_request('GetSellerList', 'trading', params)
        ebay_item_ids = []
        for item in seller_list_res.get("ItemArray").get("Item"):
            ebay_item_ids.append(item.get("ItemID"))
        ebay_item_ids = set(ebay_item_ids)
        # vwrite(ebay_item_ids)
        erp_item_ids_sql = """ select GROUP_CONCAT(TRIM(ebaytwo_product_id) SEPARATOR ', ') as ebaytwo_product_ids from tabItem """
        for item_ids in frappe.db.sql(erp_item_ids_sql,as_dict=1):
            ebay_product_ids_in_erp = (item_ids.get("ebaytwo_product_ids")).split(',')
        ebay_product_ids_in_erp = set(filter(None,map(unicode.strip, ebay_product_ids_in_erp)))
        # vwrite(ebay_product_ids_in_erp)
        res = [x for x in ebay_item_ids if x not in ebay_product_ids_in_erp]
        for item in res:
            ebay_link = "http://www.ebay.in/itm/%s" %item
            result.append(["Ebaytwo",item,ebay_link])
        return result

def execute(filters=None):
    args = {

    }
    return ItemsNotInERP(filters).run(args)
    # data = []

    # rows = get_dataget_data()
    # for row in rows:
    #   data.append(row)
    # return columns,data




