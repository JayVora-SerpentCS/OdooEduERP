# See LICENSE file for full copyright and licensing details.

import time
from datetime import date, datetime

from num2words import num2words

from odoo import _, api, fields, models
from odoo.exceptions import ValidationError


class AttendanceSheet(models.Model):
    """Defining Monthly Attendance sheet Information."""

    _description = "Attendance Sheet"
    _name = "attendance.sheet"

    name = fields.Char(string="Description", readonly=True)
    standard_id = fields.Many2one(
        "school.standard",
        "Academic Class",
        required=True,
        help="Select Standard",
    )
    month_id = fields.Many2one(
        "academic.month", "Month", required=True, help="Select Academic Month"
    )
    year_id = fields.Many2one("academic.year", "Year", required=True)
    attendance_ids = fields.One2many(
        "attendance.sheet.line",
        "standard_id",
        "Attendance",
        help="Academic Year",
    )
    user_id = fields.Many2one("school.teacher", "Faculty", help="Select Teacher")
    attendance_type = fields.Selection(
        [("daily", "FullDay"), ("lecture", "Lecture Wise")], "Type"
    )

    @api.onchange("standard_id")
    def onchange_class_info(self):
        """Method to get student roll no"""
        stud_list = []
        stud_obj = self.env["student.student"]
        for rec in self:
            if rec.standard_id:
                stud_list = [
                    {"roll_no": stu.roll_no, "name": stu.name}
                    for stu in stud_obj.search(
                        [
                            ("standard_id", "=", rec.standard_id),
                            ("state", "=", "done"),
                        ]
                    )
                ]
            rec.attendance_ids = stud_list


class StudentleaveRequest(models.Model):
    """Defining Model Student Leave Request."""

    _name = "studentleave.request"
    _description = "Student Leave Request"
    _inherit = ["mail.thread", "mail.activity.mixin"]

    def _update_vals(self, student_id):
        student_obj = self.env["student.student"]
        student = student_obj.browse(student_id)
        return {
            "roll_no": student.roll_no,
            "standard_id": student.standard_id.id,
            "teacher_id": student.standard_id.user_id.id,
        }

    @api.model
    def create(self, vals):
        if vals.get("student_id"):
            vals.update(self._update_vals(vals.get("student_id")))
        return super().create(vals)

    def write(self, vals):
        if vals.get("student_id"):
            vals.update(self._update_vals(vals.get("student_id")))
        return super().write(vals)

    def unlink(self):
        """Inherited unlink method to give warning on record deletion"""
        for rec in self:
            if rec.state in ["approve", "reject"]:
                if rec.state == "approve":
                    raise ValidationError(_("""Approve leave can not be deleted!"""))
                else:
                    raise ValidationError(_("""Reject leave can not be deleted!"""))
        return super().unlink()

    @api.onchange("student_id")
    def onchange_student(self):
        """Method to get standard and roll no of student selected"""
        if self.student_id:
            self.standard_id = self.student_id.standard_id.id
            self.roll_no = self.student_id.roll_no
            self.teacher_id = self.student_id.standard_id.user_id.id or False

    def approve_state(self):
        """Change state to approve."""
        leaves = self.filtered(lambda leave: leave.state == "toapprove")
        if leaves:
            self.state = "approve"

    def draft_state(self):
        """Change state to draft."""
        self.state = "draft"

    def toapprove_state(self):
        """Change state to toapprove."""
        leaves = self.filtered(lambda leave: leave.state == "draft")
        if leaves:
            self.state = "toapprove"

    def reject_state(self):
        """Change state to reject."""
        self.state = "reject"

    @api.depends("start_date", "end_date")
    def _compute_days(self):
        for rec in self:
            if rec.start_date and rec.end_date:
                rec.days = (rec.end_date - rec.start_date).days + 1
            if rec.start_date == rec.end_date:
                rec.days = 1
            if not rec.start_date or not rec.end_date:
                rec.days = 0

    name = fields.Char(string="Type of Leave", required=True)
    student_id = fields.Many2one("student.student", "Student", required=True)
    roll_no = fields.Char(string="Roll Number")
    standard_id = fields.Many2one("school.standard", "Class", required=True)
    attachments = fields.Binary("Attachment")
    state = fields.Selection(
        [
            ("draft", "Draft"),
            ("toapprove", "To Approve"),
            ("reject", "Reject"),
            ("approve", "Approved"),
        ],
        "Status",
        default="draft",
        tracking=True,
    )
    start_date = fields.Date()
    end_date = fields.Date()
    teacher_id = fields.Many2one("school.teacher", "Class Teacher")
    days = fields.Integer(compute="_compute_days", store=True)
    reason = fields.Text("Reason for Leave")

    @api.constrains("student_id", "start_date", "end_date")
    def check_student_request(self):
        if self.search(
            [
                ("student_id", "=", self.student_id.id),
                ("start_date", "=", self.start_date),
                ("end_date", "=", self.end_date),
                ("id", "not in", self.ids),
            ],
            limit=1,
        ):
            raise ValidationError(
                _("You cannot take leave on same date for the same student!")
            )

    @api.constrains("start_date", "end_date")
    def check_dates(self):
        if self.start_date > self.end_date:
            raise ValidationError(_("Start date should be less than end date!"))
        if self.start_date < date.today():
            raise ValidationError(
                _(
                    "Your leave request start date should be greater than current"
                    " date!"
                )
            )


class AttendanceSheetLine(models.Model):
    """Defining Attendance Sheet Line Information."""

    def _compute_percentage(self):
        """Method to get attendance percent."""

        res = {}
        for attendance_sheet_data in self:
            percentage = 0.0
            attendance_month = {
                "one": attendance_sheet_data.one,
                "two": attendance_sheet_data.two,
                "three": attendance_sheet_data.three,
                "four": attendance_sheet_data.four,
                "five": attendance_sheet_data.five,
                "six": attendance_sheet_data.six,
                "seven": attendance_sheet_data.seven,
                "eight": attendance_sheet_data.eight,
                "nine": attendance_sheet_data.nine,
                "ten": attendance_sheet_data.ten,
                "eleven": attendance_sheet_data.eleven,
                "twelve": attendance_sheet_data.twelve,
                "thirteen": attendance_sheet_data.thirteen,
                "fourteen": attendance_sheet_data.fourteen,
                "fifteen": attendance_sheet_data.fifteen,
                "sixteen": attendance_sheet_data.sixteen,
                "seventeen": attendance_sheet_data.seventeen,
                "eighteen": attendance_sheet_data.eighteen,
                "nineteen": attendance_sheet_data.nineteen,
                "twenty": attendance_sheet_data.twenty,
                "twentyone": attendance_sheet_data.twentyone,
                "twentytwo": attendance_sheet_data.twentytwo,
                "twentythree": attendance_sheet_data.twentythree,
                "twentyfour": attendance_sheet_data.twentyfour,
                "twentyfive": attendance_sheet_data.twentyfive,
                "twentysix": attendance_sheet_data.twentysix,
                "twentyseven": attendance_sheet_data.twentyseven,
                "twentyeight": attendance_sheet_data.twentyeight,
                "twentynine": attendance_sheet_data.twentynine,
                "thirty": attendance_sheet_data.thirty,
                "thirtyone": attendance_sheet_data.thirtyone,
            }
            attendance_count = 0
            for att in attendance_month.values():
                if att is True:
                    attendance_count += 1
            percentage = (float(attendance_count / 31.00)) * 100
            attendance_sheet_data.percentage = percentage
        return res

    _description = "Attendance Sheet Line"
    _name = "attendance.sheet.line"
    _order = "roll_no"

    roll_no = fields.Integer(
        "Roll Number", required=True, help="Roll Number of Student"
    )
    standard_id = fields.Many2one("attendance.sheet", "Standard")
    name = fields.Char(string="Student Name", required=True, readonly=True)
    one = fields.Boolean("1")
    two = fields.Boolean("2")
    three = fields.Boolean("3")
    four = fields.Boolean("4")
    five = fields.Boolean("5")
    six = fields.Boolean("6")
    seven = fields.Boolean("7")
    eight = fields.Boolean("8")
    nine = fields.Boolean("9")
    ten = fields.Boolean("10")
    eleven = fields.Boolean("11")
    twelve = fields.Boolean("12")
    thirteen = fields.Boolean("13")
    fourteen = fields.Boolean("14")
    fifteen = fields.Boolean("15")
    sixteen = fields.Boolean("16")
    seventeen = fields.Boolean("17")
    eighteen = fields.Boolean("18")
    nineteen = fields.Boolean("19")
    twenty = fields.Boolean("20")
    twentyone = fields.Boolean("21")
    twentytwo = fields.Boolean("22")
    twentythree = fields.Boolean("23")
    twentyfour = fields.Boolean("24")
    twentyfive = fields.Boolean("25")
    twentysix = fields.Boolean("26")
    twentyseven = fields.Boolean("27")
    twentyeight = fields.Boolean("28")
    twentynine = fields.Boolean("29")
    thirty = fields.Boolean("30")
    thirtyone = fields.Boolean("31")

    percentage = fields.Float(
        compute="_compute_percentage", string="Attendance (%)", store=False
    )


class DailyAttendance(models.Model):
    """Defining Daily Attendance Information."""

    _description = "Daily Attendance"
    _name = "daily.attendance"
    _rec_name = "standard_id"

    @api.depends("student_ids")
    def _compute_total(self):
        """Method to compute total student"""
        for rec in self:
            rec.total_student = len(rec.student_ids and rec.student_ids.ids or [])

    @api.onchange("user_id")
    def onchange_check_faculty_value(self):
        if self.user_id:
            self.standard_id = False

    @api.depends("student_ids", "student_ids.is_present")
    def _compute_present(self):
        """Method to count present students."""
        for rec in self:
            count = len([att.id for att in rec.student_ids if att.is_present])
            rec.total_presence = count

    @api.depends("student_ids", "student_ids.is_absent")
    def _compute_absent(self):
        """Method to count absent students"""
        for rec in self:
            count_fail = 0
            if rec.student_ids:
                for att in rec.student_ids:
                    if att.is_absent:
                        count_fail += 1
                rec.total_absent = count_fail

    @api.constrains("date")
    def validate_date(self):
        if self.date > datetime.today():
            raise ValidationError(
                _("""Date should be less than or equal to current date!""")
            )

    date = fields.Datetime(
        help="Current Date",
        default=lambda *a: time.strftime("%Y-%m-%d"),
    )
    standard_id = fields.Many2one(
        "school.standard",
        "Academic Class",
        required=True,
        help="Select Standard",
        states={"validate": [("readonly", True)]},
    )
    student_ids = fields.One2many(
        "daily.attendance.line",
        "standard_id",
        "Students",
        states={
            "validate": [("readonly", True)],
            "draft": [("readonly", False)],
        },
    )
    user_id = fields.Many2one(
        "school.teacher",
        "Faculty",
        help="Select Teacher",
        ondelete="restrict",
        states={"validate": [("readonly", True)]},
    )
    state = fields.Selection(
        [("draft", "Draft"), ("validate", "Validate")],
        readonly=True,
        default="draft",
    )
    total_student = fields.Integer(
        compute="_compute_total",
        store=True,
        help="Total Students in class",
        string="Total Students",
    )
    total_presence = fields.Integer(
        compute="_compute_present",
        store=True,
        string="Present Students",
        help="Present Student",
    )
    total_absent = fields.Integer(
        compute="_compute_absent",
        store=True,
        string="Absent Students",
        help="Absent Students",
    )
    is_generate = fields.Boolean("Generate?")
    subject_id = fields.Many2one("subject.subject", "Subject", help="Subject")
    is_elective_subject = fields.Boolean(help="Check this if subject is elective.")

    @api.constrains("standard_id", "user_id", "date")
    def _check_attendance(self):
        for rec in self:
            attendance = self.env["daily.attendance"].search(
                [
                    ("standard_id", "=", rec.standard_id.id),
                    ("id", "!=", rec.id),
                    ("user_id", "=", rec.user_id.id),
                ],
                limit=1,
            )
            if attendance and attendance.date.date() == rec.date.date():
                raise ValidationError(_("""Attendance should be unique!"""))

    @api.onchange("is_elective_subject")
    def onchange_is_elective_subject(self):
        self.subject_id = False

    def do_regenerate(self):
        self.is_generate = False
        self.student_ids = False

    def get_students(self):
        """Method to get standard of student selected"""
        stud_obj = self.env["student.student"]
        leave_req_obj = self.env["studentleave.request"]
        student_list = []
        for rec in self:
            if rec.standard_id:
                for stud in stud_obj.search(
                    [
                        ("standard_id", "=", rec.standard_id.id),
                        ("state", "=", "done"),
                    ]
                ):
                    stud_vals_abs = (
                        0,
                        0,
                        {
                            "roll_no": stud.roll_no,
                            "stud_id": stud.id,
                            "is_absent": True,
                        },
                    )
                    stud_vals = (
                        0,
                        0,
                        {
                            "roll_no": stud.roll_no,
                            "stud_id": stud.id,
                            "is_present": True,
                        },
                    )
                    if leave_req_obj.search(
                        [
                            ("state", "=", "approve"),
                            ("student_id", "=", stud.id),
                            ("standard_id", "=", rec.standard_id.id),
                            ("start_date", "<=", rec.date),
                            ("end_date", ">=", rec.date),
                        ]
                    ):
                        student_list.append(stud_vals_abs)
                    else:
                        student_list.append(stud_vals)
            rec.student_ids = [(5,)]
            rec.student_ids = student_list
            if rec.student_ids:
                rec.is_generate = True
            else:
                raise ValidationError(_("No Students are found for selected criteria!"))

    @api.model
    def create(self, vals):
        student_list = []
        stud_obj = self.env["student.student"]
        standard_id = vals.get("student_id")
        date = vals.get("date")
        stud_ids = stud_obj.search(
            [
                ("standard_id", "=", vals.get("standard_id")),
                ("state", "=", "done"),
            ]
        )
        for stud in stud_ids:
            line_vals = {
                "roll_no": stud.roll_no,
                "stud_id": stud.id,
                "is_present": True,
            }
            if vals.get("student_ids") and not vals.get("student_ids")[0][2].get(
                "present_absentcheck"
            ):
                student_leave = self.env["studentleave.request"].search(
                    [
                        ("state", "=", "approve"),
                        ("student_id", "=", stud.id),
                        ("standard_id", "=", standard_id),
                        ("start_date", "<=", date),
                        ("end_date", ">=", date),
                    ]
                )
                if student_leave:
                    line_vals.update({"is_absent": True})
            student_list.append((0, 0, line_vals))
        vals.update({"student_ids": student_list})
        return super().create(vals)

    def attendance_draft(self):
        """Change the state of attendance to draft"""
        att_sheet_obj = self.env["attendance.sheet"]
        academic_year_obj = self.env["academic.year"]
        academic_month_obj = self.env["academic.month"]

        for rec in self:
            if not rec.date:
                raise ValidationError(_("Please enter todays date."))
            year_search_ids = academic_year_obj.search([("code", "=", rec.date.year)])
            month_search_ids = academic_month_obj.search(
                [("code", "=", rec.date.month)]
            )
            sheet_ids = att_sheet_obj.search(
                [
                    ("standard_id", "=", rec.standard_id.id),
                    ("month_id", "=", month_search_ids.id),
                    ("year_id", "=", year_search_ids.id),
                ]
            )
            if sheet_ids:
                for data in sheet_ids:
                    for attendance_id in data.attendance_ids:
                        date = rec.date
                        # day_key = f"{date.day:02d}"
                        attendance_key = num2words(int(date.day)).replace("-", "")
                        # Construct the dictionary for the given day
                        dic = {attendance_key: False}

                        # Write the dictionary to the attendance entry
                        attendance_id.write(dic)
            rec.state = "draft"
        return True

    def attendance_validate(self):
        """Method to validate attendance."""
        sheet_line_obj = self.env["attendance.sheet.line"]
        acadmic_year_obj = self.env["academic.year"]
        acadmic_month_obj = self.env["academic.month"]
        attendance_sheet_obj = self.env["attendance.sheet"]

        for line in self:
            year_ids = acadmic_year_obj.search(
                [
                    ("date_start", "<=", line.date),
                    ("date_stop", ">=", line.date),
                ]
            )
            month_ids = acadmic_month_obj.search(
                [
                    ("date_start", "<=", line.date),
                    ("date_stop", ">=", line.date),
                    ("year_id", "in", year_ids.ids),
                ]
            )
            if month_ids:
                month_data = month_ids
                att_sheet_ids = attendance_sheet_obj.search(
                    [
                        ("month_id", "in", month_ids.ids),
                        ("year_id", "in", year_ids.ids),
                    ]
                )
                attendance_sheet_id = att_sheet_ids and att_sheet_ids[0] or False
                date = line.date
                if not attendance_sheet_id:
                    sheet = {
                        "name": (month_data.name + "-" + str(line.date.year)),
                        "standard_id": line.standard_id.id,
                        "user_id": line.user_id.id,
                        "month_id": month_data.id,
                        "year_id": year_ids and year_ids.id or False,
                    }
                    attendance_sheet_id = attendance_sheet_obj.create(sheet)
                    for student_id in line.student_ids:
                        line_dict = {
                            "roll_no": student_id.roll_no,
                            "standard_id": attendance_sheet_id.id,
                            "name": student_id.stud_id.student_name,
                        }
                        sheet_line_obj.create(line_dict)
                        for student_id in line.student_ids:
                            search_id = sheet_line_obj.search(
                                [("roll_no", "=", student_id.roll_no)]
                            )
                            # Compute attendance of each day
                            for day in range(1, 32):
                                day_key = f"{day:02d}"
                                # attendance_key = (
                                #     f"{day_key}_{int(not student_id.is_absent)}"
                                # )
                                attendance_key = num2words(day).replace("-", "")
                                val = {attendance_key: not student_id.is_absent}
                            if search_id:
                                search_id.write(val)

                else:
                    for student_id in line.student_ids:
                        search_id = sheet_line_obj.search(
                            [
                                ("roll_no", "=", student_id.roll_no),
                                ("standard_id", "=", attendance_sheet_id.id),
                            ]
                        )

                        day_key = f"{date.day:02d}"

                        # Compute attendance of each day
                        # attendance_key = f"{day_key}_{int(not student_id.is_absent)}"
                        attendance_key = num2words(int(day_key)).replace("-", "")
                        val = {attendance_key: not student_id.is_absent}

                        if search_id:
                            search_id.write(val)

        self.state = "validate"
        return True


class DailyAttendanceLine(models.Model):
    """Defining Daily Attendance Sheet Line Information."""

    _description = "Daily Attendance Line"
    _name = "daily.attendance.line"
    _order = "roll_no"
    _rec_name = "roll_no"

    roll_no = fields.Integer("Roll No.", help="Roll Number")
    standard_id = fields.Many2one("daily.attendance", "Standard")
    stud_id = fields.Many2one("student.student", "Name")
    is_present = fields.Boolean("Present", help="Check if student is present")
    is_absent = fields.Boolean("Absent", help="Check if student is absent")
    present_absentcheck = fields.Boolean("Present/Absent Boolean")

    @api.onchange("is_present")
    def onchange_attendance(self):
        """Method to make absent false when student is present."""
        if self.is_present:
            self.is_absent = False
            self.present_absentcheck = True

    @api.onchange("is_absent")
    def onchange_absent(self):
        """Method to make present false when student is absent."""
        if self.is_absent:
            self.is_present = False
            self.present_absentcheck = True

    def action_absent(self):
        for rec in self:
            if rec.standard_id.state == "validate" or not rec.standard_id.is_generate:
                raise ValidationError(
                    _(
                        "You cannot mark as absent,"
                        " While attendance is in validate state!"
                    )
                )
            rec.write({"is_present": False})
            rec.write({"is_absent": True})
        return True

    def action_present(self):
        for rec in self:
            if rec.standard_id.state == "validate" or not rec.standard_id.is_generate:
                raise ValidationError(
                    _(
                        "You cannot mark as present,"
                        " While attendance is in validate state!"
                    )
                )
            rec.is_present = True
            rec.is_absent = False
        return True
