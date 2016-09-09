# -*- coding: utf-8 -*-
# Part of Odoo. See LICENSE file for full copyright and licensing details.

{'name': 'Evaluation Management',
 'version': '9.0.0.1.4',
 'author': '''Serpent Consulting Services PVT. LTD.,
             Odoo Community Association (OCA)''',
 'website': 'http://www.almisnadtechnology.com',
 'category': 'School Management',
 'license': '',
 'complexity': 'easy',
 'summary': 'A Module For Evaluation Management In School',
 'depends': ['hr', 'school'],
 'data': ['security/ir.model.access.csv',
          'security/evaluation_security.xml',
          'views/student_evaluation_view.xml'],
 'demo': ['demo/student_evaluation_demo.xml'],
 'installable': True,
 'application': True}
