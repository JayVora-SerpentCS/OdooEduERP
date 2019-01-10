# See LICENSE file for full copyright and licensing details.

{
    'name': 'HOSTEL',
    'version': "12.0.1.0.0",
    'author': 'Serpent Consulting Services Pvt. Ltd.',
    'category': 'School Management',
    'website': 'http://www.serpentcs.com',
    'license': "AGPL-3",
    'complexity': 'easy',
    'summary': 'Module For HOSTEL Management In School',
    'depends': ['school', 'account'],
    'images': ['static/description/SchoolHostel.png'],
    'data': ['security/hostel_security.xml',
             'security/ir.model.access.csv',
             'views/hostel_view.xml',
             'views/hostel_sequence.xml',
             'views/report_view.xml',
             'views/hostel_fee_receipt.xml',
             'data/hostel_schedular.xml',
             'wizard/terminate_reason_view.xml'],
    'demo': ['demo/school_hostel_demo.xml'],
    'installable': True,
    'auto_install': False
}
