from openerp.tests import common


class AssignmentTest(common.TransactionCase):

    def setUp(self):
        super(AssignmentTest, self).setUp()
        print "\n\nEnter TestCases"

        # ENVIRONMENTS
        self.student_student = self.env['student.student']
        self.school_student_assignment = self.env['school.student.assignment']
        print "self.student_student ::::::::", self.student_student
        # INSTANCES
        self.assignment = self.env.ref('assignment.action_school_student_assignment_form_btn')
        print "self.assignment::::::", self.assignment

        self.res_users_model = self.env['res.users']
        self.partner_model = self.env['res.partner']
        self.company = self.env.ref('base.main_company')
        self.partner1 = self.env.ref('base.res_partner_1')

        print "self.res_users_model", self.res_users_model
        print "self.company  ::::", self.company
        print "self.partner1 :::::", self.partner1

    def test_security(self):
        print "Done"
