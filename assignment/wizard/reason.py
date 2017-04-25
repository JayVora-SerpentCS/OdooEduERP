from odoo import models , fields , api,_


class RejectReason(models.TransientModel):
    _name = "reject.reason"

    reasons = fields.Text('Reject Reason')

    @api.multi
    def save_reason(self):
        std_id = self._context.get('active_id')
        student_obj = self.env['school.student.assignment'].search([('id', '=',
                                                                     std_id)])
        student_obj.write({'state': 'reject',
                           'reject_assignment': self.reasons})
        return True
