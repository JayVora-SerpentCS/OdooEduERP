# -*- coding: utf-8 -*-
# See LICENSE file for full copyright and licensing details.

from odoo.tests import common


class TestTimetable(common.TransactionCase):

    def setUp(self):
        super(TestTimetable, self).setUp()
        self.time_table_obj = self.env['time.table']
        self.time_table_line_obj = self.env['time.table.line']
        self.stander_id = self.env.ref('school.demo_standard_standard_2')
        self.year_id = self.env.ref('school.demo_academic_year_1')
        self.subject_id = self.env.ref('school.demo_subject_subject_2')
        self.teacher_id = self.env.ref('school.demo_school_teacher_1')
        self.table_id = self.env.ref('timetable.time_table_firsts0')
        self.room_id = self.env.ref('school.class_room15')
#       Create time-table
        self.time_table = self.time_table_obj.\
            create({'name': 'Test Timetable',
                    'standard_id': self.stander_id.id,
                    'year_id': self.year_id.id,
                    'timetable_type': 'regular',
                    })
#       Create timetable line
        self.time_table_line = self.time_table_line_obj.\
            create({'week_day': 'monday',
                    'teacher_id': self.teacher_id.id,
                    'subject_id': self.subject_id.id,
                    'start_time': '17.0',
                    'end_time': '18.0',
                    'table_id': self.time_table.id,
                    'class_room_id': self.room_id.id
                    })

    def test_timetable(self):
        self.assertIn(self.subject_id, self.teacher_id.subject_id)
