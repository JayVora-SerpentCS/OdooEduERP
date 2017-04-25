# -*- coding: utf-8 -*-
# See LICENSE file for full copyright and licensing details.

from odoo import models, fields, api, _


class RejectReason(models.TransientModel):
    _name = "reject.reason"

    reasons = fields.Text('Reject Reason')

    @api.multi
    def save_reason(self):
        std_id = self._context.get('active_id')
        student = self.env['school.student.assignment'].browse(std_id)
        student.write({'state': 'reject',
                       'reject_assignment': self.reasons or ''})
        return True
