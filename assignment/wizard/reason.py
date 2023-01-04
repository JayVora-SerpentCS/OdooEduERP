# See LICENSE file for full copyright and licensing details.

from odoo import fields, models


class RejectReason(models.TransientModel):
    """Defining TransientModel for Reason of Rejection Details."""

    _name = "reject.reason"
    _description = "Reason of Rejection Details"

    reasons = fields.Text(
        "Reject Reason",
        help="Enter assignment reject reason here")

    def save_reason(self):
        """Method to write reason in assignment model from wizard"""
        student_assignment = self.env["school.student.assignment"]
        if self.env.context.get("active_id"):
            for rec in self:
                assignment_rec = student_assignment.search([
                    ('id', '=', self.env.context.get("active_id"))], limit=1
                    )
                assignment_rec.write(
                    {
                        'state': 'reject',
                        'assignment_reject_history_ids': [(0, 0, {
                            'assignment_id': assignment_rec.id,
                            'name': rec.reasons,
                            'user_id': rec.env.user.id})]
                        })
        return True
