# -*- coding: utf-8 -*-
# Part of Odoo. See LICENSE file for full copyright and licensing details.

{
    'name': 'Evaluation Management',
    'version': '2.0',
    'author': 'Serpent Consulting Services PVT. LTD.',
    'website': 'http://www.almisnadtechnology.com',
    'category': 'School Management',
    'complexity': 'easy',
    'summary': 'A Module For Evaluation Management In School',
    'description': ''''A module to Student Evaluation.
    A Module support the following functionalities:

    1. In This Module we can define the terms which we want to consider\
       In Evaluation.
    2. student and Faculty Both can Evaluate This.
    ''',
    'depends': ['hr', 'school'],
    'data': ['views/student_evaluation_view.xml',
             'security/ir.model.access.csv',
     ],
    'demo': [
             'demo/student_evaluation_demo.xml'
             ],
    'installable': True,
    'application': True,
}
