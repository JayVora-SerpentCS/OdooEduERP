# See LICENSE file for full copyright and licensing details.

{
    'name': 'School Event Management',
    'version': "12.0.1.0.0",
    'author': 'Serpent Consulting Services Pvt. Ltd.',
    'website': 'http://www.serpentcs.com',
    'images': ['static/description/SchoolEvent.png'],
    'category': 'School Management',
    'license': "LGPL-3",
    'complexity': 'easy',
    'summary': 'A Module For Event Management In School',
    'depends': ['school'],
    'data': ['security/event_security.xml',
             'security/ir.model.access.csv',
             'views/event_view.xml',
             'views/participants.xml',
             'views/report_view.xml'],
    'demo': ['demo/event_demo.xml'],
    'installable': True,
    'application': True
}
