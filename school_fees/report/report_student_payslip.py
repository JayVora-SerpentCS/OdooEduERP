# -*- encoding: utf-8 -*-
##############################################################################
#
#    OpenERP, Open Source Management Solution
#    Copyright (C) 2004-2009 Tiny SPRL (<http://tiny.be>).
#    Copyright (C) 2011-2012 Serpent Consulting Services
#    (<http://www.serpentcs.com>)
#    Copyright (C) 2013-2014 Serpent Consulting Services
#    (<http://www.serpentcs.com>)
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
from datetime import datetime
import time

from openerp.osv import osv
from openerp.report import report_sxw


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
        out_date = new_date.strftime('%B') + '-' + new_date.strftime('%Y')
        return out_date


class report_student_payslip(osv.AbstractModel):
    _name = 'report.school_fees.student_payslip'
    _inherit = 'report.abstract_report'
    _template = 'school_fees.student_payslip'
    _wrapped_report_class = student_payslip

# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4:
