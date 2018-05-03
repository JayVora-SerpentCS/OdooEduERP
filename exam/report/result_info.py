# -*- coding: utf-8 -*-
# See LICENSE file for full copyright and licensing details.

from odoo import models, api
from odoo.exceptions import ValidationError
from odoo.tools.translate import _


class ReportResultInfo(models.AbstractModel):
    _name = 'report.exam.result_information_report'

    @api.model
    def get_grade(self, result_id, student):
        list_fail = []
        value = {}
        for stu_res in student.year.grade_id.grade_ids:
            value.update({'fail': stu_res.fail})
        list_fail.append(value)
        return list_fail

    @api.model
    def get_lines(self, result_id, student):
        list_result = []
        for sub_id in result_id:
            for sub in sub_id.result_ids:
                std_id = sub_id.standard_id.standard_id.name
                list_result.append({'standard_id': std_id,
                                    'name': sub.subject_id.name,
                                    'code': sub.subject_id.code,
                                    'maximum_marks': sub.maximum_marks,
                                    'minimum_marks': sub.minimum_marks,
                                    'obtain_marks': sub.obtain_marks,
                                    's_exam_ids': sub_id.s_exam_ids.name})
        return list_result

    @api.model
    def get_exam_data(self, result_id, student):
        list_exam = []
        value = {}
        final_total = 0
        per = 0.0
        obtain_marks = 0.0
        maximum_marks = 0.0
        for res in result_id:
            if res.result_ids:
                for res_data in res.result_ids:
                    obtain_marks += float(res_data.obtain_marks)
                    maximum_marks += float(res_data.maximum_marks)
                per += obtain_marks * 100 / maximum_marks
            final_total = final_total + res.total
            value.update({'result': res.result,
                          'percentage': per,
                          'total': final_total})
        list_exam.append(value)
        return list_exam

    @api.model
    def get_report_values(self, docids, data=None):
        docs = self.env['student.student'].browse(docids)
        student_model = self.env['ir.actions.report'].\
        _get_report_from_name('exam.result_information_report')
        for rec in docs:
            student_search = self.env['exam.result'].search([('student_id',
                                                              '=', rec.id)])
            if not student_search or rec.state == 'draft':
                raise ValidationError(_('''You cannot print report for student
                in unconfirm state or when data is not found !'''))
            return {'doc_ids': docids,
                    'doc_model': student_model.model,
                    'data': data,
                    'docs': docs,
                    'get_lines': self.get_lines,
                    'get_exam_data': self.get_exam_data,
                    }
