# -*- encoding: utf-8 -*-
##############################################################################
#
#    OpenERP, Open Source Management Solution
#    Copyright (C) 2004-2009 Tiny SPRL (<http://tiny.be>).
#    Copyright (C) 2013-2014 Serpent Consulting Services
#    (<http://www.serpentcs.com>)
#    Copyright (C) 2015 Serpent Consulting Services
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

from datetime import datetime
import time
from openerp import models, fields, api, _
from openerp.exceptions import except_orm, Warning, RedirectWarning
from dateutil.relativedelta import relativedelta


class student_transport(models.Model):

    _name = 'student.transport'
    _description = 'Transport Information'


class hr_employee(models.Model):

    _name = 'hr.employee'
    _inherit = 'hr.employee'
    _description = 'Driver Information'

    licence_no = fields.Char('Licence No')


#class for points on root
class transport_point(models.Model):

    _name = 'transport.point'
    _description = 'Transport Point Information'

    name = fields.Char('Point Name', required=True)
    amount = fields.Float('Amount', default=0.0)

    @api.model
    def search(self, args, offset=0, limit=None, order=None, count=False):
        if self._context.get('name'):
            transport_obj = self.env['student.transport']
            for transport_data in transport_obj.browse(self._context['name']):
                point_ids = [point_id.id for point_id in
                             transport_data.trans_point_ids]
                args.append(('id', 'in', point_ids))
        return super(transport_point, self).search(args, offset, limit,
                                                   order, count=count)


#class for vehicle detail
class transport_vehicle(models.Model):

    @api.one
    @api.depends('vehi_participants_ids')
    def _participants(self):
        if self.vehi_participants_ids:
            participate_list = []
            for vehi in self.vehi_participants_ids:
                participate_list.append(vehi.id)
            self.participant = len(participate_list)
        else:
            self.participant = 0

    _name = 'transport.vehicle'
    _rec_name = 'vehicle'
    _description = 'Transport vehicle Information'

    driver_id = fields.Many2one('hr.employee', 'Driver Name', required=True)
    vehicle = fields.Char('Vehicle No', required=True)
    capacity = fields.Integer('Capacity')
    participant = fields.Integer(compute='_participants',
                                 string='Total Participants', readonly=True)
    vehi_participants_ids = fields.Many2many('transport.participant',
                                             'vehicle_participant_student_rel',
                                             'vehicle_id', 'student_id',
                                             'vehicle Participants')

    @api.model
    def search(self, args, offset=0, limit=None, order=None, count=False):
        if self._context.get('name'):
            transport_obj = self.env['student.transport']
            transport_data = transport_obj.browse(self._context['name'])
            vehicle_ids = [std_id.id for std_id in
                           transport_data.trans_vehicle_ids]
            args.append(('id', 'in', vehicle_ids))
        return super(transport_vehicle, self).search(args, offset, limit,
                                                     order, count=count)


#class for participants
class transport_participant(models.Model):

    _name = 'transport.participant'
    _rec_name = 'stu_pid_id'
    _description = 'Transport Participent Information'

    name = fields.Many2one('student.student', 'Participent Name',
                           readonly=True, required=True)
    amount = fields.Float('Amount', readonly=True)
    transport_id = fields.Many2one('student.transport', 'Transport Root',
                                   readonly=True, required=True)
    stu_pid_id = fields.Char('Personal Identification Number', required=True)
    tr_reg_date = fields.Date('Transportation Registration Date')
    tr_end_date = fields.Date('Registration End Date')
    months = fields.Integer('Registration For Months')
    vehicle_id = fields.Many2one('transport.vehicle', 'Vehicle No')
    point_id = fields.Many2one('transport.point', 'Point Name')
    state = fields.Selection([('running', 'Running'),
                                     ('over', 'Over'), ],
                                     'State', readonly=True, defalt='running')

    @api.model
    def search(self, args, offset=0, limit=None, order=None, count=False):
        if self._context.get('name'):
            student_obj = self.env['student.student']
            for student_data in student_obj.browse(self._context['name']):
                transport_ids = [transport_id.id for transport_id in
                                 student_data.transport_ids]
                args.append(('id', 'in', transport_ids))
        return super(transport_participant, self).search(args, offset, limit,
                                                         order, count=count)


#class for root detail
class student_transports(models.Model):

    _name = 'student.transport'
    _description = 'Student Transport Information'

    @api.one
    @api.depends('trans_participants_ids')
    def _total_participantes(self):
        if self.trans_participants_ids:
            tot_list = []
            for root in self.trans_participants_ids:
                tot_list.append(root.id)
            self.total_participantes = len(tot_list)
        else:
            self.total_participantes = 0

    name = fields.Char('Transport Root Name', required=True)
    start_date = fields.Date('Start Date', required=True)
    contact_per_id = fields.Many2one('hr.employee', 'Contact Person')
    end_date = fields.Date('End Date', required=True)
    total_participantes = fields.Integer(compute='_total_participantes',
                                         method=True,
                                         string='Total Participantes',
                                         readonly=True)
    trans_participants_ids = fields.Many2many('transport.participant',
                                              'transport_participant_rel',
                                              'participant_id',
                                              'transport_id', 'Participants',
                                              readonly=True)
    trans_vehicle_ids = fields.Many2many('transport.vehicle',
                                         'transport_vehicle_rel', 'vehicle_id',
                                         'transport_id', ' vehicles')
    trans_point_ids = fields.Many2many('transport.point',
                                       'transport_point_rel', 'point_id',
                                       'root_id', ' Points')
    state = fields.Selection([('draft', 'Draft'),
                                    ('open', 'Open'),
                                    ('close', 'Close')],
                                    'State', readonly=True, default='draft')

    @api.multi
    def transport_open(self):
        self.write({'state': 'open'})
        return True

    @api.multi
    def transport_close(self):
        self.write({'state': 'close'})
        return True

    @api.v7
    def delet_entry(self, cr, uid, transport_ids=None, context=None):
        ''' This method delete entry of participants
        @param self : Object Pointer
        @param cr : Database Cursor
        @param uid : Current Logged in User
        @param transport_ids : list of transport ids
        @param context : standard Dictionary
        @return: True
        '''
        prt_obj = self.pool.get('transport.participant')
        vehi_obj = self.pool.get('transport.vehicle')
        trans_ids = self.search(cr, uid, [('state', '=', 'open')],
                                context=context)
        vehi_ids = vehi_obj.search(cr, uid, [], context=context)

        for trans in self.browse(cr, uid, trans_ids, context=context):
            stu_ids = [stu_id.id for stu_id in trans.trans_participants_ids]
            participants = []
            trans_parti = []
            for prt_data in prt_obj.browse(cr, uid, stu_ids, context=context):
                date = time.strftime("%Y-%m-%d")
                if date > prt_data.tr_end_date:
                    if prt_data.state != 'over':
                        trans_parti.append(prt_data.id)
                else:
                    participants.append(prt_data.id)
            if trans_parti:
                prt_obj.write(cr, uid, prt_data.id, {'state': 'over'},
                              context=context)
            if participants:
                self.write(cr, uid, trans.id, {'trans_participants_ids':
                                               [(6, 0, participants)]},
                           context=context)
        for vehi in vehi_obj.browse(cr, uid, vehi_ids, context=context):
            stu_ids = [stu_id.id for stu_id in vehi.vehi_participants_ids]
            list1 = []
            for prt_data in prt_obj.browse(cr, uid, stu_ids, context=context):
                if prt_data.state != 'over':
                    list1.append(prt_data.id)
            vehi_obj.write(cr, uid, vehi.id, {'vehi_participants_ids':
                                              [(6, 0, list1)]},
                           context=context)
        return True


class student_student(models.Model):

    _name = 'student.student'
    _inherit = 'student.student'
    _description = 'Student Information'

    transport_ids = fields.Many2many('transport.participant', 'std_transport',
                                     'trans_id', 'stud_id', 'Transport',
                                     readonly=True)


#class for registration
class transport_registration(models.Model):

    _name = 'transport.registration'
    _description = 'Transport Registration'

    name = fields.Many2one('student.transport', 'Transport Root Name',
                           domain=[('state', '=', 'open')], required=True)
    student_name_id = fields.Many2one('student.student', 'Student Id',
                                      required=True)
    student_name = fields.Char(related="student_name_id.name",
                               string='Student Name')
    reg_date = fields.Date('Registration Date', readonly=True,
                           default=lambda * a: time.strftime
                           ("%Y-%m-%d %H:%M:%S"))
    reg_end_date = fields.Date('Registration End Date', readonly=True)
    for_month = fields.Integer('Registration For Months')
    state = fields.Selection([('draft', 'Draft'),
                                      ('confirm', 'Confirm'),
                                      ('cancel', 'Cancel')
                                     ], 'State', readonly=True,
                             default='draft')
    vehicle_id = fields.Many2one('transport.vehicle', 'Vehicle No',
                                 required=True)
    point_id = fields.Many2one('transport.point', 'Point', widget='selection',
                               required=True)
    m_amount = fields.Float('Monthly Amount', readonly=True)
    amount = fields.Float('Final Amount', readonly=True)

    part_id = fields.Integer('Part Id')
    gr_no = fields.Char('Participant Id')

    @api.multi
    @api.onchange('student_name_id')
    def part_onchage(self):
        self.part_id = self.student_name_id.id
        self.gr_no = self.student_name_id.gr_no

    @api.model
    def create(self, vals):
        ret_val = super(transport_registration, self).create(vals)
        m_amt = self.onchange_point_id(vals['point_id'])
        ex_dt = self.onchange_for_month(vals['for_month'])
        if ex_dt:
            ret_val.write({'m_amount': m_amt['value']['m_amount'],
                           'reg_end_date': ex_dt['value']['reg_end_date']})
        else:
            ret_val.write({'m_amount': m_amt['value']['m_amount']})
        return ret_val

    @api.onchange('name')
    def onchange_vehicle(self):
        vehicle_lst = []
        for trans_obj in self:
            if trans_obj.name.trans_vehicle_ids:
                for vehicle_obj in trans_obj.name.trans_vehicle_ids:
                        vehicle_lst.append(vehicle_obj.id)
            return {'domain': {'vehicle_id': [('id', 'in', vehicle_lst)]}}

    @api.multi
    def onchange_point_id(self, point):
        if not point:
            return {}
        for point_obj in self.env['transport.point'].browse(point):
            return {'value': {'m_amount': point_obj.amount}}

    @api.multi
    def onchange_for_month(self, month):
        if not month:
            return {}
        tr_start_date = time.strftime("%Y-%m-%d")
        tr_end_date = datetime.strptime(tr_start_date, '%Y-%m-%d')
        + relativedelta(months=+ month)
        date = datetime.strftime(tr_end_date, '%Y-%m-%d')
        return {'value': {'reg_end_date': date}}

    @api.multi
    def trans_regi_cancel(self):
        self.write({'state': 'cancel'})
        return True

    @api.multi
    def trans_regi_confirm(self):
        self.write({'state': 'confirm'})
        trans_obj = self.env['student.transport']
        prt_obj = self.env['student.student']
        stu_prt_obj = self.env['transport.participant']
        vehi_obj = self.env['transport.vehicle']
        for reg_data in self:
            #registration months must one or more then one
            if reg_data.for_month <= 0:
                raise Warning(_('Error !'),
                              _('Sorry Registration months must one or'
                                'more then one.'))
            # First Check Is there vacancy or not
            person = int(reg_data.vehicle_id.participant) + 1
            if reg_data.vehicle_id.capacity < person:
                raise Warning(_('Error !'),
                              _('There is No More vacancy on this vehicle.'))

            #calculate amount and Registration End date
            amount = reg_data.point_id.amount * reg_data.for_month

            tr_start_date = (reg_data.reg_date)
            month = reg_data.for_month
            tr_end_date = datetime.strptime(tr_start_date, '%Y-%m-%d')
            + relativedelta(months=+ month)
            date = datetime.strptime(reg_data.name.end_date, '%Y-%m-%d')
            if tr_end_date > date:
                raise Warning(_('Error !'),
                              _('For this much Months Registration is'
                                'not Possibal because Root end'
                                'date is Early.'))
            # make entry in Transport
            temp = stu_prt_obj.create({
                                        'stu_pid_id': str
                                        (reg_data.part_name.pid),
                                        'amount': amount,
                                        'transport_id': reg_data.name.id,
                                        'tr_end_date': tr_end_date,
                                        'name': reg_data.part_name.id,
                                        'months': reg_data.for_month,
                                        'tr_reg_date': reg_data.reg_date,
                                        'point_id': reg_data.point_id.id,
                                        'vehicle_id': reg_data.vehicle_id.id,
                                        })
            #make entry in Transport vehicle.
            list1 = []
            for prt in reg_data.vehicle_id.vehi_participants_ids:
                list1.append(prt.id)
            flag = True
            for prt in list1:
                data = stu_prt_obj.browse(prt)
                if data.name.id == reg_data.part_name.id:
                    flag = False
            if flag:
                list1.append(temp.id)
                # vehi_obj.write(cr, uid, reg_data.vehicle_id.id,
                # {'vehi_participants_ids':[(6, 0, list1)]}, context=context)
            vehicle_id = vehi_obj.browse(reg_data.vehicle_id.id)
            vehicle_id.write({'vehi_participants_ids': [(6, 0, list1)]})
            #  make entry in student.
            list1 = []
            for root in reg_data.part_name.transport_ids:
                list1.append(root.id)
            list1.append(temp.id)
            #  prt_obj.write(cr, uid, reg_data.part_name.id,
            #  {'transport_ids':[(6, 0, list1)]}, context=context)
            part_name_id = prt_obj.browse(reg_data.part_name.id)
            part_name_id.write({'transport_ids': [(6, 0, list1)]})
            #  make entry in transport.
            list1 = []
            for prt in reg_data.name.trans_participants_ids:
                list1.append(prt.id)
            list1.append(temp.id)
            #  trans_obj.write(cr, uid, reg_data.name.id,
            #  {'trans_participants_ids':[(6, 0, list1)]}, context=context)
            stu_tran_id = trans_obj.browse(reg_data.name.id)
            stu_tran_id.write({'trans_participants_ids': [(6, 0, list1)]})
        return True

    @api.multi
    def read(self, recs, fields=None, load='_classic_read'):
        res_list = []
        res = super(transport_registration, recs).read(fields=fields,
                                                       load=load)
        for res_update in res:
            res_update.update({'student_name_id': res_update.get('part_id')})
            res_list.append(res_update)
        return res_list

# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4:
