# -*- encoding: utf-8 -*-
##############################################################################
#
#    OpenERP, Open Source Management Solution
#    Copyright (C) 2004-2009 Tiny SPRL (<http://tiny.be>).
#    Copyright (C) 2011-2012 Serpent Consulting Services (<http://www.serpentcs.com>)
#    Copyright (C) 2013-2014 Serpent Consulting Services (<http://www.serpentcs.com>)
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
import time
from openerp.report import report_sxw
from openerp.osv import osv

class timetable(report_sxw.rml_parse):
    def __init__(self, cr, uid, name, context=None):
        super(timetable, self).__init__(cr, uid, name, context=context)
        self.localcontext.update({
            'time': time,
            'get_timetable':self._get_timetable,
        })

    def _get_timetable(self, timetable_id):
        timetable_detail=[]
        self.cr.execute("select t.start_time,t.end_time,s.name,week_day, \
         r.name as teacher from time_table_line t, subject_subject s, \
         resource_resource r, hr_employee hr where t.subject_id= s.id and \
         t.teacher_id= hr.id  and hr.resource_id = r.id  and table_id = %d \
         group by start_time,end_time,s.name,week_day,r.name order by \
         start_time"%(timetable_id.id))
        res = self.cr.dictfetchall()
#        self.cr.execute("select start_time,end_time from time_table_line 
#        where table_id=%d group by start_time,end_time  order by start_time
#        "%(timetable_id.id))
        self.cr.execute("select start_time,end_time from time_table_line \
        where table_id=%d group by start_time,end_time  order by \
        start_time"%(timetable_id.id))
        time_data = self.cr.dictfetchall()
        for time_detail in time_data:
            for data in res:
                if time_detail['start_time'] == data['start_time'] and \
                   time_detail['end_time'] == data['end_time']:
                    if (data['name'] == 'Recess'):
                        time_detail[data['week_day']] = data['name']
                    else:
                        time_detail[data['week_day']] = data['name']+ \
                                                    '\n(' +data['teacher']+')'
            timetable_detail.append(time_detail)
        return timetable_detail


class report_timetable_info(osv.AbstractModel):
    _name = 'report.timetable.timetable'
    _inherit = 'report.abstract_report'
    _template = 'timetable.timetable'
    _wrapped_report_class = timetable

# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4:
