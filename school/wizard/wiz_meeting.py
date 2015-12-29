# -*- coding: utf-8 -*-
# Part of Odoo. See LICENSE file for full copyright and licensing details.

from openerp import models, fields, api, _
from openerp.exceptions import except_orm


class StudentMeeting(models.TransientModel):
    _name = "student.meeting"

    name = fields.Char('Meeting Subject', size=128, required=True)
    meeting_date = fields.Datetime('Meeting Date', required=True)
    deadline = fields.Datetime('Deadline', required=True)
    description = fields.Text('Description')

    @api.multi
    def set_meeting(self):
        context = dict(self._context)
        if context is None:
            context = {}
        student_obj = self.env['student.student']
        cal_event_obj = self.env['calendar.event']
        for rec in self:
            attendee_ids = []
            flag = False
            error_student = ''
            for student in student_obj.browse(context.get('active_ids', [])):
                if not student.email:
                    flag = True
                    error_student = "\n"
                    error_student += student.pid + " : " + student.name\
                                      + " "\
                                      + student.middle + " " + student.last
                else:
                    attendee_ids.append((0, 0, {'user_id': student.user_id.id,
                                                'email': student.email}))
            if flag:
                raise except_orm(_('Error !'),
                                 _('Following Student'
                                   'does not have Email ID.\n\n'
                                   + error_student
                                   + '\nMeeting cannot be scheduled.'))
            cal_event_obj.create({'name': rec.name,
                                  'start': rec.meeting_date,
                                  'stop': rec.deadline,
                                  'description': rec.description,
                                  'attendee_ids': attendee_ids})
        return {'type': 'ir.actions.act_window_close'}
