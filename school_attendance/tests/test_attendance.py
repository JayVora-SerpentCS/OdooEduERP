# See LICENSE file for full copyright and licensing details.

from datetime import datetime

from dateutil.relativedelta import relativedelta as rd

from odoo.tests import common


class TestAttendance(common.TransactionCase):
    def setUp(self):
        super(TestAttendance, self).setUp()
        self.daily_attendance_obj = self.env["daily.attendance"]
        self.student_leave_request = self.env["studentleave.request"]
        self.teacher = self.env.ref("school.demo_school_teacher_2")
        self.school_std = self.env.ref("school.demo_school_standard_2")
        self.academic_year = self.env.ref("school.demo_academic_year_2")
        self.month = self.env.ref("school.demo_academic_month_current_6")
        self.stud_id = self.env.ref("school.demo_student_student_5")
        self.daily_attendance_line_obj = self.env["daily.attendance.line"]
        self.monthly_attendance_obj = self.env["monthly.attendance.sheet"]
        self.sheet_line = self.env["attendance.sheet.line"]
        self.attendance_sheet_obj = self.env["attendance.sheet"]
        self.attend_report_obj = self.env["student.attendance.by.month"]
        current_date = datetime.now()
        old_date = current_date - rd(days=27)
        attend_date = datetime.strftime(old_date, "%m/%d/%Y")
        leave_start_date = current_date + rd(days=10)
        leave_start = datetime.strftime(leave_start_date, "%m/%d/%Y")
        leave_end_date = current_date + rd(days=20)
        leave_end = datetime.strftime(leave_end_date, "%m/%d/%Y")
        # create daily attendance
        self.daily_attendance = self.daily_attendance_obj.create(
            {
                "user_id": self.teacher.id,
                "standard_id": self.school_std.id,
                # "date": attend_date,
            }
        )
        self.daily_attendance._compute_total()
        self.daily_attendance._compute_present()
        self.daily_attendance._compute_absent()
        self.daily_attendance.get_students()
        self.daily_attendance.attendance_draft()
        self.daily_attendance.attendance_validate()
        self.daily_attendance_line = self.daily_attendance_line_obj.search(
            [("standard_id", "=", self.daily_attendance.id)]
        )
        for rec in self.daily_attendance_line:
            rec.onchange_attendance()
            rec.onchange_absent()
            # Monthly attendance
        self.monthly_attendance = self.monthly_attendance_obj.create(
            {
                "standard_id": self.school_std.id,
                "year_id": self.academic_year.id,
                "month_id": self.month.id,
            }
        )
        self.monthly_attendance.monthly_attendance_sheet_open_window()
        # Attendance sheet
        self.attendance_sheet = self.attendance_sheet_obj.search(
            [
                ("standard_id", "=", self.monthly_attendance.standard_id.id),
                ("year_id", "=", self.monthly_attendance.year_id.id),
                ("month_id", "=", self.monthly_attendance.month_id.id),
            ]
        )
        self.attendance_sheet_obj.onchange_class_info()
        self.sheet = self.sheet_line.search(
            [("standard_id", "=", self.attendance_sheet.id)]
        )
        for rec in self.sheet:
            rec._compute_percentage()
        self.studentleave_create = self.student_leave_request.create(
            {
                "name": "Family Trip Leave",
                "student_id": self.stud_id.id,
                "start_date": leave_start,
                "end_date": leave_end,
                "reason": "Trip",
            }
        )
        self.studentleave_create.onchange_student()
        self.studentleave_create._compute_days()
        self.studentleave_create.toapprove_state()
        self.studentleave_create.approve_state()
        self.studentleave_create.reject_state()

    def test_attendance(self):
        self.assertEqual(
            self.daily_attendance.user_id,
            self.daily_attendance.standard_id.user_id,
        )
        self.assertEqual(
            self.monthly_attendance.year_id,
            self.monthly_attendance.month_id.year_id,
        )
        self.assertEqual(self.studentleave_create.student_id.state, "done")
