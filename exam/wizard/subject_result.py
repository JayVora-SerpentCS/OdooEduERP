# -*- coding: utf-8 -*-
# Part of Odoo. See LICENSE file for full copyright and licensing details.

from openerp import models, fields, api


class SubjectResultWiz(models.TransientModel):
    _name = 'subject.result.wiz'
    _description = 'Subject Wise Result'

    result_ids = fields.Many2many("exam.subject", 'subject_result_wiz_rel',
                                  'result_id', "exam_id", "Exam Subjects",
                                  select=1)

    @api.multi
    def result_report(self):
        data = self.read(self._ids)[0]
        return self.pool['report'].get_action(self._cr,
                                              self._uid, [],
                                              'exam.exam_result_report',
                                              data=data,
                                              context=self._context)
