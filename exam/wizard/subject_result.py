# -*- coding: utf-8 -*-
# See LICENSE file for full copyright and licensing details.

from odoo import models, fields, api


class SubjectResultWiz(models.TransientModel):
    _name = 'subject.result.wiz'
    _description = 'Subject Wise Result'

    result_ids = fields.Many2many("exam.subject", 'subject_result_wiz_rel',
                                  'result_id', "exam_id", "Exam Subjects")

    @api.model
    def default_get(self, fields):
        res = super(SubjectResultWiz, self).default_get(fields)
        s = self._context.get('active_id')
        exams = self.env['exam.result'].browse(s)
        newlist = []
        for rec in exams.result_ids:
            name = rec.subject_id.id
            newlist.append(name)
        res.update({'result_ids': newlist})
        return res

    @api.multi
    def result_report(self):
        data = self.read()[0]
        return self.env['report'].get_action([], 'exam.exam_result_report',
                                             data=data)
