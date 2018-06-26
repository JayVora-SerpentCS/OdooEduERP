# -*- coding: utf-8 -*-
# See LICENSE file for full copyright and licensing details.

import time
from odoo import models, api


class ReportAddExamResult(models.AbstractModel):
    _name = 'report.exam.exam_result_report'

    @api.model
    def _get_result_detail(self, subject_ids, result):
        sub_list = []
        result_data = []
        for sub in subject_ids:
            sub_list.append(sub.id)
        sub_obj = self.env['exam.subject']
        subject_exam_ids = sub_obj.search([('id', 'in', sub_list),
                                           ('exam_id', '=', result.id)])
        for subject in subject_exam_ids:
            subj = subject.subject_id and subject.subject_id.name or ''
            result_data.append({'subject': subj,
                                'max_mark': subject.maximum_marks or '',
                                'mini_marks': subject.minimum_marks or '',
                                'obt_marks': subject.obtain_marks or '',
                                'reval_marks': subject.marks_reeval or ''})
        return result_data

    @api.model
    def get_report_values(self, docids, data=None):
        active_model = self._context.get('active_model')
        report_result = self.env['ir.actions.report']._get_report_from_name(
            'exam.exam_result_report')
        result_data = self.env[active_model
                               ].browse(self._context.get('active_id'))
        return {'doc_ids': docids,
                'data': data,
                'doc_model': report_result.model,
                'docs': result_data,
                'get_result_detail': self._get_result_detail,
                'time': time,
                }
