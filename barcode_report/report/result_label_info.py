# -*- coding: utf-8 -*-
# Part of Odoo. See LICENSE file for full copyright and licensing details.

import time
from dateutil import parser
from odoo import api, fields, models


class ReportLabelInfo(models.AbstractModel):

    _name = 'report.barcode_report.result_label_info'

    def __init__(self):
        super(ResultLabelInfo, self).__init__()
        get_stud_info = self.get_student_info
        self.with_context.update({'get_student_all_info': get_stud_info})

    def get_student_info(self, standard_id, division_id, medium_id, year_id):
        env = odoo.api.Environment(self.cr, self.uid, {})
        student_obj = env['student.student']
        student_ids = student_obj.search([('standard_id', '=', standard_id),
                                          ('division_id', '=', division_id),
                                          ('medium_id', '=', medium_id),
                                          ('year', '=', year_id)])
        result = []
        for stud in student_ids:
            name = stud.name + " " + stud.middle or '' + " " + stud.last or ''
            result.append({'name': name,
                           'roll_no': stud.roll_no, 'pid': stud.pid})
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
        get_student_info = rm_act.get_student_info(standard_id, division_id, medium_id, year_id)
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
        render_model = 'barcode_report.result_label_info'
        return self.env['report'].render(render_model, docargs)
