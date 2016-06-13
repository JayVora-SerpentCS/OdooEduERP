# -*- coding: utf-8 -*-
##############################################################################
#
#    OpenERP, Open Source Management Solution
#    Copyright (C) 2004-2009 Tiny SPRL (<http://tiny.be>).
#    Copyright (C) 2011-Today Serpent Consulting Services PVT. LTD.
#    (<http://www.serpentcs.com>)
#    This program is free software: you can redistribute it and/or modify
#    it under the terms of the GNU Affero General Public License as
#    published by the Free Software Foundation, either version 3 of the
#    License, or (at your option) any later version.
#
#    This program is distributed in the hope that it will be useful,
#    but WITHOUT ANY WARRANTY; without even the implied warranty of
#    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#    GNU Affero General Public License for more details.
#
#    You should have received a copy of the GNU Affero General Public License
#    along with this program.  If not, see <http://www.gnu.org/licenses/>.
#
##############################################################################
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
        cur_rec = self.browse(self.id)
        student_obj = self.env['student.student']
        cal_event_obj = self.env['calendar.event']
        attendee_ids = []
        flag = False
        error_student = ''
        for student in student_obj.browse(self._context['active_ids']):
            if not student.email:
                flag = True
                error_student += (student.pid + " : " + student.name + " " +
                                  student.middle + " " + student.last + "\n")
            else:
                attendee_ids.append((0, 0, {'user_id': student.user_id.id,
                                    'email': student.email}))
        if flag:
            raise except_orm(_('Error !'), _("Following Student don't have \
                             Email ID.\n\n" + error_student + "\nMeeting \
                             cannot be scheduled."))
        cal_event_obj.create({
            'name': cur_rec.name,
            'start': cur_rec.meeting_date,
            'stop': cur_rec.deadline,
            'description': cur_rec.description,
            'attendee_ids': attendee_ids
        })
        return {'type': 'ir.actions.act_window_close'}
