# -*- coding: utf-8 -*-
# See LICENSE file for full copyright and licensing details.

{'name': 'HOSTEL',
 'version': "10.0.1.0.0",
 'author': "Serpent Consulting Services Pvt. Ltd., Odoo SA",
 'category': 'School Management',
 'website': 'http://www.serpentcs.com',
 'license': "AGPL-3",
 'complexity': 'easy',
 'summary': 'Module For HOSTEL Management In School',
 'depends': ['school'],
 'data': ['security/hostel_security.xml',
          'security/ir.model.access.csv',
          'views/hostel_view.xml',
          'views/hostel_sequence.xml',
          'views/report_view.xml',
          'views/hostel_fee_receipt.xml'],
 'installable': True,
 'auto_install': False}
