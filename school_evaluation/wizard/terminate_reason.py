# See LICENSE file for full copyright and licensing details.

from odoo import models


class TerminateReasonEvaluation(models.TransientModel):
    _inherit = "terminate.reason"

    def save_terminate(self):
        """Override method to make student evaluation active false when
        student is terminated"""
        student = self._context.get("active_id")
        student_rec = self.env["student.student"].browse(student)
        student_eval_rec = self.env["school.evaluation"].search(
            [("type", "=", "student"), ("student_id", "=", student_rec.id)]
        )
        if student_eval_rec:
            student_eval_rec.write({"active": False})
        return super(TerminateReasonEvaluation, self).save_terminate()
