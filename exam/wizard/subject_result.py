# -*- coding: utf-8 -*-
# Part of Odoo. See LICENSE file for full copyright and licensing details.

from openerp import models, fields, api


class SubjectResultWiz(models.TransientModel):
    _name = 'subject.result.wiz'
    _description = 'Subject Wise Result'

    subject_ids = fields.Many2many("subject.subject", 'subjectwise_result_wiz_rel',
                                  'sub_res_wiz_id', "subject_id", "Subjects")

    @api.multi
    def result_report(self):
        datas = self.read()
        data = datas and datas[0] or {}
        data.update({'result_ids' : self._context and \
                     self._context.get('active_ids', [])})
        return self.pool['report'].get_action(self._cr, self._uid, [],
                                              'exam.exam_result_report',
                                              data=data, context=self._context)
