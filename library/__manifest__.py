# -*- coding: utf-8 -*-
# See LICENSE file for full copyright and licensing details.

{
    'name': 'Library Management',
    'version': "11.0.1.0.6",
    'author': "Serpent Consulting Services Pvt. Ltd.",
    'category': 'School Management',
    'website': 'http://www.serpentcs.com',
    'license': "AGPL-3",
    'summary': 'A Module For Library Management For School',
    'complexity': 'easy',
    'depends': ['report_intrastat', 'school', 'stock', 'product',
                'account_invoicing'],
    'data': ['security/library_security.xml',
             'security/ir.model.access.csv',
             'views/report_view.xml',
             'views/qrcode_label.xml',
             'views/library_data.xml',
             'views/library_view.xml',
             'views/library_sequence.xml',
             'views/library_category_data.xml',
             'data/library_card_schedular.xml',
             'wizard/update_book_view.xml',
             'wizard/book_issue_no_view.xml',
             'wizard/card_no_view.xml'],
    'demo': ['demo/library_demo.xml'],
    'image': ['static/description/SchoolLibrary.png'],
    'installable': True,
    'application': True
}
