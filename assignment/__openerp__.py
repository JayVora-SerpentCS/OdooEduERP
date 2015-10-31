# -*- coding: utf-8 -*-
# Part of Odoo. See LICENSE file for full copyright and licensing details.

{
    'name': 'Assignment Management',
    'version': '3.0',
    'author': 'Serpent Consulting Services PVT. LTD.',
    'website': 'http://www.serpentcs.com',
    'category': 'School Management',
    'summary': 'A Module For Assignment Management In School',
    'complexity': 'easy',
    'description': '''A module to School Assignment Management.
                      which helps in school management to assign the assignment
                      to the student''',
    'depends': ['school'],
    'data': ['views/homework_view.xml', 'security/ir.model.access.csv'],
    'demo': ['demo/assignment_demo.xml'],
    'test': ['test/assignment.yml'],
    'installable': True,
    'application': True,
}
