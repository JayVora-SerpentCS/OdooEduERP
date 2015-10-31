# -*- coding: utf-8 -*-
# Part of Odoo. See LICENSE file for full copyright and licensing details.

{
    'name': 'School BarCode',
    'version': '3.0',
    'author': 'Serpent Consulting Services PVT. LTD.',
    'category': 'School Management',
    'summary': 'A Module For BarCode System For School',
    'depends': ['timetable'],
    'description': '''Print results with BarCode.''',
    'data': [
        'views/result_report.xml',
        'views/result_label.xml',
        'views/result_lable_info.xml',
    ],
    'installable': True,
}
