# -*- coding: utf-8 -*-
# Part of Odoo. See LICENSE file for full copyright and licensing details.

{
    'name': 'School Event Management',
    'version': '3.0',
    'author': 'Serpent Consulting Services PVT. LTD.',
    'website': 'http://www.serpentcs.com',
    'category': 'School Management',
    'complexity': 'easy',
    'summary': 'A Module For Event Management In School',
    'description': '''A module to Event Management in School.
    A Module support the following functionalities:
    1. In This Module we can define the Event for specific class
    so the students of particular class can only participate in that event.
    2. student can do Registration for events.
    ''',
    'depends': ['school'],
    'data': [
             'views/event_view.xml',
             'views/event_workflow.xml',
             'security/event_security.xml',
             'security/ir.model.access.csv',
             'views/participants.xml',
             'views/report_view.xml',
            ],
    'demo': ['demo/event_demo.xml'],
    'installable': True,
    'application': True,
}
