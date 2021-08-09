# See LICENSE file for full copyright and licensing details.

from odoo import _, api, fields, models
from odoo.exceptions import ValidationError


class AttendanceSheet(models.Model):
    """Defining Monthly Attendance sheet Information."""

    _description = "Attendance Sheet"
    _name = "attendance.sheet"

    name = fields.Char("Description", readonly=True, help="Enter Description")
    standard_id = fields.Many2one(
        "school.standard",
        "Academic Class",
        required=True,
        help="Select Standard",
    )
    month_id = fields.Many2one(
        "academic.month", "Month", required=True, help="Select Academic Month"
    )
    year_id = fields.Many2one(
        "academic.year", "Year", required=True, help="Select academic year"
    )
    user_id = fields.Many2one(
        "school.teacher", "Faculty", help="Select Teacher"
    )
    attendance_type = fields.Selection(
        [("daily", "FullDay"), ("lecture", "Lecture Wise")],
        "Type",
        help="Select attendance type",
    )
    attendance_sheet_line_ids = fields.One2many(
        "attendance.sheet.line.matrix", "daily_attendance_id"
    )


class StudentleaveRequest(models.Model):
    """Defining Model Student Leave Request."""

    _name = "studentleave.request"
    _description = "Student Leave Request"
    _inherit = ["mail.thread", "resource.mixin"]

    @api.depends("start_date", "end_date")
    def _compute_days(self):
        """Method to compute days based on start-enddate"""
        for rec in self:
            if rec.start_date and rec.end_date:
                rec.days = (rec.end_date - rec.start_date).days + 1
            if rec.start_date == rec.end_date:
                rec.days = 1
            if not rec.start_date or not rec.end_date:
                rec.days = 0

    name = fields.Char(
        "Type of Leave", required=True, help="Leave request name"
    )
    student_id = fields.Many2one(
        "student.student", "Student", required=True, help="Enter Student name"
    )
    roll_no = fields.Char("Roll Number", help="Enter Student name")
    standard_id = fields.Many2one(
        "school.standard", "Class", required=True, help="Select standard"
    )
    attachments = fields.Binary("Attachment", help="Attachments")
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
        help="State of the leave request",
    )
    start_date = fields.Date("Start Date", help="Enter start date")
    end_date = fields.Date("End Date", help="Enter end date")
    teacher_id = fields.Many2one(
        "school.teacher", "Class Teacher", help="Select teacher"
    )
    days = fields.Integer(
        "Days", compute="_compute_days", store=True, help="Days of the week"
    )
    reason = fields.Text("Reason for Leave", help="Reason for the leave")
    message_ids = fields.One2many(
        "mail.message",
        "res_id",
        "Messages",
        domain=lambda self: [("model", "=", self._name)],
        auto_join=True,
        help="Message that about to send",
    )
    message_follower_ids = fields.One2many(
        "mail.followers",
        "res_id",
        "Followers",
        domain=lambda self: [("res_model", "=", self._name)],
        help="Add message followers",
    )

    @api.onchange("student_id")
    def onchange_student(self):
        """Method to get standard and roll no of student selected"""
        if self.student_id:
            self.standard_id = self.student_id.standard_id.id
            self.roll_no = self.student_id.roll_no
            self.teacher_id = self.student_id.standard_id.user_id.id or False

    def _update_student_vals(self, vals):
        student_rec = self.env["student.student"].browse(
            vals.get("student_id")
        )
        vals.update(
            {
                "roll_no": student_rec.roll_no,
                "standard_id": student_rec.standard_id.id,
                "teacher_id": student_rec.standard_id.user_id.id,
            }
        )
        return vals

    @api.model
    def create(self, vals):
        """Inherited create method to  assign
        student details in leave request"""
        if vals.get("student_id"):
            vals = self._update_student_vals(vals)
        return super(StudentleaveRequest, self).create(vals)

    def write(self, vals):
        """Inherited write method to  assign
        student details in leave request"""
        if vals.get("student_id"):
            vals = self._update_student_vals(vals)
        return super(StudentleaveRequest, self).write(vals)

    @api.constrains("student_id", "start_date", "end_date")
    def check_student_request(self):
        """Constraint to check overlapping of date"""
        leave_request = self.search(
            [
                ("student_id", "=", self.student_id.id),
                ("start_date", "=", self.start_date),
                ("end_date", "=", self.end_date),
                ("id", "not in", self.ids),
            ]
        )
        if leave_request:
            raise ValidationError(
                _(
                    """
                You cannot take leave on same date for the same student!"""
                )
            )

    @api.constrains("start_date", "end_date")
    def check_dates(self):
        """Constraint on start-enddate and overlapping the leave request"""
        if self.start_date > self.end_date:
            raise ValidationError(
                _(
                    """Start date should be less than end date!
            """
                )
            )
        if self.start_date < fields.Date.today():
            raise ValidationError(
                _(
                    """Your leave request start date should \
                    be greater than current date!"""
                )
            )

    def approve_state(self):
        """Change state to approve."""
        for rec in self:
            rec.state = "approve"

    def draft_state(self):
        """Change state to draft."""
        for rec in self:
            rec.state = "draft"

    def toapprove_state(self):
        """Change state to toapprove."""
        for rec in self:
            rec.state = "toapprove"

    def reject_state(self):
        """Change state to reject."""
        for rec in self:
            rec.state = "reject"


class DailyAttendance(models.Model):
    """Defining Daily Attendance Information."""

    _description = "Daily Attendance"
    _name = "daily.attendance"
    _rec_name = "standard_id"

    date = fields.Date(
        "Date", help="Current Date", default=fields.Date.context_today
    )
    standard_id = fields.Many2one(
        "school.standard",
        "Academic Class",
        required=True,
        help="Select Standard",
        states={"validate": [("readonly", True)]},
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
        "State",
        readonly=True,
        default="draft",
        help="State of the attendance",
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

    _sql_constraints = [
        (
            "attend_unique",
            "unique(standard_id,user_id,date)",
            "Attendance should be unique!",
        )
    ]

    def _open_student_attendance_sheet(self, view_xmlid):
        """Method to open the wizard to fill
        the attendance of the students"""
        wiz = self.env["attendance.sheet.wiz"].create({})
        view_id = self.env.ref("school_attendance.%s" % view_xmlid).id
        return {
            "name": "Student Attendance Sheet",
            "type": "ir.actions.act_window",
            "view_type": "form",
            "view_mode": "form",
            "res_model": "attendance.sheet.wiz",
            "target": "new",
            "res_id": wiz.id,
            "view_id": view_id,
            "context": self.env.context,
        }

    def open_student_attendance_sheet(self):
        return self._open_student_attendance_sheet(
            "student_attendance_sheet_wiz"
        )

    @api.onchange("user_id")
    def onchange_check_faculty_value(self):
        """Onchange method for faculty"""
        if self.user_id:
            self.standard_id = False

    @api.constrains("date")
    def validate_date(self):
        """Constraint to check selected attendance date"""
        if self.date > fields.Date.today():
            raise ValidationError(
                _("Date should be less than or equal to current date!")
            )

    def attendance_draft(self):
        """Change the state of attendance to draft"""
        for rec in self:
            rec.state = "draft"

    def attendance_validate(self):
        """Method to validate attendance."""
        acadmic_month_obj = self.env["academic.month"]
        attendance_sheet_obj = self.env["attendance.sheet"]

        for rec in self:
            month_ids = acadmic_month_obj.search(
                [
                    ("date_start", "<=", rec.date),
                    ("date_stop", ">=", rec.date),
                    ("year_id.date_start", "<=", rec.date),
                    ("year_id.date_stop", ">=", rec.date),
                ],
                limit=1,
            )
            if not attendance_sheet_obj.search([
                ("month_id", "in", month_ids.ids),
                ("year_id", "=", month_ids.year_id.id)], limit=1):
                attendance_sheet_obj.create({
                    "standard_id": rec.standard_id.id,
                    "user_id": rec.user_id.id,
                    "month_id": month_ids.id,
                    "year_id": month_ids.year_id.id or False
                    })
            rec.state = "validate"


class AttendanceSheetLineMatrix(models.Model):
    _name = "attendance.sheet.line.matrix"
    _description = "Attendance Sheet Line"

    daily_attendance_id = fields.Many2one("daily.attendance")
    student_id = fields.Many2one("student.student")
    is_present_absent = fields.Selection(
        [("present", "Present"), ("absent", "Absent")],
        required=True,
        default="present",
    )
