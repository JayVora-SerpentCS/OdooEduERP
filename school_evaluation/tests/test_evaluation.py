# See LICENSE file for full copyright and licensing details.

from datetime import datetime

from odoo.tests import common


class TestEvaluation(common.TransactionCase):
    def setUp(self):
        super(TestEvaluation, self).setUp()
        self.rating_obj = self.env["rating.rating"]
        self.evaluation_template_obj = self.env["school.evaluation.template"]
        self.school_evaluation_obj = self.env["school.evaluation"]
        self.evaluation_line_obj = self.env["school.evaluation.line"]
        self.teacher = self.env.ref("school.demo_school_teacher_1")
        self.student = self.env.ref("school.demo_student_student_5")
        #        Create School Evaluation Template For Teacher
        self.evaluation_template_faculty = self.evaluation_template_obj.create(
            {
                "desc": "Communication with students and other activity",
                "type": "faculty",
            }
        )
        #       Create Rating of above template
        self.rating_faculty = self.rating_obj.create(
            {
                "rating": 5,
                "feedback": "Excellent",
                "res_id": self.evaluation_template_faculty.id,
            }
        )
        # self.rating_obj._find_parent_data()
        #        Create School Evaluation For The School Teachers
        current_date = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        self.teacher_evalution = self.school_evaluation_obj.create(
            {
                "type": "faculty",
                "teacher_id": self.teacher.id,
                "date": current_date,
            }
        )
        self.teacher_evalution.get_record()
        self.teacher_evalution._compute_total_points()
        self.teacher_evalution.set_start()
        self.teacher_evalution.eval_line_ids.write(
            {
                "point_id": self.rating_faculty.id,
            }
        )
        self.teacher_evalution.eval_line_ids.onchange_point()
        self.teacher_evalution.set_finish()
        self.teacher_evalution.set_cancel()
        self.teacher_evalution.set_draft()

        # Create School Evaluation Template For Student
        self.evaluation_template_student = self.evaluation_template_obj.create(
            {
                "desc": "Communication of Information",
                "type": "student",
            }
        )
        # Create Rating of above template
        self.rating_student = self.rating_obj.create(
            {
                "rating": 5,
                "feedback": "Excellent",
                "res_id": self.evaluation_template_student.id,
            }
        )
        # Create School Evaluation For The School Student
        self.student_evalution = self.school_evaluation_obj.create(
            {
                "type": "student",
                "student_id": self.student.id,
                "date": current_date,
            }
        )
        self.student_evalution.get_record()
        self.student_evalution._compute_total_points()
        self.student_evalution.set_start()
        self.student_evalution.eval_line_ids.write(
            {
                "point_id": self.rating_student.id,
            }
        )
        self.student_evalution.eval_line_ids.onchange_point()
        self.student_evalution.set_finish()
        self.student_evalution.set_cancel()
        self.student_evalution.set_draft()

    def test_evaluation(self):
        self.assertEqual(self.student.state, "done")
        self.assertEqual(self.rating_student.res_id, self.evaluation_template_student.id)
