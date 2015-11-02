# -*- coding: utf-8 -*-
# Part of Odoo. See LICENSE file for full copyright and licensing details.

{
    'name': 'Exam Management',
    'version': '2.0',
    'author': 'Serpent Consulting Services PVT. LTD.',
    'website': 'http://www.serpentcs.com',
    'category': 'School Management',
    'summary': 'A Module For Exams Management Taken In School',
    'complexity': 'easy',
    'description': '''A module to manage the school examination:
        1. Define Exam Timetable
        2. Conduct Exams
        3. Generate Results
    ''',
    'depends': ['timetable'],
    'data': [
             'security/ir.model.access.csv',
             'views/exam_view.xml',
             'views/exam_sequence.xml',
             'views/exam_result_report.xml',
             'views/additional_exam_report.xml',
             'views/result_information_report.xml',
             'views/report_view.xml',
             'wizard/exam_class_result.xml',
             'wizard/exam_create_result_view.xml',
             'wizard/subject_result.xml',
            ],
    'installable': True,
    'application': True,
    'demo': ['demo/exam_demo.xml'],
    'test': ['test/exam_test.yml'],
}
