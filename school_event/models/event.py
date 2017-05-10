# -*- coding: utf-8 -*-
# See LICENSE file for full copyright and licensing details.

import time
from odoo import models, fields, api, _
from odoo.exceptions import Warning as UserError


class BoardBoard(models.AbstractModel):
    _inherit = "board.board"


class SchoolStandard(models.Model):
    _name = 'school.standard'
    _inherit = 'school.standard'
    _rec_name = 'event_ids'

    event_ids = fields.Many2many('school.event', 'school_standard_event_rel',
                                 'event_id', 'standard_id', 'Events',
                                 readonly=True)


class SchoolEventParameter(models.Model):
    '''for event parameter based on which score will given'''
    _name = 'school.event.parameter'
    _description = 'Event Parameter'

    name = fields.Char('Parameter Name', required=True)


class SchoolEventParticipant(models.Model):
    '''for Participant which are participated in events'''
    _name = 'school.event.participant'
    _description = 'Participant Information'
    _order = "sequence"

    name = fields.Many2one('student.student', 'Participant Name',
                           readonly=True)
    score = fields.Float('Score', default=0)
    event_id = fields.Many2one('school.event', 'Event', readonly=True)
    stu_pid = fields.Char('Personal Identification Number', required=True,
                          readonly=True)
    win_parameter_id = fields.Many2one('school.event.parameter', 'Parameter',
                                       readonly=True)
    sequence = fields.Integer('Rank', help="The sequence field is used to Give\
                               Rank to the Participant", default=0)


class SchoolEvent(models.Model):
    '''for events'''
    _name = 'school.event'
    _description = 'Event Information'
    _rec_name = 'name'

    @api.depends('part_ids')
    def _compute_participants(self):
        for rec in self:
            rec.participants = len(rec.part_ids)

    name = fields.Char('Event Name', help="Full Name of the event")
    event_type = fields.Selection([('intra', 'IntraSchool'),
                                  ('inter', 'InterSchool')],
                                  'Event Type',
                                  help='Event is either IntraSchool\
                                        or InterSchool')
    start_date = fields.Date('Start Date', help="Event Starting Date")
    end_date = fields.Date('End Date', help="Event Ending Date")
    start_reg_date = fields.Date('Start Registration Date',
                                 help="Event registration starting date")
    last_reg_date = fields.Date('Last Registration Date',
                                help="Last Date of registration")
    contact_per_id = fields.Many2one('hr.employee', 'Contact Person',
                                     help="Event contact person")
    supervisor_id = fields.Many2one('hr.employee', 'Supervisor',
                                    help="Event Supervisor Name")
    parameter_id = fields.Many2one('school.event.parameter', 'Parameter',
                                   help="Parameters of the Event\
                                         like (Goal, Point)")
    maximum_participants = fields.Integer('Maximum Participants',
                                          help='Maximum Participant\
                                                of the Event')
    participants = fields.Integer(compute='_compute_participants',
                                  string='Participants', readonly=True)
    part_standard_ids = fields.Many2many('school.standard',
                                         'school_standard_event_rel',
                                         'standard_id', 'event_id',
                                         'Participant Standards',
                                         help="The Participant is from\
                                               which standard")
    state = fields.Selection([('draft', 'Draft'), ('open', 'Running'),
                              ('close', 'Close'), ('cancel', 'Cancel')],
                             string='State', readonly=True, default='draft')
    part_ids = fields.Many2many('school.event.participant',
                                'event_participants_rel', 'participant_id',
                                'event_id', 'Participants', readonly=True,
                                order_by='score')
    code = fields.Many2one('school.school', 'Organizer School',
                           help='Event Organized School')
    is_holiday = fields.Boolean('Is Holiday(s)',
                                help='Checked if the event is organized\
                                      on holiday.')
    color = fields.Integer('Color Index', default=0)

    @api.constrains('start_date', 'end_date')
    def _check_dates(self):

        sedt = self.start_date > self.end_date
        if (self.start_date and self.end_date and sedt):
            raise UserError(_('Error! Event start-date must be lower\
                              then Event end-date.'))

    @api.constrains('start_date', 'end_date', 'start_reg_date',
                    'last_reg_date')
    def _check_all_dates(self):

        dt = self.start_reg_date and self.last_reg_date
        if (self.start_date and self.end_date and dt):

            if self.start_reg_date > self.last_reg_date:
                raise UserError(_('Error! Event Registration StartDate must be\
                                  lower than Event Registration end-date.'))
            elif self.last_reg_date >= self.start_date:
                raise UserError(_('Error! Event Registration last-date must be\
                                    lower than Event start-date.'))

    @api.model
    def search(self, args, offset=0, limit=None, order=None, count=False):

        if self._context.get('part_name_id'):
            student_obj = self.env['student.student']
            data = student_obj.browse(self._context.get('part_name_id'))
            arg_domain = ('part_standard_ids', 'in', [data.class_id.id])
            args.append(arg_domain)
        return super(SchoolEvent, self).search(args, offset, limit, order,
                                               count=count)

    @api.multi
    def event_open(self):

        if self.part_ids and self.part_ids[0].id:
            self.write({'state': 'open'})
        else:
            raise UserError(_('No Participants ! \
                             No Participants to open the Event.'))

    @api.multi
    def event_close(self):
        self.write({'state': 'close'})
        return True

    @api.multi
    def event_draft(self):
        self.write({'state': 'draft'})
        return True

    @api.multi
    def event_cancel(self):
        self.write({'state': 'cancel'})
        return True


class SchoolEventRegistration(models.Model):
    '''for registration by students for events'''
    _name = 'school.event.registration'
    _description = 'Event Registration'

    name = fields.Many2one('school.event', 'Event Name',
                           domain=[('state', '=', 'draft')], required=True)
    part_name_id = fields.Many2one('student.student', 'Participant Name',
                                   required=True)
    reg_date = fields.Date('Registration Date', readonly=True,
                           default=lambda *a:
                           time.strftime("%Y-%m-%d %H:%M:%S"))
    state = fields.Selection([('draft', 'Draft'),
                              ('confirm', 'Confirm'),
                              ('cancel', 'Cancel')], 'State', readonly=True,
                             default='draft')
    is_holiday = fields.Boolean('Is Holiday(s)', help='Checked if the event is\
                                                    organized on holiday.')

    @api.multi
    def regi_cancel(self):
        event_obj = self.env['school.event']
        student_obj = self.env['student.student']
        event_part_obj = self.env['school.event.participant']
        self.write({'state': 'cancel'})

        for reg_data in self:
            event_data = event_obj.browse(reg_data.name.id)
            prt_data = student_obj.browse(reg_data.part_name_id.id)
            # delete entry of participant
            domain = [('stu_pid', '=', prt_data.pid),
                      ('event_id', '=', reg_data.name.id),
                      ('name', '=', reg_data.part_name_id.id)]
            stu_prt_data = event_part_obj.search(domain)
            stu_prt_data.sudo().unlink()
            # remove entry of event from student
            list1 = []

            for part in prt_data.event_ids:
                part = student_obj.browse(part.id)
                list1.append(part.id)
            flag = True

            for part in list1:
                data = event_part_obj.browse(part)
                if data.event_id.id == reg_data.name.id:
                    flag = False

            if not flag:
                list1.remove(part)
            stu_part_id = student_obj.browse(reg_data.part_name_id.id)
            stu_part_id.sudo().write({'event_ids': [(6, 0, list1)]})
            list1 = []
            # remove entry of participant from event
            flag = True

            for par in event_data.part_ids:
                part = event_part_obj.browse(par.id)
                list1.append(part.id)

            for par in list1:
                data = event_part_obj.browse(par)

                if data.name.id == reg_data.part_name_id.id:
                    parii = par
                    flag = False

            if not flag:
                list1.remove(parii)
            participants = int(event_data.participants) - 1
            event_reg_id = event_obj.browse(reg_data.name.id)
            event_reg_id.sudo().write({'part_ids': [(6, 0, list1)],
                                       'participants': participants})
        return True

    @api.multi
    def regi_confirm(self):
        self.write({'state': 'confirm'})
        event_obj = self.env['school.event']
        student_obj = self.env['student.student']
        event_part_obj = self.env['school.event.participant']

        for reg_data in self:
            event_data = event_obj.browse(reg_data.name.id)
            prt_data = student_obj.browse(reg_data.part_name_id.id)
            participants = int(event_data.participants) + 1

            # check participation is full or not.
            if participants > event_data.maximum_participants:
                raise UserError(_('Error ! \
                                 Participation in this Event is Full.'))

            # check last registration date is over or not
            if reg_data.reg_date > event_data.last_reg_date:
                raise UserError(_('Error ! Last Registration date is over \
                                   for this Event.'))
            # make entry in participant
            val = {'stu_pid': str(prt_data.pid),
                   'score': 0,
                   'win_parameter_id': event_data.parameter_id.id,
                   'event_id': reg_data.name.id,
                   'name': reg_data.part_name_id.id}
            temp = event_part_obj.sudo().create(val)
            # make entry of event in student
            list1 = []

            for evt in prt_data.event_ids:
                part = student_obj.browse(evt.id)
                list1.append(part.id)
            flag = True

            for evt in list1:
                data = event_part_obj.browse(evt)
                if data.event_id.id == reg_data.name.id:
                    flag = False

            if flag:
                list1.append(temp.id)
            stu_part_id = student_obj.browse(reg_data.part_name_id.id)
            stu_part_id.sudo().write({'event_ids': [(6, 0, list1)]})
            # make entry of participant in event
            list1 = []
            flag = True

            for evt in event_data.part_ids:
                part = event_part_obj.browse(evt.id)
                list1.append(part.id)

            for evt in list1:
                data = event_part_obj.browse(evt)
                if data.name.id == reg_data.part_name_id.id:
                    flag = False

            if flag:
                list1.append(temp.id)
            evnt_reg_id = event_obj.browse(reg_data.name.id)
            evnt_reg_id.sudo().write({'part_ids': [(6, 0, list1)]})
        return True


class StudentStudent(models.Model):
    _name = 'student.student'
    _inherit = 'student.student'
    _description = 'Student Information'

    event_ids = fields.Many2many('school.event.participant',
                                 'event_participant_student_rel', 'event_id',
                                 'stu_id', 'Events', readonly=True)

    @api.model
    def search(self, args, offset=0, limit=None, order=None, count=False):
        if self._context.get('name'):
            event_obj = self.env['school.event']
            event_data = event_obj.browse(self._context['name'])
            std_ids = [std_id.id for std_id in event_data.part_standard_ids]
            args.append(('standard_id', 'in', std_ids))
        return super(StudentStudent, self).search(args, offset, limit, order,
                                                  count=count)
