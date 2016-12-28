# -*- coding: utf-8 -*-
# See LICENSE file for full copyright and licensing details.

import time
from datetime import datetime
from odoo import models, api


class ReportStudentPayslip(models.AbstractModel):
    _name = 'report.school_fees.student_payslip'

    @api.multi
    def get_no(self):
        self.no += 1
        return self.no

    @api.multi
    def get_month(self, indate):
        new_date = datetime.strptime(indate, '%Y-%m-%d')
        out_date = new_date.strftime('%B') + '-' + new_date.strftime('%Y')
        return out_date

    @api.model
    def render_html(self, docids, data=None):
        self.model = self.env.context.get('active_model')

        docs = self.env[self.model].browse(self.env.context.get('active_ids',
                                                                []))
        indate = data['form'].get('indate')
        get_student = self.with_context(data['form'].get('used_context', {}))
        get_no = get_student.get_no()
        get_month = get_student.get_month(indate)
        docargs = {
            'doc_ids': docids,
            'doc_model': self.model,
            'data': data['form'],
            'docs': docs,
            'time': time,
            'get_no': get_no,
            'get_month': get_month,
        }
        render_model = 'school_fees.student_payslip'
        return self.env['report'].render(render_model, docargs)
