# -*- coding: utf-8 -*-
# Part of Odoo. See LICENSE file for full copyright and licensing details.

{
    'name': 'Evaluation Management',
    'version': '2.0',
    'author': 'Serpent Consulting Services PVT. LTD.',
    'website': 'http://www.almisnadtechnology.com',
    'category': 'School Management',
    'license': '',
    'complexity': 'easy',
    'summary': 'A Module For Evaluation Management In School',
    'depends': ['hr', 'school'],
    'data': ['views/student_evaluation_view.xml',
             'security/ir.model.access.csv'],
    'demo': ['demo/student_evaluation_demo.xml'],
    'installable': True,
    'application': True,
}
