# -*- coding: utf-8 -*-
# See LICENSE file for full copyright and licensing details.


from odoo import models, api, _
from odoo.exceptions import ValidationError


class TerminateReasonFees(models.TransientModel):
    _inherit = 'terminate.reason'

    @api.multi
    def save_terminate(self):
        '''Override method to raise warning when fees payment of student is
        remaining when student is terminated'''
        student = self._context.get('active_id')
        student_obj = self.env['student.student'].browse(student)
        student_fees = self.env['student.payslip'].\
            search([('student_id', '=', student_obj.id),
                    ('state', 'in', ['confirm', 'pending'])])
        if student_fees:
            raise ValidationError(_('''You cannot terminate student because
            payment of fees of student is remaining!'''))
        else:
            return super(TerminateReasonFees, self).save_terminate()
