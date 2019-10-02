# Copyright (c) 2013, vavcoders and contributors
# For license information, please see license.txt

from __future__ import unicode_literals
import frappe
from frappe import msgprint, _
from datetime import datetime,timedelta,date
from sets import Set
from erpnext_ebay.vlog import vwrite

def get_columns():
        columns = [
            _("Models") + ":Data:180",
            _("Count") + ":Data:100"
        ]
        return columns
def get_models_to_item_code():
	list_dict_of_models_and_item_code = frappe.get_list('Item', filters={'item_group' : ("in",'Laptops,Desktops,Mobiles'),'item_model':('not like','')}, fields=['name','item_model'])
	model_to_item_code_map = {} 
	for item in list_dict_of_models_and_item_code:
		if item.get('item_model') in model_to_item_code_map:
			model_to_item_code_map[item.get('item_model')].append(item.get('name'))
		else:
			model_to_item_code_map[item.get('item_model')] = list()
	
	return model_to_item_code_map

def get_count_by_item_code():
	list_dict_of_item_code_and_serial_no = frappe.get_list('Serial No',filters={'warehouse':('not like','')},fields=['name','item_code'])
	item_code_to_count_map = {}
	for item in list_dict_of_item_code_and_serial_no:
		if item.get('item_code') in item_code_to_count_map:
			item_code_to_count_map[item.get('item_code')] += 1
		else:
			item_code_to_count_map[item.get('item_code')] = 0
	
	return item_code_to_count_map

def get_data():
	models_to_item_code_map = get_models_to_item_code()
	item_code_to_count_map = get_count_by_item_code()
	models_to_count_map = {}
	for model in models_to_item_code_map:
		for item_code in models_to_item_code_map[model]:
			if model in models_to_count_map:
				if item_code in item_code_to_count_map:
					models_to_count_map[model] += item_code_to_count_map[item_code]
			else:
				models_to_count_map[model] = 0
	
	models_to_count_map = [[x,y] for x,y in models_to_count_map.items() if y!=0]
	return models_to_count_map



def execute(filters=None):
	columns, data = get_columns(), get_data()
	return columns, data
