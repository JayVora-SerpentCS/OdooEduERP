# -*- coding: utf-8 -*-
# See LICENSE file for full copyright and licensing details.

from odoo import models, api
from datetime import datetime
from dateutil.relativedelta import relativedelta as rd


class BatchExamReport(models.AbstractModel):

    _name = 'report.school_attendance.attendance_month'

    @api.multi
    def get_header_data(self, data):
        attend_month = self.env['student.attendance.by.month'
                                ].browse(self._context.get('active_id'))
        start_dt = datetime.strptime(attend_month.month.date_start, '%Y-%m-%d')
        end_dt = datetime.strptime(attend_month.month.date_stop, '%Y-%m-%d')
        delta = end_dt - start_dt
        data_dict = {}
        day_list = []
        week_day_list = []
        for i in range(0, delta.days + 1):
            tmp_date = start_dt + rd(days=+i)
            week_day = tmp_date.strftime('%a')
            week_day_list.append(week_day)
            day_list.append(i + 1)
        data_dict.update({'week_day': week_day_list,
                          'day_list': day_list})
        return [data_dict]

    @api.multi
    def get_student(self, form):
        stu_list = []
        for student in self.env['student.student'].browse(form['stud_ids']):
            stu_list += student
        return stu_list
#

    def daily_attendance(self, form, day, student):
        attend_month = self.env['student.attendance.by.month'
                                ].browse(self._context.get('active_id'))
        st_date = attend_month.month.date_start
#        end_dt = attend_month.month.date_stop
        attend_obj = self.env['daily.attendance']
        start_date = datetime.strptime(st_date, '%Y-%m-%d')
        attend_date = start_date + rd(days=+day - 1)
        sheets = attend_obj.search([('state', '=', 'validate'),
                                    ('date', '=', attend_date)])
        flag = 'A'
        for sheet in sheets:
            for line in sheet.student_ids:
                if line.stud_id.id == student.id:
                    if line.is_present:
                        flag = 'P'
        return flag

    @api.model
    def render_html(self, docids, data):
        self.model = self.env.context.get('active_model')
        docs = self.env[self.model].browse(self.env.context.get('active_ids',
                                                                []))
        docargs = {'doc_ids': docids,
                   'doc_model': self.model,
                   'docs': docs,
                   'data': data,
                   'get_header_data': self.get_header_data,
                   'get_student': self.get_student,
                   'daily_attendance': self.daily_attendance
                   }
        render_model = "school_attendance.attendance_month"
        return self.env['report'].render(render_model, docargs)
