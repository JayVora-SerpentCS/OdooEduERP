# See LICENSE file for full copyright and licensing details.

from odoo import _, api, models
from odoo.exceptions import ValidationError


class ReportResultInfo(models.AbstractModel):
    _name = "report.exam.result_information_report"
    _description = "Exam result information report"

    @api.model
    def get_grade(self, result_id, student):
        """Method to get the grade info of student"""
        list_fail = []
        value = {}
        for stu_res in student.year.grade_id.grade_ids:
            value.update({"fail": stu_res.fail})
        list_fail.append(value)
        return list_fail

    @api.model
    def get_lines(self, result_id, student):
        """Method to get the grade info of student"""
        list_result = []
        for sub_id in result_id:
            for sub in sub_id.result_ids:
                obtain_mark = sub.obtain_marks
                if sub_id.state in ["re-evaluation", "re-evaluation_confirm"]:
                    obtain_mark = sub.marks_reeval
                list_result.append(
                    {
                        "standard_id": sub_id.standard_id.standard_id.name,
                        "name": sub.subject_id.name,
                        "code": sub.subject_id.code,
                        "maximum_marks": sub.maximum_marks,
                        "minimum_marks": sub.minimum_marks,
                        "obtain_marks": obtain_mark,
                        "s_exam_ids": sub_id.s_exam_ids.name,
                    }
                )
        return list_result

    @api.model
    def _get_report_values(self, docids, data=None):
        """Inherited method to get report values"""
        docs = self.env["student.student"].browse(docids)
        student_model = self.env["ir.actions.report"]._get_report_from_name(
            "exam.result_information_report"
        )
        exam_result_obj = self.env["exam.result"]
        for rec in docs:
            student_search = exam_result_obj.search([("student_id", "=", rec.id)])
            if not student_search or rec.state == "draft":
                raise ValidationError(
                    _(
                        """You cannot print report for student
in unconfirm state or when data is not found !"""
                    )
                )
            return {
                "doc_ids": docids,
                "doc_model": student_model.model,
                "data": data,
                "docs": docs,
                "get_lines": self.get_lines,
            }
