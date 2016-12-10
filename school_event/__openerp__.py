# -*- coding: utf-8 -*-
# Part of Odoo. See LICENSE file for full copyright and licensing details.

{'name': 'School Event Management',
 'version': '9.0.0.1.4',
 'author': '''Serpent Consulting Services PVT. LTD.,
             Odoo Community Association (OCA)''',
 'website': 'http://www.serpentcs.com',
 'category': 'School Management',
 'license': '',
 'complexity': 'easy',
 'summary': 'A Module For Event Management In School',
 'depends': ['school'],
 'data': ['views/event_view.xml',
          'views/event_workflow.xml',
          'security/event_security.xml',
          'security/ir.model.access.csv',
          'views/participants.xml',
          'views/report_view.xml'],
 'demo': ['demo/event_demo.xml'],
 'test': ['test/event.yml',
          'test/event_report.yml'],
 'installable': True,
 'application': True}
