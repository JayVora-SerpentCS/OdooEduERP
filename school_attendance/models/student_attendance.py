from odoo import api, fields, models


class StudentStudent(models.Model):
    _inherit = 'student.student'

    employee_id = fields.Many2one('hr.employee', 'Student Name',
                                  ondelete="cascade",
                                  delegate=True, required=True,
                                  help='Enter related employee')

    @api.onchange("employee_id")
    def _onchange_employee_id(self):
        self.employee_id.is_student = True

class HrEmployeePrivate(models.Model):
    _inherit = "hr.employee"

    student_id = fields.Many2one("student.student", "Student")
    is_student = fields.Boolean('Is student',
                                help="Whether employee is student or not")

