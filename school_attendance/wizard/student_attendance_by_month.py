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
from openerp.osv import osv, fields

class student_attendance_by_month(osv.TransientModel):
    
    _name = 'student.attendance.by.month'
    _description = 'Student Monthly Attendance Report'
    _columns = {
        'month': fields.selection([(1, 'January'), (2, 'February'), (3, 'March'), (4, 'April'), (5, 'May'), (6, 'June'), (7, 'July'), (8, 'August'), (9, 'September'), (10, 'October'), (11, 'November'), (12, 'December')], 'Month', required=True),
        'year': fields.integer('Year', required=True),
        'attendance_type':fields.selection([('daily','FullDay'),('lecture','Lecture Wise')],'Type'),
    }
    _defaults = {
         'month': lambda *a: time.gmtime()[1],
         'year': lambda *a: time.gmtime()[0],
    }

    def print_report(self, cr, uid, ids, context=None):
        ''' This method prints report
        @param self : Object Pointer
        @param cr : Database Cursor
        @param uid : Current Logged in User
        @param ids : Current Records
        @param context : standard Dictionary
        @return : printed report
        '''
        data = self.read(cr, uid, ids)[0]
        data.update({'stud_ids': context.get('active_ids', [])})
        datas = {
             'ids': [],
             'model': 'student.student',
             'form': data,
        }
        return {
            'type': 'ir.actions.report.xml',
            'report_name': 'attendance.by.month.student',
            'datas': datas,
        }

# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4:
