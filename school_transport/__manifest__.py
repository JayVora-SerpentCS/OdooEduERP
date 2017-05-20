# -*- coding: utf-8 -*-
# See LICENSE file for full copyright and licensing details.

{
    'name': 'Transport Management',
    'version': "10.0.1.0.4",
    'author': '''Serpent Consulting Services Pvt. Ltd.''',
    'website': 'http://www.serpentcs.com',
    'license': "AGPL-3",
    'category': 'School Management',
    'complexity': 'easy',
    'summary': 'A Module For Transport & Vehicle Management In School',
    'depends': ['hr', 'school', 'account_accountant'],
    'data': ['security/transport_security.xml',
             'security/ir.model.access.csv',
             'views/transport_view.xml',
             'views/report_view.xml',
             'views/vehicle.xml',
             'views/participants.xml',
             'data/transport_schedular.xml',
             'wizard/transfer_vehicle.xml'],
    'demo': ['demo/transport_demo.xml'],
    'test': ['test/transport.yml', 'test/transport_report.yml'],
    'installable': True,
    'application': True
}
