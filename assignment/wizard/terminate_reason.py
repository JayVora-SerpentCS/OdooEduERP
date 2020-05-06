# See LICENSE file for full copyright and licensing details.


from odoo import models


class TerminateReasonAssignment(models.TransientModel):
    _inherit = 'terminate.reason'

    def save_terminate(self):
        '''Override method to make student assignment active false
        when terminated'''
        student = self._context.get('active_id')
        student_obj = self.env['student.student'].browse(student)
        student_assignment = self.env['school.student.assignment'].\
            search([('student_id', '=', student_obj.id)])
        if student_assignment:
            student_assignment.update({'active': False})
        return super(TerminateReasonAssignment, self).save_terminate()
