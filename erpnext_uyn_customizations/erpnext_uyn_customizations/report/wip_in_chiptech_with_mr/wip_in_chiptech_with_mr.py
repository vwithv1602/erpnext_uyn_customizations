# Copyright (c) 2013, vavcoders and contributors
# For license information, please see license.txt

from __future__ import unicode_literals
import frappe
from frappe import msgprint, _

def execute(filters=None):
	columns, data = get_columns(), get_data()
	return columns, data

def get_columns():
	columns = [
		_("ID") + ":Data:120",
		_("Item Code") + ":Data:450",
		_("Warehouse") + ":Data:120",
		_("Creation Date") + ":Date:80",
		_("Material Request") + ":Link/Material Request:120",
	]
	return columns

def get_data():
	sql = """ (select name as name,item_code as item_code,warehouse as warehouse,purchase_date as purchase_date,"" as material_request from `tabSerial No` where warehouse = 'Chip Tech - Uyn' and item_group='Laptops' and purchase_date>'2018-07-31' and name not in (select sn.name as name from `tabSerial No` sn inner join `tabMaterial Request Item` mri on mri.serial_no=sn.name inner join `tabMaterial Request` mr on mr.name=mri.parent where sn.warehouse = 'Chip Tech - Uyn' and sn.item_group='Laptops' and sn.purchase_date>'2018-07-31' and mr.docstatus=1 and mr.status='Pending'))
	union
	(select sn.name as name,sn.item_code as item_code,sn.warehouse as warehouse,sn.purchase_date as purchase_date,mr.name as material_request from `tabSerial No` sn inner join `tabMaterial Request Item` mri on mri.serial_no=sn.name inner join `tabMaterial Request` mr on mr.name=mri.parent where sn.warehouse = 'Chip Tech - Uyn' and sn.item_group='Laptops' and sn.purchase_date>'2018-07-31' and mr.docstatus=1 and mr.status='Pending') """
	res = frappe.db.sql(sql,as_dict=1)
	data = []
	for r in res:
		data.append([r.get("name"),r.get("item_code"),r.get("warehouse"),str(r.get("purchase_date")),r.get("material_request")])
	return data

