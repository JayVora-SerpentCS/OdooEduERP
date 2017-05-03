# -*- coding: utf-8 -*-
# See LICENSE file for full copyright and licensing details.

import time
from datetime import datetime
from dateutil.relativedelta import relativedelta
from odoo import models, fields, api, _
from odoo.exceptions import Warning as UserError


class StudentTransport(models.Model):
    _name = 'student.transport'
    _description = 'Transport Information'


class HrEmployee(models.Model):
    _name = 'hr.employee'
    _inherit = 'hr.employee'
    _description = 'Driver Information'

    licence_no = fields.Char('License No')
    is_driver = fields.Boolean('IS driver')
    transport_vehicle = fields.One2many('transport.vehicle',
                                        'driver_id', 'Vehicles')


class TransportPoint(models.Model):
    '''for points on root'''
    _name = 'transport.point'
    _description = 'Transport Point Information'

    name = fields.Char('Point Name', required=True)
    amount = fields.Float('Amount', default=0.0)

    @api.model
    def search(self, args, offset=0, limit=None, order=None, count=False):
        name = self._context.get('name')
        if name:
            transport_obj = self.env['student.transport']
            for transport_data in transport_obj.browse(name):
                point_ids = [point_id.id
                             for point_id in transport_data.trans_point_ids]
                args.append(('id', 'in', point_ids))
        return super(TransportPoint, self).search(args, offset, limit, order,
                                                  count=count)


class TransportVehicle(models.Model):
    '''for vehicle detail'''

    @api.multi
    @api.depends('vehi_participants_ids')
    def _compute_participants(self):
        for rec in self:
            rec.participant = len(rec.vehi_participants_ids)

    _name = 'transport.vehicle'
    _rec_name = 'vehicle'
    _description = 'Transport vehicle Information'

    driver_id = fields.Many2one('hr.employee', 'Driver Name', required=True)
    vehicle = fields.Char('Vehicle No', required=True)
    capacity = fields.Integer('Capacity')
    participant = fields.Integer(compute='_compute_participants',
                                 string='Total Participants', readonly=True)
    vehi_participants_ids = fields.Many2many('transport.participant',
                                             'vehicle_participant_student_rel',
                                             'vehicle_id', 'student_id',
                                             ' vehicle Participants')

    @api.model
    def search(self, args, offset=0, limit=None, order=None, count=False):
        name = self._context.get('name')
        if name:
            transport_obj = self.env['student.transport']
            transport_data = transport_obj.browse(name)
            vehicle_ids = [std_id.id
                           for std_id in transport_data.trans_vehicle_ids]
            args.append(('id', 'in', vehicle_ids))
        return super(TransportVehicle, self).search(args, offset, limit,
                                                    order, count=count)


class TransportParticipant(models.Model):
    '''for participants'''
    _name = 'transport.participant'
    _rec_name = 'stu_pid_id'
    _description = 'Transport Participant Information'

    name = fields.Many2one('student.student', 'Participant Name',
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
                              ('over', 'Over')],
                             'State', readonly=True,)

    @api.model
    def search(self, args, offset=0, limit=None, order=None, count=False):
        name = self._context.get('name')
        if name:
            student_obj = self.env['student.student']
            for student_data in student_obj.browse(name):
                transport_ids = [transport_id.id
                                 for transport_id in
                                 student_data.transport_ids]
                args.append(('id', 'in', transport_ids))
        return super(TransportParticipant, self).search(args, offset, limit,
                                                        order, count=count)


class StudentTransports(models.Model):
    '''for root detail'''

    _name = 'student.transport'
    _description = 'Student Transport Information'

    @api.multi
    @api.depends('trans_participants_ids')
    def _compute_total_participants(self):
        for rec in self:
            rec.total_participantes = len(rec.trans_participants_ids)

    name = fields.Char('Transport Root Name', required=True)
    start_date = fields.Date('Start Date', required=True)
    contact_per_id = fields.Many2one('hr.employee', 'Contact Person')
    end_date = fields.Date('End Date', required=True)
    total_participantes = fields.Integer(compute='_compute_total_participants',
                                         method=True,
                                         string='Total Participants',
                                         readonly=True)
    trans_participants_ids = fields.Many2many('transport.participant',
                                              'transport_participant_rel',
                                              'participant_id', 'transport_id',
                                              'Participants', readonly=True)
    trans_vehicle_ids = fields.Many2many('transport.vehicle',
                                         'transport_vehicle_rel',
                                         'vehicle_id',
                                         'transport_id', ' vehicles')
    trans_point_ids = fields.Many2many('transport.point',
                                       'transport_point_rel',
                                       'point_id', 'root_id', ' Points')
    state = fields.Selection([('draft', 'Draft'),
                              ('open', 'Open'),
                              ('close', 'Close')],
                             'State', readonly=True, default='draft')

    @api.multi
    def transport_open(self):
        self.state = 'open'
        return True

    @api.multi
    def transport_close(self):
        self.state = 'close'
        return True

    @api.multi
    def delet_entry(self, transport_ids=None):
        ''' This method delete entry of participants
            @param self : Object Pointer
            @param cr : Database Cursor
            @param uid : Current Logged in User
            @param transport_ids : list of transport ids
            @param context : standard Dictionary
            @return : True
        '''
        prt_obj = self.env['transport.participant']
        vehi_obj = self.env['transport.vehicle']
        trans_ids = self.search([('state', '=', 'open')])
        vehi_ids = vehi_obj.search([])

        for trans in self.browse(trans_ids):
            stu_ids = [stu_id.id for stu_id in trans.trans_participants_ids]
            participants = []
            trans_parti = []
            for prt_data in prt_obj.browse(stu_ids):
                date = time.strftime("%Y-%m-%d")
                if date > prt_data.tr_end_date:
                    if prt_data.state != 'over':
                        trans_parti.append(prt_data.id)
                else:
                    participants.append(prt_data.id)
            if trans_parti:
                prt_obj.write(prt_data.id, {'state': 'over'})
            if participants:
                self.write(trans.id, {'trans_participants_ids':
                                      [(6, 0, participants)]},)

        for vehicle in vehi_obj.browse(vehi_ids):
            stu_ids = [stu_id.id for stu_id in vehicle.vehi_participants_ids]
            list1 = []
            for prt_data in prt_obj.browse(stu_ids):
                if prt_data.state != 'over':
                    list1.append(prt_data.id)
            vehi_obj.write(vehicle.id, {
                'vehi_participants_ids': [(6, 0, list1)]})
        return True


class StudentStudent(models.Model):
    _inherit = 'student.student'
    _description = 'Student Information'

    transport_ids = fields.Many2many('transport.participant', 'std_transport',
                                     'trans_id', 'stud_id', 'Transport',
                                     readonly=True)


class TransportRegistration(models.Model):
    '''for registration'''
    _name = 'transport.registration'
    _description = 'Transport Registration'

    name = fields.Many2one('student.transport', 'Transport Root Name',
                           domain=[('state', '=', 'open')], required=True)
    part_name = fields.Many2one('student.student', 'Participant Name',
                                required=True)
    reg_date = fields.Date('Registration Date', readonly=True,
                           default=lambda * a:
                           time.strftime("%Y-%m-%d %H:%M:%S"))
    reg_end_date = fields.Date('Registration End Date', readonly=True)
    for_month = fields.Integer('Registration For Months')
    state = fields.Selection([('draft', 'Draft'),
                              ('confirm', 'Confirm'),
                              ('pending', 'Pending'),
                              ('paid', 'Paid'),
                              ('cancel', 'Cancel')], 'State', readonly=True,
                             default='draft')
    vehicle_id = fields.Many2one('transport.vehicle', 'Vehicle No',
                                 required=True)
    point_id = fields.Many2one('transport.point', 'Point', widget='selection',
                               required=True)
    m_amount = fields.Float('Monthly Amount', readonly=True)
    paid_amount = fields.Float('Paid Amount')
    remain_amt = fields.Float('Due Amount')
    transport_fees = fields.Float(compute="_compute_transport_fees",
                                  string="Transport Fees")
    amount = fields.Float('Final Amount', readonly=True)
    count_inv = fields.Integer('Invoice Count', compute="_compute_invoice")

    @api.model
    def create(self, vals):
        ret_val = super(TransportRegistration, self).create(vals)
        m_amt = self.onchange_point_id(vals['point_id'])
        ex_dt = self.onchange_for_month(vals['for_month'])
        if ex_dt:
            ret_val.write({'m_amount': m_amt['value']['m_amount'],
                           'reg_end_date': ex_dt['value']['reg_end_date']})
        else:
            ret_val.write({'m_amount': m_amt['value']['m_amount']})
        return ret_val

    @api.depends('m_amount', 'for_month')
    def _compute_transport_fees(self):
        for rec in self:
            rec.transport_fees = rec.m_amount * rec.for_month

    @api.multi
    def transport_fees_pay(self):
        for rec in self:
            rec.state = 'pending'
            transport = rec.browse(rec.id)
            vals = {'partner_id': transport.part_name.partner_id.id,
                    'account_id': transport.part_name.partner_id.
                                  property_account_receivable_id.id,
                    'transport_student_id': transport.id}
            account_object = self.env['account.invoice'].create(vals)
            acct_journal_id = \
                account_object.journal_id.default_credit_account_id.id
            account_view_id = self.env.ref('account.invoice_form')
            inv_line = []
            line_vals = {'name': 'Transport Fees',
                         'account_id': acct_journal_id,
                         'quantity': transport.for_month,
                         'price_unit': transport.m_amount,
                         }
            inv_line.append((0, 0, line_vals))
            account_object.write({'invoice_line_ids': inv_line})
            return {'name': _("Pay Transport Fees"),
                    'view_type': 'form',
                    'view_mode': 'form',
                    'res_model': 'account.invoice',
                    'view_id': account_view_id.id,
                    'type': 'ir.actions.act_window',
                    'nodestroy': True,
                    'target': 'current',
                    'res_id': account_object.id,
                    'context': {}}

    @api.multi
    def view_invoice(self):
        invoices = self.env['account.invoice'].search([('transport_student_id',
                                                        '=', self.id)])
        action = self.env.ref('account.action_invoice_tree1').read()[0]
        if len(invoices) > 1:
            action['domain'] = [('id', 'in', invoices.ids)]
        elif len(invoices) == 1:
            action['views'] = [(self.env.ref('account.invoice_form').id,
                                                            'form')]
            action['res_id'] = invoices.ids[0]
        else:
            action = {'type': 'ir.actions.act_window_close'}
        return action

    @api.multi
    def _compute_invoice(self):
        for rec in self:
            invoice_count = self.env['account.invoice'].search_count([(
                                                'transport_student_id',
                                                '=', rec.id)])
            rec.count_inv = invoice_count

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
        mon = relativedelta(months= +month)
        tr_end_date = datetime.strptime(tr_start_date, '%Y-%m-%d') + mon
        date = datetime.strftime(tr_end_date, '%Y-%m-%d')
        return {'value': {'reg_end_date': date}}

    @api.multi
    def trans_regi_cancel(self):
        self.state = 'cancel'
        return True

    @api.multi
    def trans_regi_confirm(self):
        self.write({'state': 'confirm'})
        trans_obj = self.env['student.transport']
        prt_obj = self.env['student.student']
        stu_prt_obj = self.env['transport.participant']
        vehi_obj = self.env['transport.vehicle']
        for reg_data in self:
            # registration months must one or more then one
            if reg_data.for_month <= 0:
                raise UserError(_('Error! Sorry Registration months must be 1'
                                  'or more then one.'))
            # First Check Is there vacancy or not
            person = int(reg_data.vehicle_id.participant) + 1
            if reg_data.vehicle_id.capacity < person:
                raise UserError(_('There is No More vacancy on this vehicle.'))

            # calculate amount and Registration End date
            amount = reg_data.point_id.amount * reg_data.for_month
            tr_start_date = (reg_data.reg_date)
            month = reg_data.for_month
            mon1 = relativedelta(months= +month)
            tr_end_date = datetime.strptime(tr_start_date, '%Y-%m-%d') + mon1
            date = datetime.strptime(reg_data.name.end_date, '%Y-%m-%d')
            if tr_end_date > date:
                raise UserError(_('For this much Months\
                                  Registration is not Possible because\
                                  Root end date is Early.'))
            # make entry in Transport
            dict_prt = {'stu_pid_id': str(reg_data.part_name.pid),
                        'amount': amount,
                        'transport_id': reg_data.name.id,
                        'tr_end_date': tr_end_date,
                        'name': reg_data.part_name.id,
                        'months': reg_data.for_month,
                        'tr_reg_date': reg_data.reg_date,
                        'point_id': reg_data.point_id.id,
                        'state': 'running',
                        'vehicle_id': reg_data.vehicle_id.id}
            temp = stu_prt_obj.sudo().create(dict_prt)
            # make entry in Transport vehicle.
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
            vehicle_id = vehi_obj.browse(reg_data.vehicle_id.id)
            vehicle_id.sudo().write({'vehi_participants_ids': [(6, 0, list1)]})
            # make entry in student.
            list1 = []
            for root in reg_data.part_name.transport_ids:
                list1.append(root.id)
            list1.append(temp.id)
            part_name_id = prt_obj.browse(reg_data.part_name.id)
            part_name_id.sudo().write({'transport_ids': [(6, 0, list1)]})
            # make entry in transport.
            list1 = []
            for prt in reg_data.name.trans_participants_ids:
                list1.append(prt.id)
            list1.append(temp.id)
            stu_tran_id = trans_obj.browse(reg_data.name.id)
            stu_tran_id.sudo().write({'trans_participants_ids':
                                      [(6, 0, list1)]})
        return True


class AccountInvoice(models.Model):
    _inherit = "account.invoice"

    transport_student_id = fields.Many2one('transport.registration',
                                           string="Transport Student")


class AccountPayment(models.Model):
    _inherit = "account.payment"

    @api.multi
    def post(self):
        res = super(AccountPayment, self).post()
        for invoice in self.invoice_ids:
            if invoice.transport_student_id and\
            invoice.state == 'paid':
                fees_payment = invoice.transport_student_id.paid_amount
                fees_payment += self.amount
                invoice.transport_student_id.write(
                                    {'state': 'paid',
                                     'paid_amount': fees_payment,
                                     'remain_amt': invoice.residual})
            if invoice.transport_student_id and\
            invoice.state == 'open':
                fees_payment = invoice.hostel_student_id.paid_amount
                fees_payment += self.amount
                invoice.transport_student_id.write(
                                    {'status': 'pending',
                                     'paid_amount': fees_payment,
                                     'remain_amt': invoice.residual})
        return res
