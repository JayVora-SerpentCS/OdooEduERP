# -*- coding: utf-8 -*-
# See LICENSE file for full copyright and licensing details.

from odoo import models, api
import calendar
from datetime import datetime


class BatchExamReport(models.AbstractModel):

    _name = 'report.school_attendance.attendance_month'

    @api.multi
    def get_header_data(self, data):
        months = calendar.monthrange(data.get('form').get('year'),
                                     data.get('form').get('month'))
        data_dict = {}
        day_list = []
        week_day_list = []
        for i in range(1, months[1] + 1):
            tmp_date = (str(i) + '-' + str(data.get('form').get('month')) +
                        '-' + str(data.get('form').get('year')))
            week_day = datetime.strptime(tmp_date, '%d-%m-%Y').strftime('%a')
            week_day_list.append(week_day)
            day_list.append(i)
        data_dict.update({'week_day': week_day_list,
                          'day_list': day_list})
        return [data_dict]

    @api.multi
    def get_student(self, form):
        stu_list = []
        for student in self.env['student.student'].browse(form['stud_ids']):
            stu_list += student
        return stu_list

    def daily_attendance(self, form, day, student):
        attend_obj = self.env['daily.attendance']
        attend_date = (str(form.get('month')) + '/' + str(day) + '/' +
                       str(form.get('year')))
        sheets = attend_obj.search([('state', '=', 'validate'), ('date',
                                                                 '=',
                                                                 attend_date)])
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
