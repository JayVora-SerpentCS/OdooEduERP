# -*- encoding: UTF-8 -*-
# -----------------------------------------------------------------------------
#
#    OpenERP, Open Source Management Solution
#    Copyright (C) 2012-Today Serpent Consulting Services PVT. LTD.
#    (<http://www.serpentcs.com>)
#
#    This program is free software: you can redistribute it and/or modify
#    it under the terms of the GNU General Public License as published by
#    the Free Software Foundation, either version 3 of the License, or
#    (at your option) any later version.
#
#    This program is distributed in the hope that it will be useful,
#    but WITHOUT ANY WARRANTY; without even the implied warranty of
#    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#    GNU General Public License for more details.
#
#    You should have received a copy of the GNU General Public License
#    along with this program.  If not, see <http://www.gnu.org/licenses/>
#
# -----------------------------------------------------------------------------

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
