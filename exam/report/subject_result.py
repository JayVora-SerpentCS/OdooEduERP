# -*- coding: utf-8 -*-
# Part of Odoo. See LICENSE file for full copyright and licensing details.

import time
from openerp.report import report_sxw
from openerp import models, api


class SubjectResult(report_sxw.rml_parse):

    @api.v7
    def __init__(self, cr, uid, name, context=None):
        super(SubjectResult, self).__init__(cr, uid, name, context=context)
        self.localcontext.update({'time': time,
                                  'get_subject_result' : self._get_subject_result})

    @api.v7
    def _get_subject_result(self, data):
        if data is None:
            data = {}
        res = []
        result_ids = data.get('result_ids', [])
        subject_ids = data.get('subject_ids', [])
        result_obj = self.pool.get('exam.result')
        for result in result_obj.browse(self.cr, self.uid, result_ids):
            data_dict = {
                'exam' : result.s_exam_ids and result.s_exam_ids.name or '',
                'student' : result.student_id and result.student_id.name or '',
                'result_ids' : [],
                'flag' : False
            }
            for line in result.result_ids:
                if line.subject_id and line.subject_id.id in subject_ids:
                    obtain_marks = line.obtain_marks
                    if line.marks_reeval:
                        obtain_marks = line.marks_reeval
                    elif line.marks_access:
                        obtain_marks = line.marks_access
                    data_dict['result_ids'].append({
                        'subject': line.subject_id.name or '',
                        'max_mark': line.subject_id.maximum_marks or 0.0,
                        'mini_marks': line.subject_id.minimum_marks or 0.0,
                        'obt_marks': obtain_marks or 0.0,
                    })
                    data_dict['flag'] = True
            res.append(data_dict)
        return res



class ReportSubjectResult(models.AbstractModel):
    _name = 'report.exam.exam_result_report'
    _inherit = 'report.abstract_report'
    _template = 'exam.exam_result_report'
    _wrapped_report_class = SubjectResult