#-*- coding:utf-8 -*-

##############################################################################
#
#    OpenERP, Open Source Management Solution
#    Copyright (C) 2004-2009 Tiny SPRL (<http://tiny.be>). All Rights Reserved
#    Copyright (C) 2011-2012 Serpent Consulting Services (<http://www.serpentcs.com>)
#
#    This program is free software: you can redistribute it and/or modify
#    it under the terms of the GNU Affero General Public License as published by
#    the Free Software Foundation, either version 3 of the License, or
#    (at your option) any later version.
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
from datetime import datetime
from report import report_sxw

class student_payslip(report_sxw.rml_parse):

    def __init__(self, cr, uid, name, context):
        super(student_payslip, self).__init__(cr, uid, name, context)

        self.localcontext.update({
            'time': time,
            'get_month': self.get_month,
            'get_no': self.get_no,
        })
        self.no = 0   
        
    def get_no(self):
        self.no += 1
        return self.no
    def get_month(self, indate):
        new_date = datetime.strptime(indate, '%Y-%m-%d')
        out_date = new_date.strftime('%B')+'-'+new_date.strftime('%Y')
        return out_date

report_sxw.report_sxw(
    'report.student.payslip',
    'student.payslip',
    '/home/mdi/openerp/stable-6/openobject-addons/school_fees/report/student_payslip.rml',
    parser=student_payslip, header="external"
)

# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4:
