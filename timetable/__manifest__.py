# -*- coding: utf-8 -*-
# See LICENSE file for full copyright and licensing details.
{
    'name': 'Timetable Management',
    'version': '10.0.1.0.4',
    'author': '''Serpent Consulting Services Pvt. Ltd.''',
    'website': 'http://www.serpentcs.com',
    'images': ['static/description/SchoolTimetable.png'],
    'license': "AGPL-3",
    'category': 'School Management',
    'complexity': 'easy',
    'summary': 'A Module For Timetable Management In School',
    'depends': ['school'],
    'data': ['security/timetable_security.xml',
             'security/ir.model.access.csv',
             'views/timetable_view.xml',
             'views/report_view.xml',
             'views/timetable.xml'],
    'demo': ['demo/timetable_demo.xml'],
    'installable': True,
    'application': True
}
