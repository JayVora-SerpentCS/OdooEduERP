# -*- encoding: utf-8 -*-
##############################################################################
#
#    OpenERP, Open Source Management Solution
#    Copyright (C) 2004-2009 Tiny SPRL (<http://tiny.be>).
#    Copyright (C) 2011-2012 Serpent Consulting Services (<http://www.serpentcs.com>)
#    Copyright (C) 2013-2014 Serpent Consulting Services (<http://www.serpentcs.com>)
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
    "name" : "Attendance Management",
    "version" : "3.0",
    "author" : "Serpent Consulting Services",
    "website" : "http://www.serpentcs.com",
    "category": "School Management",
    "complexity": "easy",
    "description": """A module to Student Attendance System.
        A Module support the following functionalities:
            1. Class-wise Daily Attendance Sheet.
            2. Class-wise Monthly Attendance Sheet.
                    """,
    "depends" : [
        "school","hr"
    ],
    "data" : [
        "security/ir.model.access.csv",
        "school_attendance_view.xml",
        "attendance_workflow.xml",
        "wizard/attendance_sheet_wizard_view.xml",
        "wizard/student_attendance_by_month_view.xml",
    ],
    'demo': [
             "demo/school_attendance_demo.xml"
    ],
    
    "installable": True,
    "auto_install": False,
    "application": True,
}

# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4: