# -*- coding: utf-8 -*-
# Part of Odoo. See LICENSE file for full copyright and licensing details.

from openerp.report import report_sxw
from openerp import models


class result_label_info(report_sxw.rml_parse):

    def __init__(self, cr, uid, name, context=None):
        super(result_label_info, self).__init__(cr, uid, name, context=context)
        get_stud_info = self.get_student_info
        self.localcontext.update({
                                  'get_student_all_info': get_stud_info,
                                 })

    def get_student_info(self, standard_id, division_id, medium_id, year_id):
        student_obj = self.pool.get('student.student')
        student_ids = student_obj.search(self.cr, self.uid,
                                         [('standard_id', '=', standard_id),
                                          ('division_id', '=', division_id),
                                          ('medium_id', '=', medium_id),
                                          ('year', '=', year_id)])
        result = []
        for student in student_obj.browse(self.cr, self.uid, student_ids):
            result.append({'name': student.name + " "
                           + student.middle or '' + " " + student.last or '',
                           'roll_no': student.roll_no, 'pid': student.pid})
        return result


class report_label_info(models.AbstractModel):

    _name = 'report.barcode_report.result_label_info'
    _inherit = 'report.abstract_report'
    _template = 'barcode_report.result_label_info'
    _wrapped_report_class = result_label_info
