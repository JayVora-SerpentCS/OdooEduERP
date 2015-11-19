# -*- coding: utf-8 -*-
# Part of Odoo. See LICENSE file for full copyright and licensing details.

{'name': 'HOSTEL',
 'version': '3.0',
 'author': 'Serpent Consulting Services PVT. LTD.',
 'category': 'School Management',
 'website': 'http://www.serpentcs.com',
 'license': '',
 'complexity': 'easy',
 'summary': 'Module For HOSTEL Management In School',
 'depends': ['school'],
 'demo': ['demo/school_hostel_demo.xml'],
 'data': ['security/hostel_security.xml',
          'security/ir.model.access.csv',
          'views/hostel_view.xml',
          'views/hostel_sequence.xml',
          'views/report_view.xml',
          'views/hostel_fee_receipt.xml'],
 'installable': True,
 'auto_install': False}
