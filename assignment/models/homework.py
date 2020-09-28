# See LICENSE file for full copyright and licensing details.

from odoo import _, api, fields, models
from odoo.exceptions import ValidationError


class SchoolTeacherAssignment(models.Model):
    """Defining Model for Teacher Assignment Information."""

    _name = "school.teacher.assignment"
    _description = "Teacher Assignment Information"

    name = fields.Char("Assignment Name", help="Name of Assignment")
    subject_id = fields.Many2one(
        "subject.subject", "Subject", required=True, help="Select Subject"
    )
    standard_id = fields.Many2one(
        "school.standard", "Class", help="Select Standard"
    )
    teacher_id = fields.Many2one(
        "school.teacher", "Teacher", required=True, help="Select Teacher"
    )
    assign_date = fields.Date(
        "Assign Date", required=True, help="Starting date of assignment"
    )
    due_date = fields.Date(
        "Due Date", required=True, help="Ending date of assignment"
    )
    attached_homework = fields.Binary(
        "Attached Home work", help="Attached Homework"
    )
    state = fields.Selection(
        [("draft", "Draft"), ("active", "Active"), ("done", "Done")],
        "Status",
        default="draft",
        help="State of teacher assignment",
    )
    student_assign_ids = fields.One2many(
        "school.student.assignment",
        "teacher_assignment_id",
        string="Student Assignments",
        help="Enter student assignments",
    )
    type_submission = fields.Selection(
        [("hardcopy", "Hardcopy(Paperwork)"), ("softcopy", "Softcopy")],
        default="hardcopy",
        string="Submission Type",
        help="Select Assignment type",
    )
    file_format = fields.Many2one(
        "file.format", "File Format", help="File format"
    )
    attach_files = fields.Char("File Name", help="Enter file name")
    subject_standard_assignment = fields.Many2one(
        "standard.standard",
        help="""Standard of the
                                                  assignment in which it
                                                  assigned""",
    )

    @api.onchange("standard_id")
    def onchange_subject_standard(self):
        """Onchange method to assign assignment based on standard"""
        self.subject_standard_assignment = self.standard_id.standard_id.id

    @api.constrains("assign_date", "due_date")
    def check_date(self):
        """Method to check constraint of due date and assign date"""
        if self.due_date < self.assign_date:
            raise ValidationError(
                _(
                    """
                Due date of homework should be greater than assign date"""
                )
            )

    def active_assignment(self):
        """ This method change state as active state
            and create assignment line
            @return : True
        """
        assignment_obj = self.env["school.student.assignment"]
        student_obj = self.env["student.student"]
        ir_attachment_obj = self.env["ir.attachment"]
        for rec in self:
            student_recs = student_obj.search(
                [
                    ("standard_id", "=", rec.standard_id.id),
                    ("state", "=", "done"),
                ]
            )
            if not rec.attached_homework:
                raise ValidationError(_("""Please attach the homework!"""))
            for std in student_recs:
                ass_dict = {
                    "name": rec.name,
                    "subject_id": rec.subject_id.id,
                    "standard_id": rec.standard_id.id,
                    "assign_date": rec.assign_date,
                    "due_date": rec.due_date,
                    "state": "active",
                    "attached_homework": rec.attached_homework,
                    "teacher_id": rec.teacher_id.id,
                    "teacher_assignment_id": rec.id,
                    "student_id": std.id,
                    "stud_roll_no": std.roll_no,
                    "student_standard": std.standard_id.standard_id.id,
                    "submission_type": self.type_submission,
                    "attachfile_format": self.file_format.name,
                }
                assignment_rec = assignment_obj.create(ass_dict)
                attach = {
                    "name": "test",
                    "datas": rec.attached_homework,
                    "description": "Assignment attachment",
                    "res_model": "school.student.assignment",
                    "res_id": assignment_rec.id,
                }
                ir_attachment_obj.create(attach)
            rec.state = "active"

    def done_assignments(self):
        """Changes the state to done"""
        self.state = "done"

    def unlink(self):
        """Inherited unlink method to give warning on record deletion"""
        for rec in self:
            if rec.state != "draft":
                raise ValidationError(
                    _(
                        """
                    Confirmed assignment can not be deleted!"""
                    )
                )
        return super(SchoolTeacherAssignment, self).unlink()


class SchoolStudentAssignment(models.Model):
    """Defining Model for Student Assignment Information."""

    _name = "school.student.assignment"
    _description = "Student Assignment Information"

    name = fields.Char("Assignment Name", help="Assignment Name")
    subject_id = fields.Many2one(
        "subject.subject", "Subject", required=True, help="Select Subject"
    )
    standard_id = fields.Many2one(
        "school.standard", "Class", required=True, help="Select Standard"
    )
    rejection_reason = fields.Text("Reject Reason", help="Reject Reason")
    teacher_id = fields.Many2one(
        "school.teacher",
        "Teacher",
        required=True,
        help="""Teacher responsible to assign
                                 assignment""",
    )
    assign_date = fields.Date(
        "Assign Date", required=True, help="Starting date of assignment"
    )
    due_date = fields.Date(
        "Due Date", required=True, help="End date of assignment"
    )
    state = fields.Selection(
        [
            ("draft", "Draft"),
            ("active", "Active"),
            ("reject", "Reject"),
            ("done", "Done"),
        ],
        "Status",
        default="draft",
        help="States of assignment",
    )
    student_id = fields.Many2one(
        "student.student", "Student", required=True, help="Name of Student"
    )
    stud_roll_no = fields.Integer(string="Roll no", help="Roll No of student")
    attached_homework = fields.Binary(
        "Attached Home work", help="Homework Attached by student"
    )
    teacher_assignment_id = fields.Many2one(
        "school.teacher.assignment",
        string="Teachers",
        help="Teacher assigments",
    )
    student_standard = fields.Many2one(
        "standard.standard", "Student Standard", help="Select student standard"
    )
    submission_type = fields.Selection(
        [("hardcopy", "Hardcopy(Paperwork)"), ("softcopy", "Softcopy")],
        default="hardcopy",
        string="Submission Type",
        help="Select assignment type",
    )
    attachfile_format = fields.Char(
        "Submission Fileformat", help="Enter assignment fileformat"
    )
    submit_assign = fields.Binary(
        "Submit Assignment", help="Attach assignment here"
    )
    file_name = fields.Char("File Name", help="Enter file name")
    active = fields.Boolean(
        "Active", default=True, help="Activate/Deactivate assignment"
    )

    @api.constrains("assign_date", "due_date")
    def check_date(self):
        """Method to check constraint of due date
        and assign date for homework"""
        if self.due_date < self.assign_date:
            raise ValidationError(
                _(
                    """
                Due date of homework should be greater than Assign date!"""
                )
            )

    @api.constrains("submit_assign", "file_name")
    def check_file_format(self):
        if self.file_name:
            file_format = self.file_name.split(".")
            if len(file_format) == 2:
                file_format = file_format[1]
            else:
                raise ValidationError(
                    _(
                        """Kindly attach file with format: %s!
                """
                    )
                    % self.attachfile_format
                )
            if (
                file_format in self.attachfile_format
                or self.attachfile_format in file_format
            ):
                return True
            raise ValidationError(
                _(
                    """
            Kindly attach file with format: %s!"""
                )
                % self.attachfile_format
            )

    @api.onchange("student_id")
    def onchange_student_standard(self):
        """Method to get standard of selected student"""
        self.student_standard = self.student_id.standard_id.standard_id.id

    def active_assignment(self):
        """This method change state as active"""
        if not self.attached_homework:
            raise ValidationError(_("""Kindly attach homework!"""))
        self.state = "active"

    def done_assignment(self):
        """ This method change state as done
            for school student assignment
            @return : True
        """
        if self.submission_type == "softcopy" and not self.submit_assign:
            raise ValidationError(
                _(
                    """You have not attached the homework!
Please attach the homework!"""
                )
            )
        self.state = "done"

    def reassign_assignment(self):
        """This method change state as active"""
        self.ensure_one()
        self.state = "active"

    def unlink(self):
        """Inherited unlink method to give warning on record deletion"""
        for rec in self:
            if rec.state != "draft":
                raise ValidationError(
                    _(
                        """
                        Confirmed assignment can not be deleted!"""
                    )
                )
        return super(SchoolStudentAssignment, self).unlink()


class FileFormat(models.Model):
    """Defining Model for File Format Details."""

    _name = "file.format"
    _description = "File Format Details"

    name = fields.Char("Name", help="Enter file format that can be attached")


class StudentAssign(models.Model):
    _inherit = "student.student"

    def set_alumni(self):
        """Override method to make student assignment active false when
        student is alumni"""
        student_assign_obj = self.env["school.student.assignment"]
        for rec in self:
            student_assign = student_assign_obj.search(
                [("student_id", "=", rec.id)]
            )
            if student_assign:
                student_assign.active = False
        return super(StudentAssign, self).set_alumni()
