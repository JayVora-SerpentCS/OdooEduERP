# See LICENSE file for full copyright and licensing details.

from odoo import models, fields


class RejectReason(models.TransientModel):
    """Defining TransientModel for Reason of Rejection Details."""

    _name = "reject.reason"
    _description = "Reason of Rejection Details"

    reasons = fields.Text('Reject Reason',
                          help='Enter assignment reject reason here')

    def save_reason(self):
        """Method to write reason in assignment model from wizard"""
        student_assignment = self.env['school.student.assignment']
        for rec in self:
            student_rec = student_assignment.browse(
                                            rec._context.get('active_id'))
            if student_rec:
                student_rec.write({'state': 'reject',
                               'rejection_reason': rec.reasons or ''})
        return True
