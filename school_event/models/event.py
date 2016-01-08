# -*- coding: utf-8 -*-
# Part of Odoo. See LICENSE file for full copyright and licensing details.

import time
from openerp import models, fields, api, _
from openerp.exceptions import except_orm, Warning as UserError


class BoardBoard(models.Model):
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
    sequence = fields.Integer('Rank', help="The sequence field is \
                               used to Give Rank to the Participant",
                               default=0)
    registration_id = fields.Many2one('school.event.registration',
                                      'Registration')


class SchoolEvent(models.Model):
    '''for events'''
    _name = 'school.event'
    _description = 'Event Information'
    _rec_name = 'name'

    @api.one
    @api.depends('part_ids')
    def _participants(self):
        self.participants = len(self.part_ids)

    name = fields.Char('Event Name', help="Full Name of the event")
    event_type = fields.Selection([('intra', 'IntraSchool'),
                                  ('inter', 'InterSchool')],
                                  'Event Type',
                                  help='Event is either IntraSchool\
                                        or InterSchool')
    start_date = fields.Date('Event Start Date', help="Event Starting Date")
    end_date = fields.Date('Event End Date', help="Event Ending Date")
    start_reg_date = fields.Date('Registration Start Date',
                                 help="Event registration starting date")
    last_reg_date = fields.Date('Registration End Date',
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
    participants = fields.Integer(compute='_participants',
                                  string='Participants', readonly=True)
    part_standard_ids = fields.Many2many('school.standard',
                                         'school_standard_event_rel',
                                         'standard_id', 'event_id',
                                         'Participant Standards',
                                         help="The Participant is from\
                                               which standard")
    state = fields.Selection([('draft', 'Draft'), 
                              ('reg_start', 'Registration Started'),
                              ('reg_end', 'Registration Closed'),
                              ('open', 'Running'),
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

    @api.constrains('start_date', 'end_date', 'start_reg_date',
                    'last_reg_date')
    def _check_all_dates(self):
        if (self.start_date
                and self.end_date
                and self.start_date > self.end_date):
            raise UserError(_('Error! Event start-date must be lower\
                             then Event end-date.'))

        if (self.start_date
                and self.end_date
                and self.start_reg_date
                and self.last_reg_date):

            if self.start_reg_date > self.last_reg_date:
                raise UserError(_('Error! Event Registration StartDate must\
                                be lower than Event Registration end-date.'))
            elif self.last_reg_date >= self.start_date:
                raise UserError(_('Error! Event Registration last-date must\
                                be lower than Event start-date.'))

    @api.model
    def search(self, args, offset=0, limit=None, order=None, count=False):
        context = dict(self._context)
        if context is None:
            context = {}
        if args is None:
            args = []
        if context.get('part_name_id', False):
            student_obj = self.env['student.student']
            data = student_obj.browse(self._context.get('part_name_id'))
            if data and data.class_id:
                args.append(('part_standard_ids', 'in', [data.class_id.id]))
        return super(SchoolEvent, self).search(args, offset, limit, order,
                                               count=count)

    @api.multi
    def registration_open(self):
        return self.write({'state': 'reg_start'})
    
    @api.multi
    def registration_closed(self):
        return self.write({'state' : 'reg_end'})

    @api.multi
    def event_open(self):
        return self.write({'state' : 'open'})

    @api.multi
    def event_close(self):
        return self.write({'state': 'close'})

    @api.multi
    def event_draft(self):
        return self.write({'state': 'draft'})

    @api.multi
    def event_cancel(self):
        return self.write({'state': 'cancel'})


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
    is_holiday = fields.Boolean('Is Holiday', help='Checked if the event is\
                                                    organized on holiday.')

    @api.multi
    def regi_cancel(self):
        event_part_obj = self.env['school.event.participant']

        for reg_data in self:
            domain = [('stu_pid', '=', reg_data.part_name_id.pid),
                      ('event_id', '=', reg_data.name.id),
                      ('name', '=', reg_data.part_name_id.id),
                      ('registration_id', '=', reg_data.id)]
            stu_prt_data = event_part_obj.search(domain)
            stu_prt_data.unlink()
        return self.write({'state': 'cancel'})

    @api.multi
    def regi_confirm(self):
        event_part_obj = self.env['school.event.participant']

        for reg_data in self:
            participants = len(reg_data.name.part_ids) + 1

            # check participation is full or not.
            if participants > reg_data.name.maximum_participants:
                raise except_orm(_('Error !'),
                                 _('Participation in this Event is Full.'))

            # check last registration date is over or not
            if reg_data.reg_date > reg_data.name.last_reg_date:
                raise except_orm(_('Error !'),
                                 _('Last Registration date is over'
                                   'for this Event.'))
            # make entry in participant
            val = {'stu_pid': str(reg_data.part_name_id.pid),
                   'score': 0,
                   'win_parameter_id': reg_data.name.parameter_id.id,
                   'event_id': reg_data.name.id,
                   'registration_id' : reg_data.id,
                   'name': reg_data.part_name_id.id}
            part_id = event_part_obj.create(val)
            part_ids = [part.id for part in reg_data.name.part_ids]
            part_ids.append(part_id.id)
            reg_data.name.write({'part_ids': [(6, 0, part_ids)]})
            event_ids = [event.id for event in \
                         reg_data.part_name_id.event_ids]
            event_ids.append(part_id.id)
            reg_data.part_name_id.write({'event_ids' : [(6, 0, event_ids)]})
        return self.write({'state': 'confirm'})


class StudentStudent(models.Model):
    _name = 'student.student'
    _inherit = 'student.student'
    _description = 'Student Information'

    event_ids = fields.Many2many('school.event.participant',
                                 'event_participant_student_rel', 'event_id',
                                 'stu_id', 'Events', readonly=True)

    @api.model
    def search(self, args, offset=0, limit=None, order=None, count=False):
        context = dict(self._context)
        if context is None:
            context = {}
        if context.get('name', False):
            event_data = self.env['school.event'].browse(context['name'])
            std_ids = [std_id.id for std_id in event_data.part_standard_ids]
            if std_ids:
                args.append(('standard_id', 'in', std_ids))
        return super(StudentStudent, self).search(args, offset, limit, order,
                                                  count=count)

    @api.model
    def name_search(self, name, args=None, operator='ilike', limit=100):
        context = self._context and dict(self._context) or {}
        args = args or []
        if context.get('name', False):
            event_data = self.env['school.event'].browse(context['name'])
            std_ids = [std_id.id for std_id in event_data.part_standard_ids]
            args.append(('standard_id', 'in', std_ids))
        return super(StudentStudent, self).name_search(name, args=args, \
                                                       operator='ilike', \
                                                       limit=limit)
