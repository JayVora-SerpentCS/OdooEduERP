# -*- encoding: UTF-8 -*-
# -----------------------------------------------------------------------------
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
# -----------------------------------------------------------------------------

{
    'name': 'Fees Management',
    'version': '2.2',
    'author': 'Serpent Consulting Services PVT. LTD.',
    'website': 'http://www.serpentcs.com',
    'category': 'School Management',
    'complexity': 'easy',
    'summary': 'A Module For Fees Management In School',
    'description': '''A module to School Fees Management System.
     A Module support the following functionalities:
        1. Student Fees Management.
        2. Student Fees Receipt.
        3. Student Fees structure.
        4. Student Fees Register.
    ''',
    'depends': ['school', 'account_voucher'],
    'demo': ['demo/school_fees_demo.xml'],
    'data': [
        'security/ir.model.access.csv',
        'views/school_fees_view.xml',
        'views/school_fees_sequence.xml',
        'views/student_fees_register_workflow.xml',
        'views/student_payslip_workflow.xml',
        'views/student_payslip.xml',
        'views/student_fees_register.xml',
        'views/report_view.xml',
    ],
    'installable': True,
    'application': True,
}
