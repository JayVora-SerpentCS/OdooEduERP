# -*- coding: utf-8 -*-
# Part of Odoo. See LICENSE file for full copyright and licensing details.

import time
from openerp.report import report_sxw
from openerp import models, api


class Result(report_sxw.rml_parse):

    @api.v7
    def __init__(self, cr, uid, name, context=None):
        super(Result, self).__init__(cr, uid, name, context=context)
        self.localcontext.update({'time': time,
                                  'get_result_info' : self.get_result_info})

    @api.v7
    def get_result_info(self, student):
        res = []
        result_obj = self.pool.get('exam.result')
        result_ids = result_obj.search(self.cr, self.uid,
                                       [('student_id','=',student.id)])
        standard_ids = []
        datas = []
        for result in result_obj.browse(self.cr, self.uid, result_ids):
            if result.standard_id.id not in standard_ids:
                standard_ids.append(result.standard_id.id)
                standard = result.standard_id.standard_id.name +\
                            "["+result.standard_id.division_id.name+"]"
                result_dict = {result.standard_id.id :{
                    'p/f' : result.result,
                    'roll_no' : result.roll_no_id,
                    'standard' : standard,
                    'division' : result.standard_id and \
                        result.standard_id.division_id.name or '',
                    'medium' : result.standard_id and \
                        result.standard_id.medium_id.name or '',
                    'results' : [],
                    'totals' : []
                }}
                for line in result.result_ids:
                    obtain_marks = line.obtain_marks
                    if line.marks_reeval:
                        obtain_marks = line.marks_reeval
                    elif line.marks_access:
                        obtain_marks = line.marks_access
                    result_dict[result.standard_id.id]['results'].append({
                        'subject': line.subject_id.name or '',
                        'code' : line.subject_id.code or '',
                        'max_mark': line.subject_id.maximum_marks or 0.0,
                        'mini_marks': line.subject_id.minimum_marks or 0.0,
                        'obt_marks': obtain_marks or 0.0,
                        'exam' : result.s_exam_ids and result.s_exam_ids.name \
                                or ''
                    })
                res.append(result_dict)
            else:
                for rec in res:
                    for k,v in rec.iteritems():
                        if k == result.standard_id.id:
                            if result.result != 'Pass':
                                v['p/f'] = 'Fail'
                            for line in result.result_ids:
                                obtain_marks = line.obtain_marks
                                if line.marks_reeval:
                                    obtain_marks = line.marks_reeval
                                elif line.marks_access:
                                    obtain_marks = line.marks_access
                                v['results'].append({
                                    'subject': line.subject_id.name or '',
                                    'code' : line.subject_id.code or '',
                                    'max_mark': line.subject_id and \
                                        line.subject_id.maximum_marks or 0.0,
                                    'mini_marks': line.subject_id and \
                                        line.subject_id.minimum_marks or 0.0,
                                    'obt_marks': obtain_marks or 0.0,
                                    'exam' : result.s_exam_ids and \
                                        result.s_exam_ids.name or ''
                                })
        for rec in res:
            for data in rec.values():
                tot_marks = sum(mark['max_mark'] for mark in data['results'])
                obtain = sum(mark['obt_marks'] for mark in data['results'])
                percentage = (obtain / tot_marks) * 100
                data['summary'] = {
                    'total' : tot_marks,
                    'obtain' : obtain,
                    'percentage': percentage,
                }
                datas.append(data)
        return datas


class ReportResultInfo(models.AbstractModel):
    _name = 'report.exam.result_information_report'
    _inherit = 'report.abstract_report'
    _template = 'exam.result_information_report'
    _wrapped_report_class = Result
