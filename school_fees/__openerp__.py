# -*- coding: utf-8 -*-
# Part of Odoo. See LICENSE file for full copyright and licensing details.

{'name': 'Fees Management',
 'version': '2.2',
 'author': 'Serpent Consulting Services PVT. LTD.',
 'website': 'http://www.serpentcs.com',
 'category': 'School Management',
 'license': '',
 'complexity': 'easy',
 'summary': 'A Module For Fees Management In School',
 'depends': ['school', 'account_voucher'],
 'demo': ['demo/school_fees_demo.xml'],
 'data': ['security/ir.model.access.csv',
          'views/school_fees_view.xml',
          'views/school_fees_sequence.xml',
          'views/student_fees_register_workflow.xml',
#          'views/student_payslip_workflow.xml',
          'views/student_payslip.xml',
          'views/student_fees_register.xml',
          'views/report_view.xml'],
 'installable': True,
 'application': True}
