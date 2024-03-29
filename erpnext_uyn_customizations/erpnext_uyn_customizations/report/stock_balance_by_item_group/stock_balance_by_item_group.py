# Copyright (c) 2015, Frappe Technologies Pvt. Ltd. and Contributors
# License: GNU General Public License v3. See license.txt

from __future__ import unicode_literals
import frappe
from frappe import _
from frappe.utils import flt, cint, getdate, now
from erpnext.stock.report.stock_ledger.stock_ledger import get_item_group_condition
from erpnext_ebay.vlog import vwrite

@frappe.whitelist(allow_guest=True)
def test_get_stock_balance():
	company='Usedyetnew'
	item='Lenovo L430/T430 Battery-GRADE A'
	warehouse='Stores - Uyn'
	return get_stock_balance(company,item,warehouse)
@frappe.whitelist()
def get_stock_balance(company,item,warehouse):
	from datetime import timedelta,datetime
	today = datetime.strptime(datetime.today().strftime('%Y-%m-%d'), '%Y-%m-%d')
	last_month = today - timedelta(30)
	if not item:
		filters = {"from_date":str(last_month)[:10],"to_date":str(today)[:10]}
	else:
		filters = {"from_date":str(last_month)[:10],"to_date":str(today)[:10],"item_code":item}
	items = get_items(filters)
	sle = get_stock_ledger_entries(filters, items)
	iwb_map = get_item_warehouse_map(filters, sle)
	try:
		if not item:
			data = []
			for (company, item, warehouse) in sorted(iwb_map):
				qty_dict = iwb_map[(company, item, warehouse)]
				data.append({"item_code":item,"bal_qty":qty_dict.get("bal_qty")})
			result = data
		else:
			bal_qty = iwb_map[(company, item, warehouse)].get("bal_qty")
			result = bal_qty
	except Exception:
		result = 0
	return result
	#return "%s%s" %(today,filters)

@frappe.whitelist(allow_guest=True)
def execute(filters=None):
	if not filters: filters = {}

	validate_filters(filters)

	columns = get_columns()
	items = get_items(filters)
	sle = get_stock_ledger_entries(filters, items)
	iwb_map = get_item_warehouse_map(filters, sle)
	item_map = get_item_details(items, sle, filters)
	item_reorder_detail_map = get_item_reorder_details(item_map.keys())

	data = []
	for (company, item, warehouse) in sorted(iwb_map):
		qty_dict = iwb_map[(company, item, warehouse)]
		item_reorder_level = 0
		item_reorder_qty = 0
		if item + warehouse in item_reorder_detail_map:
			item_reorder_level = item_reorder_detail_map[item + warehouse]["warehouse_reorder_level"]
			item_reorder_qty = item_reorder_detail_map[item + warehouse]["warehouse_reorder_qty"]

		report_data = [item, item_map[item]["item_name"],
			item_map[item]["item_group"],
			item_map[item]["brand"],
			item_map[item]["description"], warehouse,
			qty_dict.bal_qty, qty_dict.val_rate, qty_dict.bal_val,
			item_map[item]["stock_uom"], qty_dict.opening_qty,
			qty_dict.opening_val, qty_dict.in_qty,
			qty_dict.in_val, qty_dict.out_qty,
			qty_dict.out_val,
			item_reorder_level,
			item_reorder_qty,
			company
		]

		if filters.get('show_variant_attributes', 0) == 1:
			variants_attributes = get_variants_attributes()
			report_data += [item_map[item].get(i) for i in variants_attributes]

		data.append(report_data)
	
	item_group_mapping = {}
	for row in data:
		if row[2] in item_group_mapping:
			item_group_mapping[row[2]]['total_qty'] += row[6]
			item_group_mapping[row[2]]['total_value'] += row[8]
		else:
			item_group_mapping[row[2]] = {}
			item_group_mapping[row[2]]['total_qty'] = row[6]
			item_group_mapping[row[2]]['total_value'] = row[8]
		

	data = []
	for key in item_group_mapping:
		row = [
			key,
			item_group_mapping[key]['total_qty'],
			item_group_mapping[key]['total_value']
		]
		data.append(row)
	if filters.get('show_variant_attributes', 0) == 1:
		columns += ["{}:Data:100".format(i) for i in get_variants_attributes()]

	return columns, data

def get_columns():
	"""return columns"""

	columns = [
		_("Item Group")+":Link/Item Group:100",
		_("Balance Qty")+":Float:100",
		_("Balance Value")+":Float:100"
	]

	return columns

def get_conditions(filters):
	conditions = ""
	if not filters.get("from_date"):
		frappe.throw(_("'From Date' is required"))

	if filters.get("to_date"):
		conditions += " and sle.posting_date <= '%s'" % frappe.db.escape(filters.get("to_date"))
	else:
		frappe.throw(_("'To Date' is required"))

	if filters.get("warehouse"):
		warehouse_details = frappe.db.get_value("Warehouse",
			filters.get("warehouse"), ["lft", "rgt"], as_dict=1)
		if warehouse_details:
			conditions += " and exists (select name from `tabWarehouse` wh \
				where wh.lft >= %s and wh.rgt <= %s and sle.warehouse = wh.name)"%(warehouse_details.lft,
				warehouse_details.rgt)

	return conditions

def get_stock_ledger_entries(filters, items):
	item_conditions_sql = ''
	if items:
		item_conditions_sql = ' and sle.item_code in ({})'\
			.format(', '.join(['"' + frappe.db.escape(i, percent=False) + '"' for i in items]))

	conditions = get_conditions(filters)

	return frappe.db.sql("""
		select
			sle.item_code, warehouse, sle.posting_date, sle.actual_qty, sle.valuation_rate,
			sle.company, sle.voucher_type, sle.qty_after_transaction, sle.stock_value_difference
		from
			`tabStock Ledger Entry` sle force index (posting_sort_index)
		where sle.docstatus < 2 %s %s
		order by sle.posting_date, sle.posting_time, sle.name""" %
		(item_conditions_sql, conditions), as_dict=1)

def get_item_warehouse_map(filters, sle):
	iwb_map = {}
	from_date = getdate(filters.get("from_date"))
	to_date = getdate(filters.get("to_date"))

	for d in sle:
		key = (d.company, d.item_code, d.warehouse)
		if key not in iwb_map:
			iwb_map[key] = frappe._dict({
				"opening_qty": 0.0, "opening_val": 0.0,
				"in_qty": 0.0, "in_val": 0.0,
				"out_qty": 0.0, "out_val": 0.0,
				"bal_qty": 0.0, "bal_val": 0.0,
				"val_rate": 0.0
			})

		qty_dict = iwb_map[(d.company, d.item_code, d.warehouse)]

		if d.voucher_type == "Stock Reconciliation":
			qty_diff = flt(d.qty_after_transaction) - qty_dict.bal_qty
		else:
			qty_diff = flt(d.actual_qty)

		value_diff = flt(d.stock_value_difference)

		if d.posting_date < from_date:
			qty_dict.opening_qty += qty_diff
			qty_dict.opening_val += value_diff

		elif d.posting_date >= from_date and d.posting_date <= to_date:
			if qty_diff > 0:
				qty_dict.in_qty += qty_diff
				qty_dict.in_val += value_diff
			else:
				qty_dict.out_qty += abs(qty_diff)
				qty_dict.out_val += abs(value_diff)

		qty_dict.val_rate = d.valuation_rate
		qty_dict.bal_qty += qty_diff
		qty_dict.bal_val += value_diff
		
	iwb_map = filter_items_with_no_transactions(iwb_map)

	return iwb_map
	
def filter_items_with_no_transactions(iwb_map):
	for (company, item, warehouse) in sorted(iwb_map):
		qty_dict = iwb_map[(company, item, warehouse)]
		
		no_transactions = True
		float_precision = cint(frappe.db.get_default("float_precision")) or 3
		for key, val in qty_dict.items():
			val = flt(val, float_precision)
			qty_dict[key] = val
			if key != "val_rate" and val:
				no_transactions = False
		
		if no_transactions:
			iwb_map.pop((company, item, warehouse))

	return iwb_map

def get_items(filters):
	conditions = []
	if filters.get("item_code"):
		conditions.append("item.name=%(item_code)s")
	else:
		if filters.get("brand"):
			conditions.append("item.brand=%(brand)s")
		if filters.get("item_group"):
			conditions.append(get_item_group_condition(filters.get("item_group")))

	items = []
	if conditions:
		items = frappe.db.sql_list("""select name from `tabItem` item where {}"""
			.format(" and ".join(conditions)), filters)
	return items

def get_item_details(items, sle, filters):
	item_details = {}
	if not items:
		items = list(set([d.item_code for d in sle]))
		
	if items:
		for item in frappe.db.sql("""
			select name, item_name, description, item_group, brand, stock_uom
			from `tabItem`
			where name in ({0})
			""".format(', '.join(['"' + frappe.db.escape(i, percent=False) + '"' for i in items])), as_dict=1):
				item_details.setdefault(item.name, item)

	if filters.get('show_variant_attributes', 0) == 1:
		variant_values = get_variant_values_for(item_details.keys())
		item_details = {k: v.update(variant_values.get(k, {})) for k, v in item_details.iteritems()}

	return item_details

def get_item_reorder_details(items):
	item_reorder_details = frappe._dict()

	if items:
		item_reorder_details = frappe.db.sql("""
			select parent, warehouse, warehouse_reorder_qty, warehouse_reorder_level
			from `tabItem Reorder`
			where parent in ({0})
		""".format(', '.join(['"' + frappe.db.escape(i, percent=False) + '"' for i in items])), as_dict=1)

	return dict((d.parent + d.warehouse, d) for d in item_reorder_details)

def validate_filters(filters):
	if not (filters.get("item_code") or filters.get("warehouse")):
		sle_count = flt(frappe.db.sql("""select count(name) from `tabStock Ledger Entry`""")[0][0])
		if sle_count > 500000:
			frappe.throw(_("Please set filter based on Item or Warehouse"))

def get_variants_attributes():
	'''Return all item variant attributes.'''
	return [i.name for i in frappe.get_all('Item Attribute')]

def get_variant_values_for(items):
	'''Returns variant values for items.'''
	attribute_map = {}
	for attr in frappe.db.sql('''select parent, attribute, attribute_value
		from `tabItem Variant Attribute` where parent in (%s)
		''' % ", ".join(["%s"] * len(items)), tuple(items), as_dict=1):
			attribute_map.setdefault(attr['parent'], {})
			attribute_map[attr['parent']].update({attr['attribute']: attr['attribute_value']})

	return attribute_map
