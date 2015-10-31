# -*- coding: utf-8 -*-
# Part of Odoo. See LICENSE file for full copyright and licensing details.

{
    'name': 'Attendance Management',
    'version': '3.0',
    'author': 'Serpent Consulting Services PVT. LTD.',
    'website': 'http://www.serpentcs.com',
    'category': 'School Management',
    'summary': 'A Module For Attendance Management In School',
    'complexity': 'easy',
    'description': '''A module to Student Attendance System.
        A Module support the following functionalities:
            1. Class-wise Daily Attendance Sheet.
            2. Class-wise Monthly Attendance Sheet.''',
    'depends': ['school', 'hr'],
    'data': [
        'security/ir.model.access.csv',
        'views/school_attendance_view.xml',
        'views/attendance_workflow.xml',
        'wizard/attendance_sheet_wizard_view.xml',
        'wizard/student_attendance_by_month_view.xml',
#         'data/daily_attendance_data.xml',
    ],
    'demo': ['demo/school_attendance_demo.xml'],
    'installable': True,
    'application': True,
}
