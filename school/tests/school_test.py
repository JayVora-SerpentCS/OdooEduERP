# -*- coding: utf-8 -*-
# Part of Odoo. See LICENSE file for full copyright and licensing details.

from openerp.tests import common


class SchoolTest(common.TransactionCase):

    def setUp(self):
        super(SchoolTest, self).setUp()

        self.student_student = self.env['student.student']

    def _create_user(self):
        """Create a user."""
        user = self.student_student.create({
            'name': 'Ram',
            'middle': 'A',
            'last': 'Shah',
            'date_of_birth': '06/02/2017',
        })
        return user
