# -*- encoding: utf-8 -*-
##############################################################################
#
#    OpenERP, Open Source Management Solution
#    Copyright (C) 2004-2009 Tiny SPRL (<http://tiny.be>).
#    Copyright (C) 2012-Today Serpent Consulting Services PVT. LTD.
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
    "name": "Transport Management",
    "version": "3.0",
    "author": "Serpent Consulting Services Pvt. Ltd.",
    "website": "http://www.serpentcs.com",
    "category": "School Management",
    "complexity": "easy",
    "description": """A module to School Transport Management.
    A Module support the following functionalities:

    1. In This Module we can define the Transport Root and Points with
       vehicles.
    2. student can do Registration for any root with selected point for
       specific month.
    3. Vehicle information.
    4. Driver information.

    """,
    "depends": [
        "hr",
        "school"
    ],
    "demo": ["demo/transport_demo.xml"],
    "data": [
        "transport_view.xml",
        "report_view.xml",
        "wizard/transfer_vehicle.xml",
        "security/ir.model.access.csv",
        "views/vehicle.xml",
        "views/participants.xml",
    ],

    'test': [
        "test/transport.yml",
        "test/transport_report.yml",
    ],
    "installable": True,
    "auto_install": False,
    "application": True,
}

# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4:
