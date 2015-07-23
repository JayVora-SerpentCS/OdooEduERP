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
from openerp import models, fields, api
from openerp.tools.translate import _

    
class monthly_attendance_sheet(models.TransientModel):
    """
    For Monthly Attendance Sheet
    """
    _name = "monthly.attendance.sheet"
    _description = "Monthly Attendance Sheet Wizard"

    standard_id = fields.Many2one('school.standard', 'Academic Class',
                                  required=True)
    year_id = fields.Many2one('academic.year', 'Year', required=True)
    month_id = fields.Many2one('academic.month', 'Month', required=True)

#     _columns = {
#         'standard_id': fields.many2one('school.standard', 'Academic Class',
#                                         required=True ),
#         'year_id': fields.many2one('academic.year', 'Year', required=True),
#         'month_id': fields.many2one('academic.month', 'Month', required=True)
#     }
    @api.multi
    def monthly_attendance_sheet_open_window(self):
        ''' This method open new window with monthly attendance sheet
        @param self : Object Pointer
        @param cr : Database Cursor
        @param uid : Current Logged in User
        @param ids : Current Records
        @param context : standard Dictionary
        @return : record of monthly attendance sheet
        '''
#         if context is None:
#             context = {}
        data = self.read([])[0]
        models_data = self.env['ir.model.data']
        #         atten_sheet_line_created = 0
        # Get opportunity views
        dummy, form_view = models_data.get_object_reference
        ('school_attendance', 'view_attendance_sheet_form')
        dummy, tree_view = models_data.get_object_reference
        ('school_attendance', 'view_attendance_sheet_tree')
        print "\n data ::::::::::::", data
        return {
            'view_type': 'form',
            'view_mode': 'tree, form',
            'res_model': 'attendance.sheet',
            'view_id': False,
            'domain': [('standard_id', '=', data['standard_id'][0]),
                       ('month_id', '=', data['month_id'][0]),
                       ('year_id', '=', data['year_id'][0])],
            'views': [(tree_view or False, 'tree'), (form_view or False,
                                                     'form')],
            'type': 'ir.actions.act_window',
        }

# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4:
