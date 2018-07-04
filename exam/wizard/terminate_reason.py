# -*- coding: utf-8 -*-
# See LICENSE file for full copyright and licensing details.


from odoo import models, api


class TerminateReasonExam(models.TransientModel):
    _inherit = 'terminate.reason'

    @api.multi
    def save_terminate(self):
        '''Override method to make exam results false when student is
        terminated'''
        student = self._context.get('active_id')
        student_obj = self.env['student.student'].browse(student)
        addexam_result = self.env['additional.exam.result'].\
            search([('student_id', '=', student_obj.id)])
        regular_examresult = self.env['exam.result'].\
            search([('student_id', '=', student_obj.id)])
        if addexam_result:
            addexam_result.write({'active': False})
        if regular_examresult:
            regular_examresult.write({'active': False})
        return super(TerminateReasonExam, self).save_terminate()
