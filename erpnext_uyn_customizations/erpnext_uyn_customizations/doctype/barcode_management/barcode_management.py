# -*- coding: utf-8 -*-
# Copyright (c) 2018, vavcoders and contributors
# For license information, please see license.txt

from __future__ import unicode_literals
import frappe
from frappe.model.document import Document
from erpnext_ebay.vlog import vwrite
from frappe.utils.file_manager import download_file
import datetime,time
import string,random
class BarcodeManagement(Document):
	pass

def id_generator(size=7, chars=string.ascii_uppercase + string.digits):
	return ''.join(random.choice(chars) for _ in range(size))
def validate_new_barcodes(barcodes,result):
	barcode_list = ','.join("'{0}'".format(b) for b in barcodes)
	check_if_exists_sql = """ select GROUP_CONCAT(name SEPARATOR ',') as names from `tabSerial No` where name in ({0}) """.format(barcode_list)
	check_if_exists_res = frappe.db.sql(check_if_exists_sql,as_dict=1)
	existing_barcodes = check_if_exists_res[0].get("names")
	if existing_barcodes:
		existing_barcodes = existing_barcodes.split(',')
	else:
		existing_barcodes = []
	new_barcodes = []
	for i in range(len(existing_barcodes)):
		seq = id_generator()
		seq = "%s%s" %("UYN",seq)
		new_barcodes.append(seq)
	if len(new_barcodes):
		result = [x for x in barcodes if x not in existing_barcodes]
		result = result + new_barcodes
		new_barcodes = []
		return validate_new_barcodes(result,result)
	else:
		return barcodes

@frappe.whitelist()
def get_new_barcodes(qty):
	new_barcodes = ""
	barcodes = []
	for i in range(int(qty)):
		seq = id_generator()
		seq = "%s%s" %("UYN",seq)
		barcodes.append(seq)
		new_barcodes += "UYN%s\n" %(seq)
	new_set = validate_new_barcodes(barcodes,barcodes)
	return "\n".join(new_set)
@frappe.whitelist()
def generate_barcodes(barcodes,file_name):
    from reportlab.graphics.barcode import code39, code128, code93
    from reportlab.graphics.barcode import eanbc, qr, usps
    from reportlab.graphics.shapes import Drawing 
    from reportlab.lib.pagesizes import letter,A6
    from reportlab.lib.units import mm
    from reportlab.pdfgen import canvas
    from reportlab.graphics import renderPDF
    from reportlab.pdfbase import pdfmetrics
    from reportlab.pdfbase.pdfmetrics import registerFontFamily,stringWidth
    from reportlab.pdfbase.ttfonts import TTFont
    
    #----------------------------------------------------------------------
    def createBarCodes(barcodes):
		A4 = A6
		# Registered font family
		pdfmetrics.registerFont(TTFont('Vera', 'Vera.ttf'))
		pdfmetrics.registerFont(TTFont('VeraBd', 'VeraBd.ttf'))
		pdfmetrics.registerFont(TTFont('VeraIt', 'VeraIt.ttf'))
		pdfmetrics.registerFont(TTFont('VeraBI', 'VeraBI.ttf'))
		pdfmetrics.registerFont(TTFont('freemono', 'FreeMono.ttf'))
		# Registered fontfamily
		registerFontFamily('Vera',normal='Vera',bold='VeraBd',italic='VeraIt',boldItalic='VeraBI')

		"""
		Create barcode examples and embed in a PDF
		"""
		c = canvas.Canvas("site1.local/public/files/barcodes_%s.pdf" % file_name, pagesize=A4)
		i = 0
		for barcode_value in barcodes:
			text_width = stringWidth(barcode_value,'freemono', 4)
			i = i + 25
			barcode128 = code128.Code128(barcode_value,barHeight=3*mm,barWidth = .4)
			codes = [ barcode128]
			x = 1 * mm
			y = 285 * mm
			x1 = 6.4 * mm
			x = A4[0]/2
			for code in codes:
				# draw the eanbc13 code
				# barcode_eanbc13 = eanbc.Ean13BarcodeWidget(barcode_value)
				# bounds = barcode_eanbc13.getBounds()
				# width = bounds[2] - bounds[0]
				# height = bounds[3] - bounds[1]
				d = Drawing(50, 10)
				# d.add(code.drawOn(c,x,835-i))
				d.add(code.drawOn(c,(A4[0]/2)-40,A4[1]-i))
				c.setFont('freemono', 4)
				# c.drawString(x+40,y-i+24,barcode_value)
				
				# c.drawString((A4[0]-text_width)/2,A4[1]-i-4,barcode_value)
				c.drawString((A4[0]/2)-20,A4[1]-i-4,barcode_value)
				if (i%400==0):
					i = 0
					c.showPage()
				renderPDF.draw(d, c, 15, 465)
				# code.drawOn(c, x , y)
				# y = y - 15 * mm
		c.save()
		file_url = "/files/barcodes_%s.pdf" % file_name
		return file_url
		
    
    # if __name__ == "__main__":
    barcodes = [s.strip() for s in barcodes.splitlines()]
    return createBarCodes(barcodes)
	
	
# Barcode generation for Purchase Receipt
