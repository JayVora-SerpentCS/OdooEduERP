# -*- coding: utf-8 -*-
# See LICENSE file for full copyright and licensing details.


import time
from odoo import api, fields, models


class ReportLabelInfo(models.AbstractModel):
    _name = 'report.barcode_report.result_label_info'

    def get_student_info(self, standard_id, division_id, medium_id, year_id):
        student_obj = self.env['student.student']
        student_ids = student_obj.search([('standard_id', '=', standard_id),
                                          ('division_id', '=', division_id),
                                          ('medium_id', '=', medium_id),
                                          ('year', '=', year_id)])
        result = []
        for student in student_obj.browse(student_ids):
            name = (student.name + " " + student.middle or '' + " " +
                    student.last or '')
            result.append({'name': name,
                           'roll_no': student.roll_no, 'pid': student.pid})
        return result

    @api.model
    def render_html(self, docids, data=None):
        self.model = self.env.context.get('active_model')

        docs = self.env[self.model].browse(self.env.context.get('active_ids',
                                                                []))
        standard_id = data['form'].get('standard_id')[0]
        year_id = data['form'].get('year_id')[0]
        get_student = self.with_context(data['form'].get('used_context', {}))
        get_student_info = get_student.get_student_info(standard_id,
                                                        standard_id.div_id,
                                                        standard_id.medium_id,
                                                        year_id)
        docargs = {
            'doc_ids': docids,
            'doc_model': self.model,
            'data': data['form'],
            'docs': docs,
            'time': time,
            'get_student_info': get_student_info,
        }
        render_model = 'barcode_report.result_label_info'
        return self.env['report'].render(render_model, docargs)
