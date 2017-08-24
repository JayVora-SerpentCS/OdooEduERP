# -*- coding: utf-8 -*-
# See LICENSE file for full copyright and licensing details.

from odoo import models, fields, api
from odoo.exceptions import ValidationError
from odoo.tools.translate import _


class StudentAttendanceByMonth(models.TransientModel):

    _name = 'student.attendance.by.month'
    _description = 'Student Monthly Attendance Report'

    month = fields.Many2one('academic.month')
    year = fields.Many2one('academic.year')
    attendance_type = fields.Selection([('daily', 'FullDay'),
                                        ('lecture', 'Lecture Wise')], 'Type')

    @api.model
    def default_get(self, fields):
        res = super(StudentAttendanceByMonth, self).default_get(fields)
        students = self.env['student.student'
                            ].browse(self._context.get('active_id'))
        if students.state == 'draft':
            raise ValidationError(_('''You can not print report for student in
                                    draft state!'''))
        return res

    @api.multi
    def print_report(self, vals):
        ''' This method prints report
        @param self : Object Pointer
        @param cr : Database Cursor
        @param uid : Current Logged in User
        @param ids : Current Records
        @param context : standard Dictionary
        @return : printed report
        '''
        stud_search = self.env['student.student'
                               ].search([('id', '=', vals.get('active_id')),
                                         ('state', '=', 'done')])
        daily_attend = self.env['daily.attendance']
        for rec in self:
            attend_stud = daily_attend.search([('standard_id', '=',
                                                stud_search.standard_id.id),
                                               ('date', '>=',
                                                rec.month.date_start),
                                               ('date', '<=',
                                                rec.month.date_stop)])
            if not attend_stud:
                raise ValidationError(_('''There is no data of attendance for
                student in selected month or year!'''))
        data = self.read([])[0]
        if data.get('year'):
            data['year'] = self.year.name
        data.update({'stud_ids': vals.get('active_ids')})
        datas = {'ids': [],
                 'model': 'student.student',
                 'type': 'ir.actions.report.xml',
                 'form': data}
        return self.env['report'
                        ].get_action(self,
                                     'school_attendance.attendance_month',
                                     data=datas)
