# -*- encoding: utf-8 -*-
##############################################################################
#
#    OpenERP, Open Source Management Solution
#    Copyright (C) 2004-2009 Tiny SPRL (<http://tiny.be>).
#    Copyright (C) 2011-2012 Serpent Consulting Services
#    (<http://www.serpentcs.com>)
#    Copyright (C) 2013-2014 Serpent Consulting Services
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
import time
from openerp.exceptions import except_orm, Warning


class school_standard(models.Model):

    _name = 'school.standard'
    _inherit = 'school.standard'
    _rec_name = 'event_ids'

    event_ids = fields.Many2many('school.event', 'school_standard_event_rel',
                                 'event_id', 'standard_id', 'Events',
                                 readonly=True)


# Class for event parameter based on which score will given
class school_event_parameter(models.Model):

    _name = 'school.event.parameter'
    _description = 'Event Parameter'

    name = fields.Char('Parameter Name', required=True)


# class for Participant which are participeted in events
class school_event_participant(models.Model):

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
    sequence = fields.Integer('Rank', help="The sequence field is used to"
                              "Give Rank to the Participant", default=0)


# class for events
class school_event(models.Model):

    _name = 'school.event'
    _description = 'Event Information'
    _rec_name = 'name'

    @api.one
    def _participants(self):
        cnt = 0
        for rec_part_id in self.part_ids:
            cnt += 1
        self.participants = cnt

    name = fields.Char('Event Name', help="Full Name of the event")
    event_type = fields.Selection([('intra', 'Intra School'),
                                  ('inter', 'Inter School')],
                                  'Event Type', help='Event is either Intra'
                                  'chool or Inter school')
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
                                   help="Parameters of the Event"
                                   "like (Goal, Point)")
    maximum_participants = fields.Integer('Maximum Participants',
                                          help='Maximum Participant'
                                          'of the Event')
    participants = fields.Integer(compute='_participants',
                                  string='Participants', readonly=True)
    part_standard_ids = fields.Many2many('school.standard',
                                         'school_standard_event_rel',
                                         'standard_id', 'event_id',
                                         'Participant Standards',
                                         help="The Participant is"
                                         "from whcih standard")
    state = fields.Selection([('draft', 'Draft'), ('open', 'Running'),
                              ('close', 'Close'), ('cancel', 'Cancel')],
                             string='State', readonly=True, default='draft')
    part_ids = fields.Many2many('school.event.participant',
                                'event_participants_rel', 'participant_id',
                                'event_id', 'Participants', readonly=True,
                                order_by='score')
    code = fields.Char('Organiser School', help="Event Organised School")
    is_holiday = fields.Boolean('Is Holiday', help='Checked if the event'
                                'is organised on holiday.')
    color = fields.Integer('Color Index', default=0)

    @api.constrains('start_date', 'end_date')
    def _check_dates(self):
        for date_obj in self:
            if date_obj.start_date and date_obj.end_date and\
                    date_obj.start_date > date_obj.end_date:
                    raise Warning(_('Error! Event start-date must be lower'
                                    'then Event end-date.'))

    @api.constrains('start_date', 'end_date', 'start_reg_date',
                    'last_reg_date')
    def _check_all_dates(self):
        for all_date_obj in self:
            if all_date_obj.start_date and all_date_obj.end_date and\
                    all_date_obj.start_reg_date and all_date_obj.last_reg_date:
                    if all_date_obj.start_reg_date > all_date_obj.\
                            last_reg_date:
                            raise Warning(_('Error! Event Registration start-'
                                            'date must be lower than Event'
                                            'Registration end-date.'))
                    elif all_date_obj.last_reg_date >= all_date_obj.start_date:
                        raise Warning(_('Error! Event Registration last-date'
                                        'must be lower than Event'
                                        'start-date.'))

    @api.model
    def search(self, args, offset=0, limit=None, order=None, count=False):
        if self._context.get('part_name_id'):
            student_obj = self.env['student.student']
            student_data = student_obj.browse(self._context.get
                                              ('part_name_id'))
            args.append(('part_standard_ids', 'in',
                         [student_data.class_id.id]))
        return super(school_event, self).search(args, offset, limit, order,
                                                count=count)

    @api.multi
    def event_open(self):
        for event_open_obj in self:
            if event_open_obj.part_ids and event_open_obj.part_ids[0].id:
                event_open_obj.write({'state': 'open'})
            else:
                raise except_orm(_('No Participants !'), _('No Participants to'
                                                           'open the Event.'))

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


# class for registration by students for events
class school_event_registration(models.Model):

    _name = 'school.event.registration'
    _description = 'Event Registration'

    name = fields.Many2one('school.event', 'Event Name',
                           domain=[('state', '=', 'draft')], required=True)
    part_name_id = fields.Many2one('student.student', 'Participant Id',
                                   required=True)
    part_name = fields.Char(related="part_name_id.name",
                            string='participant name')
    reg_date = fields.Date('Registration Date', readonly=True,
                           default=lambda *a: time.strftime
                           ("%Y-%m-%d %H:%M:%S"))
    state = fields.Selection([('draft', 'Draft'),
                              ('confirm', 'Confirm'),
                              ('cancel', 'Cancel')
                              ], 'State', readonly=True, default='draft')
    is_holiday = fields.Boolean('Is Holiday', help='Checked if the event is'
                                'organised on holiday.')
    part_id = fields.Integer('Part Id')
    gr_no = fields.Char('Participant Id')

    @api.multi
    @api.onchange('part_name_id')
    def part_onchage(self):
        self.part_id = self.part_name_id.id
        self.gr_no = self.part_name_id.gr_no

    @api.multi
    def regi_cancel(self):
        event_obj = self.env['school.event']
        student_obj = self.env['student.student']
        event_part_obj = self.env['school.event.participant']
        self.write({'state': 'cancel'})
        for reg_data in self:
            event_data = event_obj.browse(reg_data.name.id)
            prt_data = student_obj.browse(reg_data.part_name_id.id)
            # delete etry of participant
            stu_prt_data = event_part_obj.search([('stu_pid', '=',
                                                   prt_data.pid),
                                                  ('event_id', '=',
                                                   reg_data.name.id),
                                                  ('name', '=',
                                                   reg_data.part_name_id.id)])
            stu_prt_data.unlink()
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
            if flag is False:
                list1.remove(part)
            stu_part_id = student_obj.browse(reg_data.part_name_id.id)
            stu_part_id.write({'event_ids': [(6, 0, list1)]})
            list1 = []

            # remove etry of participant from event
            flag = True
            for par in event_data.part_ids:
                part = event_part_obj.browse(par.id)
                list1.append(part.id)
            for par in list1:
                data = event_part_obj.browse(par)
                if data.name.id == reg_data.part_name_id.id:
                    parii = par
                    flag = False
            if flag is False:
                list1.remove(parii)
            participants = int(event_data.participants) - 1
            event_reg_id = event_obj.browse(reg_data.name.id)
            event_reg_id.write({'part_ids': [(6, 0, list1)],
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
                raise except_orm(_('Error !'), _('Participation in this Event'
                                                 'is Full.'))

            # check last registration date is over or not
            if reg_data.reg_date > event_data.last_reg_date:
                raise except_orm(_('Error !'), _('Last Registration date is'
                                                 'over for this Event.'))

            # make entry in participant
            val = {
                'stu_pid': str(prt_data.pid),
                'score': 0,
                'win_parameter_id': event_data.parameter_id.id,
                'event_id': reg_data.name.id,
                'name': reg_data.part_name_id.id,
            }
            temp = event_part_obj.create(val)
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
            stu_part_id.write({'event_ids': [(6, 0, list1)]})
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
            evnt_reg_id.write({'part_ids': [(6, 0, list1)]})
        return True

    @api.multi
    def read(self, recs, fields=None, load='_classic_read'):
        res_list = []
        res = super(school_event_registration, recs).read(fields=fields,
                                                          load=load)
        for res_update in res:
            res_update.update({'part_name_id': res_update.get('part_id')})
            res_list.append(res_update)
        return res_list


class student_student(models.Model):

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
            event_data = event_obj.browse(self._context.get('name'))
            std_ids = [std_id.id for std_id in event_data.part_standard_ids]
            args.append(('class_id', 'in', std_ids))
        return super(student_student, self).search(args, offset, limit, order,
                                                   count=count)

# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4:
