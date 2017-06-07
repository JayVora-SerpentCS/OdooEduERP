# See LICENSE file for full copyright and licensing details.

from odoo.tests import common


class TestAttendance(common.TransactionCase):

    def setUp(self):
        super(TestAttendance, self).setUp()
        self.daily_attendance_obj = self.env['daily.attendance']
        self.hr_employee = self.env.ref('hr.employee_chs')
        self.school_std = self.env.ref('school.demo_school_standard_2')
        self.academic_year = self.env.ref('school.demo_academic_year_2')
        self.month = self.env.ref('school.demo_academic_month_current_6')
        self.stud_id = self.env.ref('school.demo_student_student_5')
        self.daily_attendance_line_obj = self.env['daily.attendance.line']
        self.monthly_attendance_obj = self.env['monthly.attendance.sheet']
        self.sheet_line = self.env['attendance.sheet.line']
        self.attendance_sheet_obj = self.env['attendance.sheet']
        self.attend_report_obj = self.env['student.attendance.by.month']
        # create daily attendance
        self.daily_attendance = self.daily_attendance_obj.\
            create({'user_id': self.hr_employee.id,
                    'standard_id': self.school_std.id,
                    })
        self.daily_attendance._compute_total()
        self.daily_attendance._compute_present()
        self.daily_attendance._compute_absent()
        self.daily_attendance.onchange_standard_id()
        self.daily_attendance.attendance_draft()
        self.daily_attendance.attendance_validate()
        self.daily_attendance_line = self.daily_attendance_line_obj.search(
                                    [('standard_id', '=',
                                      self.daily_attendance.id)])
        for rec in self.daily_attendance_line:
            rec.onchange_attendance()
            rec.onchange_absent()
            # Monthly attendance
        self.monthly_attendance = self.monthly_attendance_obj.\
            create({'standard_id': self.school_std.id,
                    'year_id': self.academic_year.id,
                    'month_id': self.month.id
                    })
        self.monthly_attendance.monthly_attendance_sheet_open_window()
        # Attendance sheet
        self.attendance_sheet = self.attendance_sheet_obj.search(
                                [('standard_id', '=',
                                  self.monthly_attendance.standard_id.id),
                                 ('year_id', '=',
                                 self.monthly_attendance.year_id.id),
                                 ('month_id', '=',
                                  self.monthly_attendance.month_id.id)])
        self.attendance_sheet_obj.onchange_class_info()
        self.sheet = self.sheet_line.search([('standard_id', '=',
                                              self.attendance_sheet.id)])
        for rec in self.sheet:
            rec._compute_percentage()
        vals = {'active_id': self.stud_id.id}
        self.attend_report = self.attend_report_obj.\
            create({'month': 6,
                    'year': '2017'
                    })
        self.attend_report.print_report(vals)

    def test_attendance(self):
        self.assertEqual(self.daily_attendance.user_id,
                         self.daily_attendance.standard_id.user_id)
        self.assertEqual(self.monthly_attendance.year_id,
                         self.monthly_attendance.month_id.year_id)
