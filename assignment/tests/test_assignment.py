from openerp.tests import common


class AssignmentTest(common.TransactionCase):

    def setUp(self):
        super(AssignmentTest, self).setUp()

        # ENVIRONMENTS
        self.student_student = self.env['student.student']
        self.school_student_assignment = self.env['school.student.assignment']

        self.assignment = self.env.ref('assignment.action_school_student_assignment_form_btn')

        self.res_users_model = self.env['res.users']
        self.partner_model = self.env['res.partner']

    def test_security(self):
        print "Done"
