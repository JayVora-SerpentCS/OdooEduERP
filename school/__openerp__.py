# -*- coding: utf-8 -*-
# Part of Odoo. See LICENSE file for full copyright and licensing details.

{
    'name': 'School',
    'version': '3.0',
    'author': 'Serpent Consulting Services PVT. LTD.',
    'website': 'http://www.serpentcs.com',
    'category': 'School Management',
    'complexity': 'easy',
    'Summary': 'A Module For School Management',
    'description': '''A module to School Management.
        A Module support the following functionalities:
        1. Admission Procedure
        2. Student Information
        3. Parent Information
        4. Teacher Information
        5. School Information
        6. Standard, Medium and Division Information
        7. Subject Information
                    ''',
    'depends': ['hr', 'mail', 'crm', 'report', 'board'],
    'data': [
            'wizard/wiz_send_email_view.xml',
            'security/school_security.xml',
            'views/school_view.xml',
            'security/ir.model.access.csv',
            'views/admission_workflow.xml',
            'data/student_sequence.xml',
            'wizard/assign_roll_no_wizard.xml',
            'wizard/move_standards_view.xml',
            'wizard/wiz_meeting_view.xml',
            'views/report_view.xml',
            'views/identity_card.xml',
    ],
    'demo': ['demo/school_demo.xml'],
    'test': [
            'test/school_test.yml',
            'test/assign_roll_no_test.yml',
        ],
    'installable': True,
    'application': True,
}
