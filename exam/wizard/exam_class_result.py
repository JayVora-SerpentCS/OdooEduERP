# -*- coding: utf-8 -*-
# Part of Odoo. See LICENSE file for full copyright and licensing details.

from odoo import models, fields, api, _


class ResultPrint(models.TransientModel):
    _name = 'result.print'
    _description = 'students result'

    standard_id = fields.Many2one('school.standard', 'Standard', required=True)
    exam_id = fields.Many2one('exam.exam', 'Exam')
    year_id = fields.Many2one('academic.year', 'Academic Year', required=True)

    @api.multi
    def get_result(self):
        domain = []
        for result_line in self:
            domain = [('standard_id', '=', result_line.standard_id.id),
                      ('s_exam_ids', '=', result_line.exam_id.id)]
            return {'name': _('Result Info'),
                    'view_type': 'form',
                    'view_mode': 'tree,form',
                    'res_model': 'exam.result',
                    'type': 'ir.actions.act_window',
                    'domain': domain}
        return True
