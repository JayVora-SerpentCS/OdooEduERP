# -*- coding: utf-8 -*-
# See LICENSE file for full copyright and licensing details.

from datetime import datetime
from odoo import models, api


class ReportStudentFeesRegister(models.AbstractModel):
    _name = 'report.school_fees.student_fees_register'

    @api.multi
    def get_month(self, indate):
        new_date = datetime.strptime(indate, '%Y-%m-%d')
        out_date = new_date.strftime('%B') + '-' + new_date.strftime('%Y')
        return out_date

    @api.model
    def get_report_values(self, docids, data=None):
        students = self.env['student.fees.register'].search([('id', 'in',
                                                              docids)])
        fees_report = self.env['ir.actions.report'].\
        _get_report_from_name('school_fees.student_fees_register')
        return {'doc_ids': docids,
                'doc_model': fees_report.model,
                'docs': students,
                'data': data,
                'get_month': self.get_month,
                }
