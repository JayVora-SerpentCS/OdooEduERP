# See LICENSE file for full copyright and licensing details.

from odoo import api, fields, models


class SubjectResultWiz(models.TransientModel):
    _name = "subject.result.wiz"
    _description = "Subject Wise Result"

    result_ids = fields.Many2many(
        "subject.subject",
        "subject_exam_result_wiz_rel",
        "exam_result_id",
        "subject_id",
        "Exam Subjects",
        help="Select exam subjects",
        required=True
    )
    s_exam_id = fields.Many2one(
        "exam.exam", "Examination", required=True, help="Select Exam"
    )

    @api.model
    def default_get(self, fields):
        """Override default method to get default subjects"""
        res = super(SubjectResultWiz, self).default_get(fields)
        exam_rec = self.env["school.teacher"].browse(
            self._context.get("active_id")
        )
        subjectlist =exam_rec.subject_id.ids
        res.update({"result_ids": [(6, 0, subjectlist)]})
        return res

    def result_report(self):
        """Method to get the result report"""
        data = self.read()[0]
        return self.env.ref("exam.add_exam_result_id_qweb").report_action(
            [], data=data
        )
