# See LICENSE file for full copyright and licensing details.

from odoo import api, models


class ReportStudentFeesRegister(models.AbstractModel):
    _name = "report.school_fees.student_fees_register"
    _description = "School Fees Register Report"

    def get_month(self, indate):
        """Method to get month"""
        return indate.strftime("%B") + "-" + indate.strftime("%Y")

    @api.model
    def _get_report_values(self, docids, data=None):
        student_payslip = []
        # Inherited method to get report data
        students_rec = self.env["student.fees.register"].search(
            [("id", "in", docids)]
        )
        fees_report = self.env["ir.actions.report"]._get_report_from_name(
            "school_fees.student_fees_register"
        )
        for student in students_rec.line_ids:
            if student.sudo().student_id.user_id.id == self.env.user.id:
                student_payslip.append(student)
            elif (
                self.env.ref("school.group_school_administration").id
                in self.env.user.groups_id.ids
            ):
                student_payslip.append(student)

        return {
            "doc_ids": docids,
            "doc_model": fees_report.model,
            "docs": students_rec,
            "data": data,
            "get_month": self.get_month,
            "payslip": student_payslip,
        }
