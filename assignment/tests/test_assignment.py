# See LICENSE file for full copyright and licensing details.

from dateutil.relativedelta import relativedelta as rd

from odoo import fields
from odoo.tests import common


class TestAssignment(common.TransactionCase):
    def setUp(self):
        super(TestAssignment, self).setUp()
        self.teacher_assignment_obj = self.env["school.teacher.assignment"]
        self.student_assignment_obj = self.env["school.student.assignment"]
        self.file_formatobj = self.env["file.format"]
        self.teacher_id = self.env.ref("school.demo_school_teacher_1")
        self.subject_id = self.env.ref("school.demo_subject_subject_3")
        self.standard_std = self.env.ref("school.demo_standard_standard_1")
        self.standard = self.env.ref("school.demo_school_standard_1")
        self.student = self.env.ref("school.demo_student_student_5")
        self.standard_id = self.env.ref("school.demo_school_standard_2")
        self.standard_std2 = self.env.ref("school.demo_standard_standard_2")
        current_date = fields.Datetime.today()
        assign_date = current_date + rd(days=3)
        assign = assign_date
        due_date = current_date + rd(days=4)
        end_date = due_date
        # Create File format
        self.file_format = self.file_formatobj.create({"name": "pdf"})
        #        Create Student Assignment
        self.student_assign = self.student_assignment_obj.create(
            {
                "student_id": self.student.id,
                "teacher_id": self.teacher_id.id,
                "subject_id": self.subject_id.id,
                "standard_id": self.standard.id,
                "assign_date": assign,
                "due_date": end_date,
                "submission_type": "hardcopy",
            }
        )
        self.student_assign.check_date()
        self.student_assign.onchange_student_standard()
        # Create Teacher Assignment
        self.school_teacher_assignment = self.teacher_assignment_obj.create(
            {
                "name": "Test Product Packaging",
                "teacher_id": self.teacher_id.id,
                "subject_id": self.subject_id.id,
                "standard_id": self.standard.id,
                "assign_date": assign,
                "due_date": end_date,
                "type_submission": "hardcopy",
            }
        )
        self.school_teacher_assignment.onchange_subject_standard()

    def test_assignment(self):
        student_assign_ids = self.school_teacher_assignment.student_assign_ids
        for student in student_assign_ids:
            student.done_assignment()
            self.assertEqual("done", student.state)
