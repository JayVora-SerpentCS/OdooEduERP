# -*- coding: utf-8 -*-
# Part of Odoo. See LICENSE file for full copyright and licensing details.

{'name': 'Attendance Management',
 'version': '9.0.0.3.0',
 'author': '''Serpent Consulting Services PVT. LTD.,
             Odoo Community Association (OCA)''',
 'website': 'http://www.serpentcs.com',
 'category': 'School Management',
 'license': '',
 'summary': 'A Module For Attendance Management In School',
 'complexity': 'easy',
 'depends': ['school', 'hr'],
 'data': ['security/ir.model.access.csv',
          'views/school_attendance_view.xml',
          'views/attendance_workflow.xml',
          'wizard/attendance_sheet_wizard_view.xml',
          'wizard/student_attendance_by_month_view.xml'],
 'demo': ['demo/school_attendance_demo.xml'],
 'test': ['test/school_attendance_test.yml',
          'test/attendance_by_month_student_report_test.yml',
          'test/monthly_attendance_sheet_wizard_test.yml',
          'test/daily_attendance_current_test.yml',
          'test/student_attendance_by_month_wizard_test.yml'
          ],
 'installable': True,
 'application': True}
