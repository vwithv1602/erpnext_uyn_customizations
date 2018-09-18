from __future__ import unicode_literals
import frappe

class FlipkartError(frappe.ValidationError): pass
class FlipkartSetupError(frappe.ValidationError): pass
