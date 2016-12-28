# -*- coding: utf-8 -*-
# See LICENSE file for full copyright and licensing details.

import time
from odoo import models, api


class ReportTimetableInfo(models.AbstractModel):
    _name = 'report.timetable.timetable'

    @api.multi
    def _get_timetable(self, timetable_id):
        timetable_detail = []
        self.cr.execute("select t.start_time,t.end_time,s.name,week_day,r.name\
                         as teacher from time_table_line t, subject_subject s,\
                         resource_resource r, hr_employee hr where\
                         t.subject_id= s.id and t.teacher_id= hr.id\
                         and hr.resource_id = r.id  and table_id = %d\
                         group by start_time,end_time,s.name,week_day,r.name\
                         order by start_time" % (timetable_id.id))
        res = self.cr.dictfetchall()
        self.cr.execute("select start_time,end_time from time_table_line\
                         where table_id=%d group by start_time,end_time\
                         order by start_time" % (timetable_id.id))
        time_data = self.cr.dictfetchall()
        for time_detail in time_data:
            for data in res:
                if ((time_detail['start_time'] == data['start_time']) and
                        (time_detail['end_time'] == data['end_time'])):
                    if (data['name'] == 'Recess'):
                        time_detail[data['week_day']] = data['name']
                    else:
                        td = data['name'] + '\n(' + data['teacher'] + ')'
                        time_detail[data['week_day']] = td
            timetable_detail.append(time_detail)
        return timetable_detail

    @api.model
    def render_html(self, docids, data=None):
        self.model = self.env.context.get('active_model')

        docs = self.env[self.model].browse(self.env.context.get('active_ids',
                                                                []))
        timetable_id = data['form'].get('timetable_id')[0]
        get_student = self.with_context(data['form'].get('used_context', {}))
        _get_timetable = get_student._get_timetable(timetable_id)
        docargs = {
            'doc_ids': docids,
            'doc_model': self.model,
            'data': data['form'],
            'docs': docs,
            'time': time,
            '_get_timetable': _get_timetable,
        }
        render_model = 'timetable.timetable'
        return self.env['report'].render(render_model, docargs)
