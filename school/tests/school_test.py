from openerp.tests import common


class SchoolTest(common.TransactionCase):

    def setUp(self):
        super(SchoolTest, self).setUp()

        self.student_student = self.env['student.student']
        print "self.student_student", self.student_student

    def _create_user(self):
        """Create a user."""
        user = self.student_student.create({
            'name': 'Krishna',
            'middle': 'N',
            'last': 'Prajapati',
            'date_of_birth': '06/02/2017',
        })
        print "user::::", user
        return user

    def test_security(self):
        print "Done..........."
