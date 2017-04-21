# -*- coding: utf-8 -*-
# See LICENSE file for full copyright and licensing details.


from odoo import api, models


class ReportLabelInfo(models.AbstractModel):
    _name = 'report.barcode_report.result_label_info'

    def get_student_all_info(self, standard_id, division_id, medium_id,
                             year_id):
        student_obj = self.env['student.student']
        domain = [('standard_id', '=', standard_id.id),
                                          ('division_id', '=', division_id.id),
                                          ('medium_id', '=', medium_id.id),
                                          ('year', '=', year_id.id),
                                          ('state', '=', 'done')]
        student_ids = student_obj.search(domain)
        result = []
        for student in student_ids:
            name = (student.name + " " + student.middle or '' + " " +
                    student.last or '')
            result.append({'name': name,
                           'roll_no': student.roll_no,
                           'pid': student.pid})
        return result

    @api.model
    def render_html(self, docids, data=None):
        docs = self.env['time.table'].browse(docids)
        docargs = {
            'doc_ids': docids,
            'doc_model': docs,
            'data': data,
            'docs': docs,
            'get_student_all_info': self.get_student_all_info,
        }
        return self.env['report'].render('barcode_report.result_label_info',
                                         docargs)
