# -*- coding: utf-8 -*-
# See LICENSE file for full copyright and licensing details.

{
    'name': 'Exam Management',
    'version': "10.0.1.0.10",
    'author': '''Serpent Consulting Services Pvt. Ltd.,
                 Odoo Community Association (OCA)''',
    'website': 'http://www.serpentcs.com',
    'category': 'School Management',
    'license': "AGPL-3",
    'summary': 'A Module For Exams Management Taken In School',
    'complexity': 'easy',
    'depends': ['timetable'],
    'data': ['security/exam_security.xml',
             'security/ir.model.access.csv',
             'views/exam_view.xml',
             'views/exam_sequence.xml',
             'views/exam_result_report.xml',
             'views/additional_exam_report.xml',
             'views/result_information_report.xml',
             'views/report_view.xml',
             'wizard/subject_result.xml'],
    'demo': ['demo/exam_demo.xml'],
    'installable': True,
    'application': True,
    'test': ['test/exam_test.yml']
}
