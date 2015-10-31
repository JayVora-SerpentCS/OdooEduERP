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
    'name': 'Transport Management',
    'version': '3.0',
    'author': 'Serpent Consulting Services PVT. LTD.',
    'website': 'http://www.serpentcs.com',
    'category': 'School Management',
    'complexity': 'easy',
    'summary': 'A Module For Transport & Vehicle Management In School',
    'description': '''A module to School Transport Management.
    A Module support the following functionalities:

    1. We can define the Transport Root and Points with vehicles.
    2. Student can Register for any root with selected point for\
       specific month.
    3. Vehicle information.
    4. Driver information.
    ''',
    'depends': ['hr', 'school'],
    'demo': ['demo/transport_demo.xml'],
    'data': [
        'security/ir.model.access.csv',
        'views/transport_view.xml',
        'views/report_view.xml',
        'views/vehicle.xml',
        'views/participants.xml',
        'wizard/transfer_vehicle.xml',
    ],
    'test': [
        'test/transport.yml',
        'test/transport_report.yml',
    ],
    'installable': True,
    'application': True,
}
