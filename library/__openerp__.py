# -*- encoding: utf-8 -*-
##############################################################################
#
#    OpenERP, Open Source Management Solution
#    Copyright (C) 2004-2009 Tiny SPRL (<http://tiny.be>).
#    Copyright (C) 2011-2012 Serpent Consulting Services
#    (<http://www.serpentcs.com>)
#    Copyright (C) 2013-2014 Serpent Consulting Services
#    (<http://www.serpentcs.com>)
#    This program is free software: you can redistribute it and/or modify
#    it under the terms of the GNU Affero General Public License as
#    published by the Free Software Foundation, either version 3 of the
#    License, or (at your option) any later version.
#
#    This program is distributed in the hope that it will be useful,
#    but WITHOUT ANY WARRANTY; without even the implied warranty of
#    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#    GNU Affero General Public License for more details.
#
#    You should have received a copy of the GNU Affero General Public License
#    along with this program.  If not, see <http://www.gnu.org/licenses/>.
#
##############################################################################

{
    "name": "Library Management",
    "version": "2.3",
    "author": "Serpent Consulting Services Pvt. Ltd.",
    "category": "School Management",
    "website": "http://www.serpentcs.com",
    "complexity": "easy",
    "description": """Module to manage library.
        Books Information,
        Publisher and Author Information,
        Book Rack Tracking etc...""",
    "depends": [
        "report_intrastat",
        "mrp",
        "delivery",
        "school"
    ],
    "demo": ["demo/library_demo.xml"],
    "data": [
        "security/library_security.xml",
        "security/ir.model.access.csv",
        'email/email_template_new_book_request.xml',
        "library_category_data.xml",
        "wizard/update_prices_view.xml",
        "library_data.xml",
        "library_view.xml",
        "library_issue_workflow.xml",
        "library_sequence.xml",
        "library_workflow.xml",
        "wizard/update_book_view.xml",
        "wizard/book_issue_no_view.xml",
        "wizard/card_no_view.xml",
        "report_view.xml",
        "view/qrcode_label.xml"
    ],
    "installable": True,
    "auto_install": False,
    "application": True,
}

# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4:
