# See LICENSE file for full copyright and licensing details.


from odoo import models


class TerminateReasonExam(models.TransientModel):
    _inherit = "terminate.reason"

    def save_terminate(self):
        """Override method to make exam results false when student is
        terminated"""
        student = self._context.get("active_id")
        student_rec = self.env["student.student"].browse(student)
        addexam_result_rec = self.env["additional.exam.result"].search(
            [("student_id", "=", student_rec.id)]
        )
        regular_examresult_rec = self.env["exam.result"].search(
            [("student_id", "=", student_rec.id)]
        )
        if addexam_result_rec:
            addexam_result_rec.write({"active": False})
        if regular_examresult_rec:
            regular_examresult_rec.write({"active": False})
        return super(TerminateReasonExam, self).save_terminate()
