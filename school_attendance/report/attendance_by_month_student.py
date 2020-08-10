# See LICENSE file for full copyright and licensing details.

from odoo import models, api
# import calendar
from datetime import datetime
from dateutil.relativedelta import relativedelta as rd


class BatchExamReport(models.AbstractModel):
    """Defining Batch exam report."""

    _name = 'report.school_attendance.attendance_month'
    _description = "Report attendance Month"

    def get_header_data(self, data):
        attend_month = self.env['student.attendance.by.month'
                                ].browse(data['form']['id'])
        strtdate_str = attend_month.month.date_start.strftime('%Y-%m-%d')
        enddate_str = attend_month.month.date_stop.strftime('%Y-%m-%d')
        start_dt = datetime.strptime(strtdate_str, '%Y-%m-%d')
        end_dt = datetime.strptime(enddate_str, '%Y-%m-%d')
#        delta = end_dt - start_dt
        data_dict = {}
        day_list = []
        week_day_list = []
        while start_dt <= end_dt:
            week_day = start_dt.strftime('%a')
            week_day_list.append(week_day)
            day_list.append(start_dt.day)
            start_dt = start_dt + rd(days=1)
        data_dict.update({'week_day': week_day_list,
                          'day_list': day_list
                          })
        return [data_dict]

    def get_student(self, form):
        stu_list = []
        for student in self.env['student.student'].browse(form['stud_ids']):
            stu_list += student
        return stu_list

    def daily_attendance(self, form, day, student):
        attend_month = self.env['student.attendance.by.month'
                                ].browse(form.get('id'))
        st_date = attend_month.month.date_start.strftime('%Y-%m-%d')
#        end_dt = attend_month.month.date_stop
        attend_obj = self.env['daily.attendance']
        start_date = datetime.strptime(st_date, '%Y-%m-%d')
        if day - start_date.day >= 0:
            attend_date = start_date + rd(days=+day - start_date.day)
        else:
            attend_date = start_date + rd(days=+day + start_date.day)
        sheets = attend_obj.search([('state', '=', 'validate'),
                                    ('date',
                                     '=', attend_date)])
        flag = 'A'
        for sheet in sheets:
            for line in sheet.student_ids:
                if line.stud_id.id == student.id:
                    if line.is_present:
                        flag = 'P'
        return flag

    @api.model
    def _get_report_values(self, docids, data=None):
        attendance_data = self.env['ir.actions.report']._get_report_from_name(
            'school_attendance.attendance_month')
        active_model = self._context.get('active_model')
        docs = self.env[active_model
                        ].browse(self._context.get('active_ids'))
        return {'doc_ids': docids,
                'doc_model': attendance_data.model,
                'data': data,
                'docs': docs,
                'get_header_data': self.get_header_data,
                'daily_attendance': self.daily_attendance,
                'get_student': self.get_student,
                }
