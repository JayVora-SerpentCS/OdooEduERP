# -*- coding: utf-8 -*-
# See LICENSE file for full copyright and licensing details.

{
    'name': 'Transport Management',
    'version': "1.0.3",
    'author': '''Serpent Consulting Services Pvt. Ltd.,
                 Odoo Community Association (OCA)''',
    'website': 'http://www.serpentcs.com',
    'license': "AGPL-3",
    'category': 'School Management',
    'complexity': 'easy',
    'summary': 'A Module For Transport & Vehicle Management In School',
    'depends': ['hr', 'school'],
    'data': ['security/transport_security.xml',
             'security/ir.model.access.csv',
             'views/transport_view.xml',
             'views/report_view.xml',
             'views/vehicle.xml',
             'views/participants.xml',
             'wizard/transfer_vehicle.xml'],
    'demo': ['demo/transport_demo.xml'],
    'test': ['test/transport.yml', 'test/transport_report.yml'],
    'installable': True,
    'application': True
}
