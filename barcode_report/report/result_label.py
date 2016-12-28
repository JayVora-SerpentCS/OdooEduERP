# -*- coding: utf-8 -*-
# See LICENSE file for full copyright and licensing details.


from odoo import models, api
from odoo.report import report_sxw


class ResultLabel(report_sxw.rml_parse):

    def __init__(self, cr, uid, name, context=None):
        super(ResultLabel, self).__init__(cr, uid, name, context=context)
        self.localcontext.update({'get_student_info': self.get_student_info})

    def get_student_info(self, standard_id, division_id, medium_id, year_id):
        student_obj = self.pool.get('student.student')
        student_ids = student_obj.search(self.cr, self.uid,
                                         [('standard_id', '=', standard_id),
                                          ('division_id', '=', division_id),
                                          ('medium_id', '=', medium_id),
                                          ('year', '=', year_id)])
        result = []
        for student in student_obj.browse(self.cr, self.uid, student_ids):
            result.append(student.pid)
        return result


class ReportLabel(models.AbstractModel):

    _name = 'report.barcode_report.result_label'
    _inherit = 'report.abstract_report'
    _template = 'barcode_report.result_label'
    _wrapped_report_class = ResultLabel
