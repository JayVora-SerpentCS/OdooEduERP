# See LICENSE file for full copyright and licensing details.

from odoo import api, models


class BatchExamReport(models.AbstractModel):
    _name = "report.exam.exam_result_batch"
    _description = "Batch wise Exam Result"

    def pass_student(self, year, standard_id):
        """Method to determine students who pass the exam"""
        exam_rec = self.env["exam.exam"].search(
            [
                ("standard_id", "=", standard_id.id),
                ("academic_year", "=", year.id),
                ("state", "=", "finished"),
            ]
        )
        exam_result_rec = []
        exam_result_pass_rec = []
        exam_result_fail_rec = []
        result_obj = self.env["exam.result"]
        for rec in exam_rec:
            exam_result_rec += result_obj.search(
                [
                    ("s_exam_ids", "=", rec.id),
                    ("state", "!=", "draft"),
                    ("standard_id", "=", standard_id.id),
                ]
            )
            exam_result_pass_rec += result_obj.search(
                [
                    ("s_exam_ids", "=", rec.id),
                    ("result", "=", "Pass"),
                    ("state", "!=", "draft"),
                    ("standard_id", "=", standard_id.id),
                ]
            )
            exam_result_fail_rec += result_obj.search(
                [
                    ("s_exam_ids", "=", rec.id),
                    ("result", "=", "Fail"),
                    ("state", "!=", "draft"),
                    ("standard_id", "=", standard_id.id),
                ]
            )
        std_pass = ""
        if len(exam_result_pass_rec) > 0:
            # Calculate percentage of students who pass the exams
            std_pass = (100 * len(exam_result_pass_rec)) / len(exam_result_rec)
        return [
            {
                "student_appear": len(exam_result_rec) or 0.0,
                "studnets": len(exam_result_pass_rec) or 0.0,
                "pass_std": std_pass or 0.0,
                "fail_student": len(exam_result_fail_rec) or 0.0,
            }
        ]

    @api.model
    def _get_report_values(self, docids, data=None):
        """Inherited method to get report values."""
        batch_result = self.env["ir.actions.report"]._get_report_from_name(
            "exam.exam_result_batch"
        )
        batch_model = self.env[batch_result.model].browse(
            self.env.context.get("active_ids", [])
        )
        return {
            "doc_ids": docids,
            "doc_model": batch_result.model,
            "docs": batch_model,
            "data": data,
            "pass_student_count": self.pass_student,
        }
