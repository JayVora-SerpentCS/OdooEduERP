# -*- coding: utf-8 -*-
# Part of Odoo. See LICENSE file for full copyright and licensing details.

{'name': 'Timetable Management',
 'version': "10.0.1.0.0",
 'author': "Serpent Consulting Services Pvt. Ltd., Odoo SA,\
    Odoo Community Association (OCA)",
 'website': 'http://www.serpentcs.com',
 'license': "AGPL-3",
 'category': 'School Management',
 'complexity': 'easy',
 'summary': 'A Module For Timetable Management In School',
 'depends': ['school'],
 'data': ['security/ir.model.access.csv',
          'views/timetable_view.xml',
          'views/report_view.xml',
          'views/timetable.xml'],
 'demo': ['demo/timetable_demo.xml'],
 'test': ['test/timetable.yml'],
 'installable': True,
 'application': True}
