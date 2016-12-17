# -*- coding: utf-8 -*-
# Part of Odoo. See LICENSE file for full copyright and licensing details.

from odoo.report import report_sxw
from odoo import models
import odoo


class ResultLabelInfo(report_sxw.rml_parse):

    def __init__(self, cr, uid, name, context=None):
        super(ResultLabelInfo, self).__init__(cr, uid, name, context=context)
        get_stud_info = self.get_student_info
        self.localcontext.update({'get_student_all_info': get_stud_info})

    def get_student_info(self, standard_id, division_id, medium_id, year_id):
        env = odoo.api.Environment(self.cr, self.uid, {})
        student_obj = env['student.student']
        student_ids = student_obj.search([('standard_id', '=', standard_id),
                                          ('division_id', '=', division_id),
                                          ('medium_id', '=', medium_id),
                                          ('year', '=', year_id)])
        result = []
        for student in student_ids:
            name = student.name + " " + student.middle or '' + " " + student.\
                    last or ''
            result.append({'name': name,
                           'roll_no': student.roll_no, 'pid': student.pid})
        return result


class ReportLabelInfo(models.AbstractModel):

    _name = 'report.barcode_report.result_label_info'
    _inherit = 'report.abstract_report'
    _template = 'barcode_report.result_label_info'
    _wrapped_report_class = ResultLabelInfo
