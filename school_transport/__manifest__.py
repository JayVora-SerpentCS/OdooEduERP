# See LICENSE file for full copyright and licensing details.

{
    'name': 'Transport Management',
    'version': "12.0.1.0.0",
    'author': 'Serpent Consulting Services Pvt. Ltd.',
    'website': 'http://www.serpentcs.com',
    'license': "LGPL-3",
    'category': 'School Management',
    'complexity': 'easy',
    'summary': 'A Module For Transport & Vehicle Management In School',
    'depends': ['school', 'account'],
    'images': ['static/description/SchoolTransport.png'],
    'data': ['security/transport_security.xml',
             'security/ir.model.access.csv',
             'views/transport_view.xml',
             'views/report_view.xml',
             'views/vehicle.xml',
             'views/participants.xml',
             'data/transport_schedular.xml',
             'wizard/transfer_vehicle.xml',
             'wizard/terminate_reason_view.xml'],
    'demo': ['demo/transport_demo.xml'],
    'installable': True,
    'application': True
}
