# -*- coding: utf-8 -*-
# See LICENSE file for full copyright and licensing details.

from odoo import models, api
import odoo


class ReportLabel(models.AbstractModel):

    _name = 'report.barcode_report.result_label'

    def __init__(self):
        super(ResultLabel, self).__init__()
        self.localcontext.update({'get_student_info': self.get_student_info})

    def get_student_info(self, standard_id, division_id, medium_id, year_id):
        env = odoo.api.Environment(self.cr, self.uid, {})
        student_obj = env['student.student']
        student_ids = student_obj.search([('standard_id', '=', standard_id),
                                          ('division_id', '=', division_id),
                                          ('medium_id', '=', medium_id),
                                          ('year', '=', year_id)])
        result = []
        for student in student_ids:
            result.append(student.pid)
        return result

    @api.model
    def render_html(self, docids, data=None):
        self.model = self.env.context.get('active_model')
        docs = self.env[self.model].browse(self.env.context.get('active_ids',
                                                                []))
        standard_id = data.get('standard_id')
        division_id = data.get('division_id')
        medium_id = data.get('medium_id')
        year_id = data.get('year_id')
        rm_act = self.with_context(data['form'].get('used_context', {}))
        get_student_info = rm_act.get_student_info(standard_id, division_id,
                                                   medium_id, year_id)
        docargs = {
            'doc_ids': docids,
            'doc_model': self.model,
            'data': data['form'],
            'docs': docs,
            'time': time,
            'GetData': get_data_res,
            'GetReserv': get_reserv_res,
        }
        standard_id = parser.parse(docargs.get('data').get('standard_id '))
        docargs['data'].update({'standard_id': standard_id})
        division_id = parser.parse(docargs.get('data').get('division_id '))
        docargs['data'].update({'division_id': division_id})
        medium_id = parser.parse(docargs.get('data').get('medium_id '))
        docargs['data'].update({'medium_id': medium_id})
        year_id = parser.parse(docargs.get('data').get('year_id '))
        docargs['data'].update({'year_id': year_id})
        render_model = 'barcode_report.result_label'
        return self.env['report'].render(render_model, docargs)
