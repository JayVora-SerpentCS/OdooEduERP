# -*- coding: utf-8 -*-
# See LICENSE file for full copyright and licensing details.

{
    'name': 'Exam Management',
    'version': "11.0.1.0.15",
    'author': 'Serpent Consulting Services Pvt. Ltd.',
    'website': 'http://www.serpentcs.com',
    'category': 'School Management',
    'license': "AGPL-3",
    'summary': 'A Module For Exams Management Taken In School',
    'complexity': 'easy',
    'images': ['static/description/exam_banner.png'],
    'depends': ['school', 'timetable', 'mail'],
    'data': ['security/exam_security.xml',
             'security/ir.model.access.csv',
             'views/exam_view.xml',
             'views/exam_sequence.xml',
             'views/exam_result_report.xml',
             'views/additional_exam_report.xml',
             'views/result_information_report.xml',
             'views/batch_exam.xml',
             'views/report_view.xml',
             'wizard/subject_result.xml',
             'wizard/batch_result.xml'],
    'demo': ['demo/exam_demo.xml'],
    'installable': True,
    'application': True,
}
