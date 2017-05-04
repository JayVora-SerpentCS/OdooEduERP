from odoo import models, fields, api, _


class TerminateReason(models.TransientModel):
    _name = "terminate.reason"

    reason = fields.Text('Reason')

    @api.multi
    def save_terminate(self):
        stud_id = self._context.get('active_id')
        student = self.env['student.student'].browse(stud_id)
        student.write({'state': 'terminate',
                       'terminate_reason': self.reason})
