from odoo import fields, models


class AttendanceSheetWiz(models.TransientModel):
    _name = "attendance.sheet.wiz"
    _description = "To Fill Student Attendance"

    attendance_line_ids = fields.Many2many(
        "attendance.sheet.line.matrix",
        default=lambda self: self._default_attendance_line_ids()
    )

    def _default_attendance_line_ids(self):
        """To get the students of list from the selected
        class for filling the attendance"""
        context_params = self._context.get("params")
        daily_attendance_rec = self.env["daily.attendance"].browse(
            context_params.get("id")
        )
        students = self.env["student.student"].search(
                    [
                        ("standard_id", "=", daily_attendance_rec.standard_id.id),
                        ("state", "=", "done"),
                    ]
                )
        recs = self.env["daily.attendance"].search([])
        return [
            (
                0,
                0,
                {
                    "daily_attendance_id": rec.id,
                    "student_id": student.id,
                },
            )
                for rec in recs
            for student in students
        ]