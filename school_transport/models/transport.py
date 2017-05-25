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
    def name_search(self, name='', args=None, operator='ilike',
                    limit=100):
        transport_obj = self.env['student.transport']
        name_points = self._context.get('name')
        args = args or []
        if name_points:
            transport_data = transport_obj.browse(name_points)
            point_ids = [point_id.id
                         for point_id in transport_data.trans_point_ids]
            args.extend([('id', 'in', point_ids)])
        return super(TransportPoint, self).name_search(name=name, args=args,
                                                       operator=operator,
                                                       limit=limit)


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
    def name_search(self, name='', args=None, operator='ilike',
                    limit=100):
        transport_obj = self.env['student.transport']
        name_vehicle = self._context.get('name')
        args = args or []
        if name_vehicle:
            transport_data = transport_obj.browse(name_vehicle)
            vehicle_ids = [std_id.id
                           for std_id in transport_data.trans_vehicle_ids]
            args.extend([('id', 'in', vehicle_ids)])
        return super(TransportVehicle, self).name_search(name=name, args=args,
                                                         operator=operator,
                                                         limit=limit)


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
    def name_search(self, name='', args=None, operator='ilike',
                    limit=100):
        student_obj = self.env['student.student']
        std_name = self._context.get('name')
        if std_name:
            for student_data in student_obj.browse(std_name):
                transport_ids = [transport_id.id
                                 for transport_id in
                                 student_data.transport_ids]
                args.append(('id', 'in', transport_ids))
        return super(TransportParticipant, self).name_search(name=name,
                                                             args=args,
                                                             operator=operator,
                                                             limit=limit)


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
        for rec in self:
            rec.state = 'open'
        return True

    @api.multi
    def transport_close(self):
        for rec in self:
            rec.state = 'close'
        return True

    @api.multi
    def participant_expire(self):
        current_date = datetime.now()
        trans_parti = self.env['transport.participant']
        parti_obj_search = trans_parti.search([('tr_end_date', '<',
                                                current_date)])
        if parti_obj_search:
            for partitcipants in parti_obj_search:
                partitcipants.state = 'over'


class StudentStudent(models.Model):
    _inherit = 'student.student'
    _description = 'Student Information'

    transport_ids = fields.Many2many('transport.participant', 'std_transport',
                                     'trans_id', 'stud_id', 'Transport')


class TransportRegistration(models.Model):
    '''for registration'''
    _name = 'transport.registration'
    _description = 'Transport Registration'

    @api.depends('state')
    def _get_user_groups(self):
        user_group = self.env.ref('school_transport.group_transportation_user')
        grps = [group.id
                for group in self.env['res.users'].browse(self._uid).groups_id]
        if user_group.id in grps:
            self.transport_user = True

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
    transport_user = fields.Boolean(compute="_get_user_groups",
                                    string="transport user")

    @api.model
    def create(self, vals):
        ret_val = super(TransportRegistration, self).create(vals)
        if ret_val:
            ret_val.onchange_point_id()
            ret_val.onchange_for_month()
        return ret_val

    @api.depends('m_amount', 'for_month')
    def _compute_transport_fees(self):
        for rec in self:
            rec.transport_fees = rec.m_amount * rec.for_month

    @api.multi
    def transport_fees_pay(self):
        invoice_obj = self.env['account.invoice']
        for rec in self:
            rec.state = 'pending'
            partner = rec.part_name and rec.part_name.partner_id
            vals = {'partner_id': partner.id,
                    'account_id': partner.property_account_receivable_id.id,
                    'transport_student_id': rec.id}
            invoice = invoice_obj.create(vals)
            journal = invoice.journal_id
            acct_journal_id = journal.default_credit_account_id.id
            account_view_id = self.env.ref('account.invoice_form')
            line_vals = {'name': 'Transport Fees',
                         'account_id': acct_journal_id,
                         'quantity': rec.for_month,
                         'price_unit': rec.m_amount}
            invoice.write({'invoice_line_ids': [(0, 0, line_vals)]})
            return {'name': _("Pay Transport Fees"),
                    'view_type': 'form',
                    'view_mode': 'form',
                    'res_model': 'account.invoice',
                    'view_id': account_view_id.id,
                    'type': 'ir.actions.act_window',
                    'nodestroy': True,
                    'target': 'current',
                    'res_id': invoice.id,
                    'context': {}}

    @api.multi
    def view_invoice(self):
        invoice_obj = self.env['account.invoice']
        for rec in self:
            invoices = invoice_obj.search([('transport_student_id', '=',
                                            rec.id)])
            action = rec.env.ref('account.action_invoice_tree1').read()[0]
            if len(invoices) > 1:
                action['domain'] = [('id', 'in', invoices.ids)]
            elif len(invoices) == 1:
                action['views'] = [(rec.env.ref('account.invoice_form').id,
                                    'form')]
                action['res_id'] = invoices.ids[0]
            else:
                action = {'type': 'ir.actions.act_window_close'}
            return action

    @api.multi
    def _compute_invoice(self):
        inv_obj = self.env['account.invoice']
        for rec in self:
            rec.count_inv = inv_obj.search_count([('transport_student_id',
                                                   '=', rec.id)])

    @api.multi
    @api.onchange('point_id')
    def onchange_point_id(self):
        for rec in self:
            if rec.point_id:
                rec.m_amount = rec.point_id.amount or 0.0

    @api.multi
    @api.onchange('for_month')
    def onchange_for_month(self):
        for rec in self:
            tr_start_date = time.strftime("%Y-%m-%d")
            mon = relativedelta(months=+rec.for_month)
            tr_end_date = datetime.strptime(tr_start_date, '%Y-%m-%d'
                                            ) + mon
            date = datetime.strftime(tr_end_date, '%Y-%m-%d')
            rec.reg_end_date = date

    @api.multi
    def trans_regi_cancel(self):
        for rec in self:
            rec.write({'state': 'cancel'})
        return True

    @api.multi
    def trans_regi_confirm(self):
        trans_obj = self.env['student.transport']
        prt_obj = self.env['student.student']
        stu_prt_obj = self.env['transport.participant']
        vehi_obj = self.env['transport.vehicle']
        for rec in self:
            # registration months must one or more then one
            if rec.for_month <= 0:
                raise UserError(_('Error! Sorry Registration months must be 1'
                                  'or more then one.'))
            # First Check Is there vacancy or not
            person = int(rec.vehicle_id.participant) + 1
            if rec.vehicle_id.capacity < person:
                raise UserError(_('There is No More vacancy on this vehicle.'))

            rec.write({'state': 'confirm'})
            # calculate amount and Registration End date
            amount = rec.point_id.amount * rec.for_month
            tr_start_date = (rec.reg_date)
            month = rec.for_month
            mon1 = relativedelta(months=+month)
            tr_end_date = datetime.strptime(tr_start_date, '%Y-%m-%d') + mon1
            date = datetime.strptime(rec.name.end_date, '%Y-%m-%d')
            if tr_end_date > date:
                raise UserError(_('For this much Months\
                                  Registration is not Possible because\
                                  Root end date is Early.'))
            # make entry in Transport
            dict_prt = {'stu_pid_id': str(rec.part_name.pid),
                        'amount': amount,
                        'transport_id': rec.name.id,
                        'tr_end_date': tr_end_date,
                        'name': rec.part_name.id,
                        'months': rec.for_month,
                        'tr_reg_date': rec.reg_date,
                        'point_id': rec.point_id.id,
                        'state': 'running',
                        'vehicle_id': rec.vehicle_id.id}
            temp = stu_prt_obj.sudo().create(dict_prt)
            # make entry in Transport vehicle.
            list1 = []
            for prt in rec.vehicle_id.vehi_participants_ids:
                list1.append(prt.id)
            flag = True
            for prt in list1:
                data = stu_prt_obj.browse(prt)
                if data.name.id == rec.part_name.id:
                    flag = False
            if flag:
                list1.append(temp.id)
            vehicle_id = vehi_obj.browse(rec.vehicle_id.id)
            vehicle_id.sudo().write({'vehi_participants_ids': [(6, 0, list1)]})
            # make entry in student.
            list1 = []
            for root in rec.part_name.transport_ids:
                list1.append(root.id)
            list1.append(temp.id)
            part_name_id = prt_obj.browse(rec.part_name.id)
            part_name_id.sudo().write({'transport_ids': [(6, 0, list1)]})
            # make entry in transport.
            list1 = []
            for prt in rec.name.trans_participants_ids:
                list1.append(prt.id)
            list1.append(temp.id)
            stu_tran_id = trans_obj.browse(rec.name.id)
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
        for rec in self:
            for invoice in rec.invoice_ids:
                vals = {}
                if invoice.transport_student_id and invoice.state == 'paid':
                    fees_payment = (invoice.transport_student_id.paid_amount +
                                    rec.amount)
                    vals = {'state': 'paid',
                            'paid_amount': fees_payment}
                elif invoice.transport_student_id and invoice.state == 'open':
                    fees_payment = (invoice.transport_student_id.paid_amount +
                                    rec.amount)
                    vals = {'status': 'pending',
                            'paid_amount': fees_payment,
                            'remain_amt': invoice.residual}
                invoice.transport_student_id.write(vals)
        return res
