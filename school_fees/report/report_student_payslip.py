# See LICENSE file for full copyright and licensing details.

from datetime import datetime
from odoo import models, api


class ReportStudentPayslip(models.AbstractModel):
    _name = 'report.school_fees.student_payslip'
    _description = "School Fees Payslip Report"

    @api.multi
    def get_month(self, indate):
        new_date = datetime.strptime(indate, '%Y-%m-%d')
        out_date = new_date.strftime('%B') + '-' + new_date.strftime('%Y')
        return out_date

    @api.model
    def _get_report_values(self, docids, data=None):
        student_payslip = self.env['student.payslip'].search([('id', 'in',
                                                               docids)])
        payslip_model = self.env['ir.actions.report'].\
            _get_report_from_name('school_fees.student_payslip')
        return {
            'doc_ids': docids,
            'doc_model': payslip_model.model,
            'docs': student_payslip,
            'data': data,
            'get_month': self.get_month
        }
