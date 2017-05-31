# -*- coding: utf-8 -*-
# Part of Odoo. See LICENSE file for full copyright and licensing details.

{'name': 'Assignment Management',
 'version': '9.0.0.1.4',
 'author': '''Serpent Consulting Services PVT. LTD.,
             Odoo Community Association (OCA)''',
 'website': 'http://www.serpentcs.com',
 'images': ['static/description/Assignment_Management.png'],
 'license': '',
 'category': 'School Management',
 'summary': 'A Module For Assignment Management In School',
 'complexity': 'easy',
 'depends': ['school'],
 'data': ['views/homework_view.xml', 'security/ir.model.access.csv'],
 'demo': ['demo/assignment_demo.xml'],
 'test': ['test/assignment.yml'],
 'installable': True,
 'application': True}
