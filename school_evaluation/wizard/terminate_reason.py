# See LICENSE file for full copyright and licensing details.

from odoo import models


class TerminateReasonEvaluation(models.TransientModel):
    _inherit = 'terminate.reason'

    def save_terminate(self):
        '''Override method to make student evaluation active false when
        student is terminated'''
        student = self._context.get('active_id')
        student_obj = self.env['student.student'].browse(student)
        student_eval = self.env['school.evaluation'].\
            search([('type', '=', 'student'),
                    ('student_id', '=', student_obj.id)])
        if student_eval:
            student_eval.write({'active': False})
        return super(TerminateReasonEvaluation, self).save_terminate()
