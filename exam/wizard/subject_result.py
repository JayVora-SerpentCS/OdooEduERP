# See LICENSE file for full copyright and licensing details.

from odoo import api, fields, models


class SubjectResultWiz(models.TransientModel):
    _name = "subject.result.wiz"
    _description = "Subject Wise Result"

    result_ids = fields.Many2many(
        "exam.subject",
        "subject_result_wiz_rel",
        "result_id",
        "exam_id",
        "Exam Subjects",
        help="Select exam subjects",
    )

    @api.model
    def default_get(self, fields):
        """Override default method to get default subjects"""
        res = super(SubjectResultWiz, self).default_get(fields)
        exam_rec = self.env["exam.result"].browse(
            self._context.get("active_id")
        )
        subjectlist = [rec.subject_id.id for rec in exam_rec.result_ids]
        res.update({"result_ids": subjectlist})
        return res

    def result_report(self):
        """Method to get the result report"""
        data = self.read()[0]
        return self.env.ref("exam.add_exam_result_id_qweb").report_action(
            [], data=data
        )
