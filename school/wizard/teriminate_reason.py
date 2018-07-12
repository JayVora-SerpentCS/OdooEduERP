# See LICENSE file for full copyright and licensing details.

from odoo import models, fields, api


class TerminateReason(models.TransientModel):
    _name = "terminate.reason"

    reason = fields.Text('Reason')

    @api.multi
    def save_terminate(self):
        '''Method to terminate student and change state to terminate'''
        self.env['student.student'
                 ].browse(self._context.get('active_id')
                          ).write({'state': 'terminate',
                                   'terminate_reason': self.reason,
                                   'active': False})
        student = self._context.get('active_id')
        student_obj = self.env['student.student'].browse(student)
        student_obj.standard_id._compute_total_student()
        user = self.env['res.users'].\
            search([('id', '=', student_obj.user_id.id)])
        student_reminder = self.env['student.reminder'].\
            search([('stu_id', '=', student_obj.id)])
        for rec in student_reminder:
            rec.active = False
        if user:
            user.write({'active': False})
