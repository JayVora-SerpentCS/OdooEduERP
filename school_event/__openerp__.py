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
    "name" : "School_Event",
    "version" : "3.1",
    "author" : "Serpent Consulting Services",
    "website" : "http://www.serpentcs.com", 
    "category": "School Management",
    "complexity": "easy",
    "description": """A module to Event Management in School.
    A Module support the following functionalities:
   
    1. In This Module we can define the Event for specific class so the students of that perticular class can only participat in that event.
    2. student can do Registration for events.
    
    """,

    "depends" : ["school"],
    "data" : [
       "event_view.xml", 
       "event_workflow.xml",
       "security/ir.model.access.csv",
       "views/participants.xml",
       "report_view.xml",
    ],
    "demo": [
             "demo/event_demo.xml"
             ],
    'test': [
    ],
    "installable": True,
    "auto_install": False,
    "application": True,
}

# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4:
