# Copyright (c) 2013, vavcoders and contributors
# For license information, please see license.txt

from __future__ import unicode_literals
import frappe
from frappe import msgprint, _

def execute(filters=None):
    if not filters:
        filters = {}
    supplier = filters.get("supplier")
    if not supplier:
        columns, data = [_("ERROR") + ":Data:300"],[["Supplier is mandatory"]]
    else:
        columns, data = get_columns(), get_data(supplier)
    return columns, data

def get_columns():
    """return columns bab on filters"""
    columns = [
        _("PO Number") + ":Link/Purchase Order:90",
        # _("PO Status") + ":Data:70",
        _("PO Amount") + ":Currency:70",
        _("PR Number") + ":Link/Purchase Receipt:90",
        _("PR Amount") + ":Currency:70",
        # _("PR Return Number") + ":Data:70",
        # _("PR Amount") + ":Data:70",
        _("PI Number") + ":Link/Purchase Invoice:90",
        _("PI Amount") + ":Currency:70",
        # _("Paid Amount") + ":Data:70",
        # _("JV") + ":Data:70"
    ]
    return columns
@frappe.whitelist()
def test():
    return get_data('Manvi Technologies')

def get_data(supplier):
    # Get all PRs of a supplier
    uniq_prs = get_uniq_prs(supplier)

    # Get pr data
    data = get_pr_data(uniq_prs,supplier)
    return data
    
    

def get_uniq_prs(supplier):
    pr_data = []
    # PR associated with PO
    sql = """ select distinct pri.purchase_order,pr.name as prec_name,pr.supplier,pr.status as pr_status from `tabPurchase Receipt` pr inner join `tabPurchase Receipt Item` pri on pri.parent=pr.name where pr.supplier='Manvi Technologies' and pr.docstatus=1 and pr.is_return<>1 and pr.status not in ('Draft') """
    for rec in frappe.db.sql(sql,as_dict=1):
        pr_data.append(rec.get("prec_name"))
    # PR associated with PI 
    sql = """ select distinct pri.purchase_order,pii.parent as pi_name,pri.parent as prec_name from `tabPurchase Receipt Item` pri inner join `tabPurchase Invoice Item` pii on pii.purchase_receipt=pri.parent inner join `tabPurchase Receipt` pr on pr.name=pri.parent where pri.docstatus=1 and pr.is_return<>1 and pr.status not in ('Draft') """
    for rec in frappe.db.sql(sql,as_dict=1):
        pr_data.append(rec.get("prec_name"))
    uniq_prs = set(pr_data) 
    return uniq_prs


def get_pr_data(uniq_prs,supplier):
    pr_data = []
    comma_sep_pr_condition = ','.join("'{0}'".format(pr) for pr in list(uniq_prs))
    sql = """ select distinct pr.name as pr_name,pri.purchase_order as po_name,sum(poi.net_amount) as po_amount,pii.parent as pi_name,sum(pri.net_amount) as pr_amount,sum(pii.net_amount) as pi_amount from `tabPurchase Receipt` pr right join `tabPurchase Receipt Item` pri on pri.parent=pr.name inner join `tabPurchase Order Item` poi on poi.parent=pri.purchase_order left join `tabPurchase Invoice Item` pii on pii.purchase_receipt=pr.name where pr.name in ({0}) and pr.supplier='{1}' group by poi.name,pri.name """.format(comma_sep_pr_condition,supplier)
    for rec in frappe.db.sql(sql,as_dict=1):
        pr_data.append([rec.get("po_name"),rec.get("po_amount"),rec.get("pr_name"),rec.get("pr_amount"),rec.get("pi_name"),rec.get("pi_amount")])
    return pr_data

