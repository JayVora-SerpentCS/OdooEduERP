# -*- coding: utf-8 -*-
# See LICENSE file for full copyright and licensing details.

{
    'name': 'Evaluation Management',
    'version': "11.0.1.0.3",
    'author': '''Serpent Consulting Services Pvt. Ltd.''',
    'website': 'http://www.almisnadtechnology.com',
    'category': 'School Management',
    'license': "AGPL-3",
    'complexity': 'easy',
    'summary': 'A Module For Evaluation Management In School',
    'images': ['static/description/Evaluation1.jpg'],
    'depends': ['hr', 'school'],
    'data': ['security/evaluation_security.xml',
             'views/school_evaluation_view.xml',
             'views/templates.xml',
             'security/ir.model.access.csv'],
    'demo': ['demo/school_evaluation_demo.xml'],
    'installable': True,
    'application': True
}
