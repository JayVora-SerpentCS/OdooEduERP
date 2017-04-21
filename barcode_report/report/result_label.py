# -*- coding: utf-8 -*-
# See LICENSE file for full copyright and licensing details.


from odoo import api, models


class ReportLabel(models.AbstractModel):

    _name = 'report.barcode_report.result_label'

    @api.multi
    def get_student_info(self, standard_id, division_id, medium_id, year_id):
        student_obj = self.env['student.student']
        domain = [('standard_id', '=', standard_id.id),
                                          ('division_id', '=', division_id.id),
                                          ('medium_id', '=', medium_id.id),
                                          ('year', '=', year_id.id),
                                          ('state', '=', 'done')]
        student_ids = student_obj.search(domain)
        result = []
        for student in student_ids:
            result.append({'pid': student.pid})
        return result

    @api.model
    def render_html(self, docids, data=None):
        docs = self.env['time.table'].browse(docids)
        ans = self.env['time.table'].search([('id', 'in', docids)])
        docargs = {
            'doc_ids': docids,
            'doc_model': docs,          #self.env['time.table'],
            'data': data,
            'docs': docs,
            'get_student_info': self.get_student_info,
        }
        return self.env['report'].render('barcode_report.result_label',
                                         docargs)
