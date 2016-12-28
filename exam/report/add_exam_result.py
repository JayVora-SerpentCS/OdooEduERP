# -*- coding: utf-8 -*-
# See LICENSE file for full copyright and licensing details.

import time
from odoo.report import report_sxw
from odoo import models, api
import odoo


class AddExamResult(report_sxw.rml_parse):

    @api.model
    def __init__(self):
        super(AddExamResult, self).__init__()
        get_result_detail = self._get_result_detail
        self.localcontext.update({'time': time,
                                  'get_result_detail': get_result_detail})

    @api.model
    def _get_result_detail(self, subject_ids, result):
        sub_list = []
        result_data = []
        for sub in subject_ids:
            sub_list.append(sub.id)
        env = odoo.api.Environment(self.cr, self.uid, {})
        sub_obj = env['exam.subject']
        subject_exam_ids = sub_obj.search([('id', 'in', sub_list),
                                           ('exam_id', '=', result.id)])
        for subject in subject_exam_ids:
            subj = subject.subject_id and subject.subject_id.name or ''
            result_data.append({'subject': subj,
                                'max_mark': subject.maximum_marks or '',
                                'mini_marks': subject.minimum_marks or '',
                                'obt_marks': subject.obtain_marks or ''})
        return result_data


class ReportAddExamResult(models.AbstractModel):
    _name = 'report.exam.exam_result_report'
    _inherit = 'report.abstract_report'
    _template = 'exam.exam_result_report'
    _wrapped_report_class = AddExamResult
