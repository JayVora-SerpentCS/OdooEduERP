# -*- coding: utf-8 -*-
# Part of Odoo. See LICENSE file for full copyright and licensing details.

from openerp import models, fields, api


class MonthlyAttendanceSheet(models.TransientModel):
    '''For Monthly Attendance Sheet'''
    _name = "monthly.attendance.sheet"
    _description = "Monthly Attendance Sheet Wizard"

    standard_id = fields.Many2one('school.standard', 'Academic Class',
                                  required=True)
    year_id = fields.Many2one('academic.year', 'Year', required=True)
    month_id = fields.Many2one('academic.month', 'Month', required=True)

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
        data = self.read([])[0]
        models_data = self.env['ir.model.data']
        # Get opportunity views
        dummy, form_view = models_data.get_object_reference(
                            'school_attendance', 'view_attendance_sheet_form')
        dummy, tree_view = models_data.get_object_reference(
                            'school_attendance', 'view_attendance_sheet_tree')
        return {
                'view_type': 'form',
                'view_mode': 'tree, form',
                'res_model': 'attendance.sheet',
                'view_id': False,
                'domain': [('standard_id', '=', data['standard_id'][0]),
                           ('month_id', '=', data['month_id'][0]),
                           ('year_id', '=', data['year_id'][0])],
                'views': [(tree_view or False, 'tree'),
                          (form_view or False, 'form')],
                'type': 'ir.actions.act_window',
               }
