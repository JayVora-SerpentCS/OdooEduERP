# -*- coding: utf-8 -*-
# See LICENSE file for full copyright and licensing details.

from odoo import models, api, fields, _


class BatchExamResult(models.TransientModel):
    '''designed for printing batch report'''

    _name = "exam.batchwise.result"

    standard_id = fields.Many2one("school.standard",
                                  "Standard")
    year = fields.Many2one('academic.year', 'Academic Year')

    @api.multi
    def print_batch_report(self):
        data = self.read()[0]
        return self.env['report'].get_action([], 'exam.exam_result_batch',
                                             data=data)
