# -*- encoding: UTF-8 -*-
##############################################################################
#
#    OpenERP, Open Source Management Solution
#    Copyright (C) 2012-Today Serpent Consulting Services PVT. LTD.
#    (<http://www.serpentcs.com>)
#
#    This program is free software: you can redistribute it and/or modify
#    it under the terms of the GNU General Public License as published by
#    the Free Software Foundation, either version 3 of the License, or
#    (at your option) any later version.
#
#    This program is distributed in the hope that it will be useful,
#    but WITHOUT ANY WARRANTY; without even the implied warranty of
#    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#    GNU General Public License for more details.
#
#    You should have received a copy of the GNU General Public License
#    along with this program.  If not, see <http://www.gnu.org/licenses/>
#
##############################################################################

{
    'name': 'Library Management',
    'version': '2.2',
    'author': 'Serpent Consulting Services PVT. LTD.',
    'category': 'School Management',
    'website': 'http://www.serpentcs.com',
    'complexity': 'easy',
    'description': '''Module to manage library.
        Books Information,
        Publisher and Author Information,
        Book Rack Tracking etc...''',
    'depends': ['report_intrastat', 'mrp', 'delivery', 'school'],
    'demo': ['demo/library_demo.xml'],
    'data': [
        'security/library_security.xml',
        'security/ir.model.access.csv',
        'views/report_view.xml',
        'views/qrcode_label.xml',
        'views/library_data.xml',
        'views/library_view.xml',
        'views/library_issue_workflow.xml',
        'views/library_sequence.xml',
        'views/library_workflow.xml',
        'views/library_category_data.xml',
        'wizard/update_prices_view.xml',
        'wizard/update_book_view.xml',
        'wizard/book_issue_no_view.xml',
        'wizard/card_no_view.xml',
    ],
    'installable': True,
    'application': True,
}
