# -*- encoding: utf-8 -*-
##############################################################################
#
#    OpenERP, Open Source Management Solution
#    Copyright (C) 2004-2009 Tiny SPRL (<http://tiny.be>).
#    Copyright (C) 2011-Today Serpent Consulting Services PVT. LTD.
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
    "name": "Hostel",
    "version": "3.0",
    "author": "Serpent Consulting Services Pvt. Ltd.",
    "category": "School Management",
    "website": "http://www.serpentcs.com",
    "complexity": "easy",
    "description": """Module to Manages Hostel.
        Rooms Information,
        Allocation of Rooms Details
        Discharge of Room Details ...""",
    "depends": ["school"],
    "demo": [
              "demo/school_hostel_demo.xml"
             ],
    "data": [
        "security/hostel_security.xml",
        "security/ir.model.access.csv",
        "hostel_view.xml",
        "hostel_sequence.xml",
        "report_view.xml",
        "views/hostel_fee_receipt.xml",
    ],
    "installable": True,
    "auto_install": False,
}

# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=
