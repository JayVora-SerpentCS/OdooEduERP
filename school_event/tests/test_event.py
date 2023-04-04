# See LICENSE file for full copyright and licensing details.

from datetime import datetime

from dateutil.relativedelta import relativedelta as rd

from odoo.tests import common


class TestEvent(common.TransactionCase):
    def setUp(self):
        super(TestEvent, self).setUp()
        self.school_event_obj = self.env["event.event"]
        self.school_event_reg_obj = self.env["event.registration"]
        self.school_id = self.env.ref("school.demo_school_1")
        self.teacher = self.env.ref("school.demo_school_teacher_1")
        self.part_name = self.env.ref("school.demo_student_student_5")
        self.standard = self.env.ref("school.demo_standard_standard_2")
        currdt = datetime.now()
        event_start = currdt + rd(days=15)
        eve_start = datetime.strftime(event_start, "%Y-%m-%d")
        event_end = currdt + rd(days=20)
        eve_end = datetime.strftime(event_end, "%Y-%m-%d")
        # Create school event
        self.school_event = self.school_event_obj.create(
            {
                "name": "New Event",
                "date_begin": eve_start,
                "date_end": eve_end,
                "employee_id": self.teacher.id,
                "part_standard_ids": [(6, 0, (self.standard.ids))],
            }
        )
        self.school_event._check_closing_date()
        self.school_event.update(
            {"stage_id": self.env.ref("event.event_stage_announced").id}
        )
        # Create event registration
        self.school_event_reg = self.school_event_reg_obj.create(
            {
                "part_name_id": self.part_name.id,
                "event_id": self.school_event.id,
            }
        )
        self.school_event_reg.onchange_student_standard()
        self.school_event_reg.action_cancel()
        self.school_event_reg.action_set_draft()
        self.school_event_reg.action_confirm()

    def test_exam(self):
        self.assertEqual(self.school_event_reg.part_name_id.state, "done")
