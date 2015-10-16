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
    "name" : "School",
    "version" : "3.0",
    "author" : "Serpent Consulting Services Pvt. Ltd.",
    "website" : "http://www.serpentcs.com",
    "category": "School Management",
    "complexity": "easy",
    "description": """A module to School Management.
        A Module support the following functionalities:
        1. Admission Procedure
        2. Student Information
        3. Parent Information
        4. Teacher Information
        5. School Information
        6. Standard, Medium and Division Information
        7. Subject Information
                    """,
    "depends" : ["hr", "email_template", "crm", "report"],
    "data" : [
            "wizard/wiz_send_email_view.xml",
            "security/school_security.xml",
            "school_view.xml",
            "security/ir.model.access.csv",
            "admission_workflow.xml",
            "student_sequence.xml",
            "wizard/assign_roll_no_wizard.xml",
            "wizard/move_standards_view.xml",
            "wizard/wiz_meeting_view.xml",
            "report_view.xml",
            "views/identity_card.xml",
    ],
    "demo": [
           'demo/school_demo.xml',
            ],
    "test": [
        'test/school_test.yml',
        'test/assign_roll_no_test.yml',
        ],
    "installable": True,
    "auto_install": False,
    "application": True,
}

# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4: