# -*- coding: utf-8 -*-
# Part of Odoo. See LICENSE file for full copyright and licensing details.

import time
from openerp.report import report_sxw
from openerp import models, api


class TimeTable(report_sxw.rml_parse):

    @api.v7
    def __init__(self, cr, uid, name, context=None):
        super(TimeTable, self).__init__(cr, uid, name, context=context)
        self.localcontext.update({'time': time,
                                  'get_timetable': self._get_timetable})

    @api.v7
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
                if ((time_detail['start_time'] == data['start_time'])
                        and (time_detail['end_time'] == data['end_time'])):
                    if (data['name'] == 'Recess'):
                        time_detail[data['week_day']] = data['name']
                    else:
                        time_detail[data['week_day']] = (data['name'] +
                                                         '\n(' +
                                                         data['teacher'] +
                                                         ')')
            timetable_detail.append(time_detail)
        return timetable_detail


class ReportTimetableInfo(models.AbstractModel):
    _name = 'report.timetable.timetable'
    _inherit = 'report.abstract_report'
    _template = 'timetable.timetable'
    _wrapped_report_class = TimeTable
