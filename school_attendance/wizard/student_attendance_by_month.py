# -*- coding: utf-8 -*-
# Part of Odoo. See LICENSE file for full copyright and licensing details.

import time
from odoo import models, fields, api


class StudentAttendanceByMonth(models.TransientModel):

    _name = 'student.attendance.by.month'
    _description = 'Student Monthly Attendance Report'

    month = fields.Selection([(1, 'January'), (2, 'February'), (3, 'March'),
                              (4, 'April'), (5, 'May'), (6, 'June'),
                              (7, 'July'), (8, 'August'), (9, 'September'),
                              (10, 'October'), (11, 'November'),
                              (12, 'December')], 'Month', required=True,
                             default=lambda *a: time.gmtime()[1])
    year = fields.Integer('Year', required=True,
                          default=lambda *a: time.gmtime()[0])
    attendance_type = fields.Selection([('daily', 'FullDay'),
                                        ('lecture', 'Lecture Wise')], 'Type')

    @api.multi
    def print_report(self):
        ''' This method prints report
        @param self : Object Pointer
        @param cr : Database Cursor
        @param uid : Current Logged in User
        @param ids : Current Records
        @param context : standard Dictionary
        @return : printed report
        '''
        data = self.read([])[0]
        data.update({'stud_ids': self._context.get('active_ids', [])})
        datas = {'ids': [],
                 'model': 'student.student',
                 'form': data}
        return {'type': 'ir.actions.report.xml',
                'report_name': 'attendance.by.month.student',
                'datas': datas}
