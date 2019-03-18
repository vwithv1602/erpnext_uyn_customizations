# Copyright (c) 2013, vavcoders and contributors
# For license information, please see license.txt

from __future__ import unicode_literals
import frappe
from frappe import msgprint, _
def execute(filters=None):
	columns, data = [ _("Employee") + ":Data:250"], [["Testing Employee"]]
	return columns, data
