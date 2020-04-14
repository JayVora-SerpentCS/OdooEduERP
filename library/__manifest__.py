# See LICENSE file for full copyright and licensing details.

{
    'name': 'Library Management',
    'version': "13.0.1.0.0",
    'author': "Serpent Consulting Services Pvt. Ltd.",
    'category': 'School Management',
    'website': 'http://www.serpentcs.com',
    'license': "AGPL-3",
    'summary': 'A Module For Library Management For School',
    'complexity': 'easy',
    'depends': ['school', 'stock', 'delivery', 'purchase'],
    'data': ['security/library_security.xml',
             'security/ir.model.access.csv',
             'views/report_view.xml',
             'views/qrcode_label.xml',
             'views/library_view.xml',
             'data/library_sequence.xml',
             'data/library_category_data.xml',
             'data/library_card_schedular.xml',
             'wizard/update_book_view.xml',
             'wizard/book_issue_no_view.xml',
             'wizard/card_no_view.xml',
             'wizard/terminate_reason.xml'],
    'demo': ['demo/library_demo.xml'],
    'image': ['static/description/SchoolLibrary.png'],
    'installable': True,
    'application': True
}
