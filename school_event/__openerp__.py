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
    'name': 'School Event Management',
    'version': '3.0',
    'author': 'Serpent Consulting Services PVT. LTD.',
    'website': 'http://www.serpentcs.com',
    'category': 'School Management',
    'complexity': 'easy',
    'summary': 'A Module For Event Management In School',
    'description': '''A module to Event Management in School.
    A Module support the following functionalities:
    1. In This Module we can define the Event for specific class
    so the students of particular class can only participate in that event.
    2. student can do Registration for events.
    ''',
    'depends': ['school'],
    'data': [
       'views/event_view.xml',
       'views/event_workflow.xml',
       'security/event_security.xml',
       'security/ir.model.access.csv',
       'views/participants.xml',
       'views/report_view.xml',
    ],
    'demo': ['demo/event_demo.xml'],
    'test': [
    ],
    'installable': True,
    'application': True,
}
