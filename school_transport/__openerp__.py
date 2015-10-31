# -*- coding: utf-8 -*-
# Part of Odoo. See LICENSE file for full copyright and licensing details.

{
    'name': 'Transport Management',
    'version': '3.0',
    'author': 'Serpent Consulting Services PVT. LTD.',
    'website': 'http://www.serpentcs.com',
    'category': 'School Management',
    'complexity': 'easy',
    'summary': 'A Module For Transport & Vehicle Management In School',
    'description': '''A module to School Transport Management.
    A Module support the following functionalities:

    1. We can define the Transport Root and Points with vehicles.
    2. Student can Register for any root with selected point for\
       specific month.
    3. Vehicle information.
    4. Driver information.
    ''',
    'depends': ['hr', 'school'],
    'demo': ['demo/transport_demo.xml'],
    'data': [
        'security/ir.model.access.csv',
        'views/transport_view.xml',
        'views/report_view.xml',
        'views/vehicle.xml',
        'views/participants.xml',
        'wizard/transfer_vehicle.xml',
    ],
    'test': [
        'test/transport.yml',
        'test/transport_report.yml',
    ],
    'installable': True,
    'application': True,
}
