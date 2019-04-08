# -*- coding: utf-8 -*-
from __future__ import unicode_literals
from . import __version__ as app_version

app_name = "erpnext_uyn_customizations"
app_title = "Erpnext Uyn Customizations"
app_publisher = "vavcoders"
app_description = "UYN Customizations on ERPNEXT"
app_icon = "octicon octicon-file-directory"
app_color = "#34ace0"
app_email = "vwithv1602@gmail.com"
app_license = "license.txt"

# Includes in <head>
# ------------------

# include js, css files in header of desk.html
# app_include_css = "/assets/erpnext_uyn_customizations/css/erpnext_uyn_customizations.css"
# app_include_js = "/assets/erpnext_uyn_customizations/js/erpnext_uyn_customizations.js"

# include js, css files in header of web template
# web_include_css = "/assets/erpnext_uyn_customizations/css/erpnext_uyn_customizations.css"
# web_include_js = "/assets/erpnext_uyn_customizations/js/erpnext_uyn_customizations.js"

# include js in page
# page_js = {"page" : "public/js/file.js"}

# include js in doctype views
# doctype_js = {"doctype" : "public/js/doctype.js"}
# doctype_list_js = {"doctype" : "public/js/doctype_list.js"}
# doctype_tree_js = {"doctype" : "public/js/doctype_tree.js"}
# doctype_calendar_js = {"doctype" : "public/js/doctype_calendar.js"}

# Home Pages
# ----------

# application home page (will override Website Settings)
# home_page = "login"

# website user home page (by Role)
# role_home_page = {
#	"Role": "home_page"
# }

# Website user home page (by function)
# get_website_user_home_page = "erpnext_uyn_customizations.utils.get_home_page"

# Generators
# ----------

# automatically create page for each record of this doctype
# website_generators = ["Web Page"]

# Installation
# ------------

# before_install = "erpnext_uyn_customizations.install.before_install"
# after_install = "erpnext_uyn_customizations.install.after_install"

# Desk Notifications
# ------------------
# See frappe.core.notifications.get_notification_config

# notification_config = "erpnext_uyn_customizations.notifications.get_notification_config"

# Permissions
# -----------
# Permissions evaluated in scripted ways

# permission_query_conditions = {
# 	"Event": "frappe.desk.doctype.event.event.get_permission_query_conditions",
# }
#
# has_permission = {
# 	"Event": "frappe.desk.doctype.event.event.has_permission",
# }

# Document Events
# ---------------
# Hook on document methods and events

# doc_events = {
# 	"*": {
# 		"on_update": "method",
# 		"on_cancel": "method",
# 		"on_trash": "method"
#	}
# }

# Scheduled Tasks
# ---------------

scheduler_events = {
    "all": [
		"erpnext_uyn_customizations.flipkart_api.sync_flipkart"
	]
}
# scheduler_events = {
# 	"all": [
# 		"erpnext_uyn_customizations.tasks.all"
# 	],
# 	"daily": [
# 		"erpnext_uyn_customizations.tasks.daily"
# 	],
# 	"hourly": [
# 		"erpnext_uyn_customizations.tasks.hourly"
# 	],
# 	"weekly": [
# 		"erpnext_uyn_customizations.tasks.weekly"
# 	]
# 	"monthly": [
# 		"erpnext_uyn_customizations.tasks.monthly"
# 	]
# }

# Testing
# -------

# before_tests = "erpnext_uyn_customizations.install.before_tests"

# Overriding Whitelisted Methods
# ------------------------------
#
# override_whitelisted_methods = {
# 	"frappe.desk.doctype.event.event.get_events": "erpnext_uyn_customizations.event.get_events"
# }

