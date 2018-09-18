from frappe import _

def get_data():
	return {
		'fieldname': 'tech_repack',
		'non_standard_fieldnames': {
			'Stock Entry': 'reference_tech_repack_no',
		},
		'internal_links': {
		},
		'transactions': [
			{
				'label': _('Reference'),
				'items': ['Stock Entry']
			}
		]
	}
