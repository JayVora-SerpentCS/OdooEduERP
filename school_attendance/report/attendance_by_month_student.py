# -*- coding: utf-8 -*-
# See LICENSE file for full copyright and licensing details.

from odoo import models, api
import calendar
from datetime import datetime


class BatchExamReport(models.AbstractModel):

    _name = 'report.school_attendance.attendance_month'

    @api.multi
    def get_days_month(self, data):
        months = calendar.monthrange(data.get('form').get('year'),
                                     data.get('form').get('month'))
        return months[(1)]

    @api.multi
    def getweek_day_month(self, data):
        months = calendar.monthrange(data.get('form').get('year'),
                                     data.get('form').get('month'))
        day_list = []
        for i in range(1, months[1] + 1):
            tmp_date = (str(i) + '-' + str(data.get('form').get('month')) +
                        '-' + str(data.get('form').get('year')))
            week_day = datetime.strptime(tmp_date, '%d-%m-%Y').strftime('%a')
            day_list.append(week_day)
        return day_list

    @api.multi
    def student_present_absent(self, data):
        student_ids = data['form']['stud_ids']
        months = calendar.monthrange(data.get('form').get('year'),
                                     data.get('form').get('month'))
        if student_ids:
            stud_list = []
            for i in range(1, months[1] + 1):
                tmp_date = str(data.get('form').get('month')) + '/' + str(i)\
                            + '/' + str(data.get('form').get('year'))
                for student in student_ids:
                    stud_search = self.env['daily.attendance'
                                           ].search([('date', '=', tmp_date),
                                                     ('state', '=', 'validate')
                                                     ])
                    attend_line = self.env['daily.attendance.line'].search(
                             [('standard_id', '=', stud_search.id),
                              ('stud_id', '=', student)])
                attend = 'A'
                for line in attend_line:
                    if line and line.is_present:
                        attend = 'P'
                stud_list.append(attend)
            return stud_list

    @api.model
    def render_html(self, docids, data):
        self.model = self.env.context.get('active_model')
        docs = self.env[self.model].browse(self.env.context.get('active_ids',
                                                                []))
        docargs = {'doc_ids': docids,
                   'doc_model': self.model,
                   'docs': docs,
                   'data': data,
                   'months': self.get_days_month,
                   'weeks': self.getweek_day_month,
                   'attendance': self.student_present_absent
                   }
        render_model = "school_attendance.attendance_month"
        return self.env['report'].render(render_model, docargs)
