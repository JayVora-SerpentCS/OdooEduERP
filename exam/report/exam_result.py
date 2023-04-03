# See LICENSE file for full copyright and licensing details.

from odoo import _, api, models
from odoo.exceptions import ValidationError


class ReportAddExamResult(models.AbstractModel):
    _name = "report.exam.exam_result_report"
    _description = "Exam result Report"

    @api.model
    def _get_report_values(self, docids, data=None):
        """Inherited method to get report values"""
        result_data = []
        teacher_data = self.env["school.teacher"].browse(
            self._context.get("active_ids")
        )
        subject_exam_ids = self.env["exam.subject"].search(
            [
                ("subject_id", "in", data.get("result_ids")),
                ("exam_id.standard_id", "=", teacher_data.standard_id.id),
                ("exam_id.s_exam_ids", "=", data.get("s_exam_id")[0]),
            ],
            order="subject_id asc",
        )
        if not subject_exam_ids:
            raise ValidationError(_("""There is no data to print!"""))

        student_name = ""
        for subject in subject_exam_ids:
            student_data_dict = {
                "subject": subject.subject_id.name or "",
                "max_mark": subject.maximum_marks or "",
                "mini_marks": subject.minimum_marks or "",
                "obt_marks": subject.obtain_marks or "",
                "reval_marks": subject.marks_reeval or "",
            }
            if (
                not student_name
                or student_name != subject.exam_id.sudo().student_id.name
            ):
                student_name = subject.exam_id.student_id.name
                student_data_dict.update({"student_name": student_name})
            result_data.append(student_data_dict)

        return {
            "doc_ids": docids,
            "data": data,
            "doc_model": "school.teacher",
            "docs": teacher_data,
            "get_result_detail": result_data,
            "exam_name": data.get("s_exam_id")[1],
        }
