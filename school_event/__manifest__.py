# -*- coding: utf-8 -*-
# See LICENSE file for full copyright and licensing details.

{
    'name': 'School Event Management',
    'version': "10.0.1.0.3",
    'author': '''Serpent Consulting Services Pvt. Ltd.,
                 Odoo Community Association (OCA)''',
    'website': 'http://www.serpentcs.com',
    'images': ['static/description/SchoolEvent.png'],
    'category': 'School Management',
    'license': "AGPL-3",
    'complexity': 'easy',
    'summary': 'A Module For Event Management In School',
    'depends': ['school'],
    'data': ['security/event_security.xml',
             'security/ir.model.access.csv',
             'views/event_view.xml',
             'views/participants.xml',
             'views/report_view.xml'],
    'demo': ['demo/event_demo.xml'],
    'post_init_hook': 'post_init_hook',
    'installable': True,
    'application': True
}
