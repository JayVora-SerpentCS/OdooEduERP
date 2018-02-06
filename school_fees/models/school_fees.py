# -*- coding: utf-8 -*-
# See LICENSE file for full copyright and licensing details.

import time
from odoo import models, fields, api, _
from odoo.exceptions import ValidationError, Warning as UserError
from datetime import datetime


class StudentFeesRegister(models.Model):
    '''Student fees Register'''
    _name = 'student.fees.register'
    _description = 'Student fees Register'

    @api.multi
    @api.depends('line_ids')
    def _compute_total_amount(self):
        '''Method to compute total amount'''
        for rec in self:
            total_amt = 0.0
            for line in rec.line_ids:
                total_amt += line.total
            rec.total_amount = total_amt

    name = fields.Char('Name', required=True, help="Enter Name")
    date = fields.Date('Date', required=True,
                       help="Date of register",
                       default=lambda * a: time.strftime('%Y-%m-%d'))
    number = fields.Char('Number', readonly=True,
                         default=lambda self: _('New'))
    line_ids = fields.One2many('student.payslip', 'register_id',
                               'PaySlips')
    total_amount = fields.Float("Total",
                                compute="_compute_total_amount",
                                store=True)
    state = fields.Selection([('draft', 'Draft'), ('confirm', 'Confirm')],
                             'State', readonly=True, default='draft')
    journal_id = fields.Many2one('account.journal', 'Journal',
                                 help="Select Journal",
                                 required=False)
    company_id = fields.Many2one('res.company', 'Company', required=True,
                                 change_default=True, readonly=True,
                                 default=lambda obj_c: obj_c.env['res.users'].
                                 browse([obj_c._uid])[0].company_id)
    fees_structure = fields.Many2one('student.fees.structure',
                                     'Fees Structure')
    standard_id = fields.Many2one('standard.standard', 'Class')

    @api.multi
    def fees_register_draft(self):
        '''Changes the state to draft'''
        self.write({'state': 'draft'})
#        for rec in self:
#            rec.state = 'draft'
#        return True

    @api.multi
    def fees_register_confirm(self):
        '''Method to confirm payslip'''
        stud_obj = self.env['student.student']
        slip_obj = self.env['student.payslip']
        school_std_obj = self.env['school.standard']
        for rec in self:
            if not rec.journal_id:
                raise ValidationError(_('Kindly, Select Account Journal'))
            if not rec.fees_structure:
                raise ValidationError(_('Kindly, Select Fees Structure'))
            school_std = school_std_obj.search([('standard_id', '=',
                                                 rec.standard_id.id)])
            student_ids = stud_obj.search([('standard_id', 'in',
                                            school_std.ids),
                                           ('state', '=', 'done')])
            for stu in student_ids:
                old_slips = slip_obj.search([('student_id', '=', stu.id),
                                             ('date', '=', rec.date)])
                # Check if payslip exist of student
                if old_slips:
                    raise UserError(_('There is already a Payslip exist for\
                                           student: %s\
                                           for same date.!') % stu.name)
                else:
                    rec.number = self.env['ir.sequence'].\
                        next_by_code('student.fees.register') or _('New')
                    res = {'student_id': stu.id,
                           'register_id': rec.id,
                           'name': rec.name,
                           'date': rec.date,
                           'company_id': rec.company_id.id,
                           'currency_id':
                           rec.company_id.currency_id.id or False,
                           'journal_id': rec.journal_id.id,
                           'fees_structure_id': rec.fees_structure.id or False}
                    slip_id = slip_obj.create(res)
                    slip_id.onchange_student()
            # Calculate the amount
            amount = 0
            for data in rec.line_ids:
                amount += data.total
            rec.write({'total_amount': amount,
                       'state': 'confirm'})
        return True


class StudentPayslipLine(models.Model):
    '''Student PaySlip Line'''
    _name = 'student.payslip.line'
    _description = 'Student PaySlip Line'

    name = fields.Char('Name', required=True)
    code = fields.Char('Code', required=True)
    type = fields.Selection([('month', 'Monthly'),
                             ('year', 'Yearly'),
                             ('range', 'Range')],
                            'Duration', required=True)
    amount = fields.Float('Amount', digits=(16, 2))
    line_ids = fields.One2many('student.payslip.line.line', 'slipline_id',
                               'Calculations')
    slip_id = fields.Many2one('student.payslip', 'Pay Slip')
    description = fields.Text('Description')
    company_id = fields.Many2one('res.company', 'Company',
                                 change_default=True,
                                 default=lambda obj_c: obj_c.env['res.users'].
                                 browse([obj_c._uid])[0].company_id)
    currency_id = fields.Many2one('res.currency',
                                  'Currency')
    currency_symbol = fields.Char(related="currency_id.symbol",
                                  string='Symbol')
    account_id = fields.Many2one('account.account', "Account")

    @api.onchange('company_id')
    def set_currency_onchange(self):
        for rec in self:
            rec.currency_id = rec.company_id.currency_id.id


class StudentFeesStructureLine(models.Model):
    '''Student Fees Structure Line'''
    _name = 'student.fees.structure.line'
    _description = 'Student Fees Structure Line'
    _order = 'sequence'

    name = fields.Char('Name', required=True)
    code = fields.Char('Code', required=True)
    type = fields.Selection([('month', 'Monthly'),
                             ('year', 'Yearly'),
                             ('range', 'Range')],
                            'Duration', required=True)
    amount = fields.Float('Amount', digits=(16, 2))
    sequence = fields.Integer('Sequence')
    line_ids = fields.One2many('student.payslip.line.line', 'slipline1_id',
                               'Calculations')
    account_id = fields.Many2one('account.account', string="Account")
    company_id = fields.Many2one('res.company', 'Company',
                                 change_default=True,
                                 default=lambda obj_c: obj_c.env['res.users'].
                                 browse([obj_c._uid])[0].company_id)
    currency_id = fields.Many2one('res.currency', 'Currency')
    currency_symbol = fields.Char(related="currency_id.symbol",
                                  string='Symbol')

    @api.onchange('company_id')
    def set_currency_company(self):
        for rec in self:
            rec.currency_id = rec.company_id.currency_id.id


class StudentFeesStructure(models.Model):
    '''Fees structure'''
    _name = 'student.fees.structure'
    _description = 'Student Fees Structure'

    name = fields.Char('Name', required=True)
    code = fields.Char('Code', required=True)
    line_ids = fields.Many2many('student.fees.structure.line',
                                'fees_structure_payslip_rel',
                                'fees_id', 'slip_id', 'Fees Structure')

    _sql_constraints = [('code_uniq', 'unique(code)',
                         '''The code of the Fees Structure must
                         be unique !''')]


class StudentPayslip(models.Model):
    _name = 'student.payslip'
    _description = 'Student PaySlip'

    @api.multi
    def _compute_invoice(self):
        '''Method to compute number invoice'''
        inv_obj = self.env['account.invoice']
        for rec in self:
            rec.invoice_count = inv_obj.search_count([('student_payslip_id',
                                                       '=', rec.id)])
        return True

    fees_structure_id = fields.Many2one('student.fees.structure',
                                        'Fees Structure',
                                        states={'paid': [('readonly', True)]})
    standard_id = fields.Many2one('school.standard', 'Class')
    division_id = fields.Many2one('standard.division', 'Division')
    medium_id = fields.Many2one('standard.medium', 'Medium')
    register_id = fields.Many2one('student.fees.register', 'Register')
    name = fields.Char('Description')
    number = fields.Char('Number', readonly=True,
                         default=lambda self: _('New'))
    student_id = fields.Many2one('student.student', 'Student', required=True)
    date = fields.Date('Date', readonly=True,
                       help="Current Date of payslip",
                       default=lambda * a: time.strftime('%Y-%m-%d'))
    line_ids = fields.One2many('student.payslip.line', 'slip_id',
                               'PaySlip Line')
    total = fields.Monetary("Total", readonly=True,
                            help="Total Amount")
    state = fields.Selection([('draft', 'Draft'), ('confirm', 'Confirm'),
                              ('pending', 'Pending'), ('paid', 'Paid')],
                             'State', readonly=True, default='draft')
    journal_id = fields.Many2one('account.journal', 'Journal', required=False)
    invoice_count = fields.Integer(string="# of Invoices",
                                   compute="_compute_invoice")
    paid_amount = fields.Monetary('Paid Amount', help="Amount Paid")
    due_amount = fields.Monetary('Due Amount', help="Amount Remaining")
    currency_id = fields.Many2one('res.currency', 'Currency')
    currency_symbol = fields.Char(related='currency_id.symbol',
                                  string='Symbol')
    move_id = fields.Many2one('account.move', 'Journal Entry', readonly=True,
                              ondelete='restrict',
                              help='Link to the automatically'
                              'generated Journal Items.')
    payment_date = fields.Date('Payment Date', readonly=True,
                               states={'draft': [('readonly', False)]},
                               help='Keep empty to use the current date')
    type = fields.Selection([('out_invoice', 'Customer Invoice'),
                             ('in_invoice', 'Supplier Invoice'),
                             ('out_refund', 'Customer Refund'),
                             ('in_refund', 'Supplier Refund'),
                             ], 'Type', required=True,
                            change_default=True, default='out_invoice')
    company_id = fields.Many2one('res.company', 'Company', required=True,
                                 change_default=True, readonly=True,
                                 default=lambda obj_c: obj_c.env['res.users'].
                                 browse([obj_c._uid])[0].company_id)

    _sql_constraints = [('code_uniq', 'unique(student_id,date,state)',
                         'The code of the Fees Structure must be unique !')]

    @api.onchange('student_id')
    def onchange_student(self):
        '''Method to get standard , division , medium of student selected'''
        if self.student_id:
            self.standard_id = self.student_id.standard_id.id
            self.division_id = self.student_id.standard_id.division_id.id
            self.medium_id = self.student_id.medium_id

    @api.multi
    def unlink(self):
        for rec in self:
            if rec.state != 'draft':
                raise UserError(_('''You can delete record in unconfirm state
                only!'''))
        return super(StudentPayslip, self).unlink()

    @api.multi
    @api.onchange('journal_id')
    def onchange_journal_id(self):
        '''Method to get currency from journal'''
        for rec in self:
            currency_id = rec.journal_id and rec.journal_id.currency_id and\
                rec.journal_id.currency_id.id\
                or rec.journal_id.company_id.currency_id.id
            rec.currency_id = currency_id

    @api.model
    def create(self, vals):
        if vals.get('student_id'):
            student = self.env['student.student'].browse(vals.get('student_id')
                                                         )
            vals.update({'standard_id': student.standard_id.id,
                         'division_id': student.standard_id.division_id.id,
                         'medium_id': student.medium_id.id})
        return super(StudentPayslip, self).create(vals)

    @api.multi
    def write(self, vals):
        if vals.get('student_id'):
            student = self.env['student.student'].browse(vals.get('student_id')
                                                         )
            vals.update({'standard_id': student.standard_id.id,
                         'division_id': student.standard_id.division_id.id,
                         'medium_id': student.medium_id.id})
        return super(StudentPayslip, self).write(vals)

    @api.multi
    def copy(self, default=None):
        if default is None:
            default = {}
        default.update({'state': 'draft',
                        'number': False,
                        'move_id': False,
                        'line_ids': []})
        return super(StudentPayslip, self).copy(default)

    @api.multi
    def payslip_draft(self):
        '''Change state to draft'''
        self.write({'state': 'draft'})
        return True

    @api.multi
    def payslip_paid(self):
        '''Change state to paid'''
        self.write({'state': 'paid'})
        return True

    @api.multi
    def payslip_confirm(self):
        '''Method to confirm payslip'''
        for rec in self:
            if not rec.journal_id:
                raise ValidationError(_('Kindly, Select Account Journal!'))
            if not rec.fees_structure_id:
                raise ValidationError(_('Kindly, Select Fees Structure!'))
            lines = []
            for data in rec.fees_structure_id.line_ids or []:
                line_vals = {'slip_id': rec.id,
                             'name': data.name,
                             'code': data.code,
                             'sequence': data.sequence,
                             'type': data.type,
                             'account_id': data.account_id.id,
                             'amount': data.amount,
                             'currency_id': data.currency_id.id or False,
                             'currency_symbol': data.currency_symbol or False}
                lines.append((0, 0, line_vals))
            rec.write({'line_ids': lines})
            # Compute amount
            amount = 0
            for data in rec.line_ids:
                amount += data.amount
            rec.write({'total': amount,
                       'state': 'confirm',
                       'due_amount': amount,
                       'currency_id': rec.company_id.currency_id.id or False
                       })
        return True

    @api.multi
    def invoice_view(self):
        '''View number of invoice of student'''
        invoice_obj = self.env['account.invoice']
        for rec in self:
            invoices = invoice_obj.search([('student_payslip_id', '=',
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
    def action_move_create(self):
        cur_obj = self.env['res.currency']
        move_obj = self.env['account.move']
        move_line_obj = self.env['account.move.line']
        for fees in self:
            if not fees.journal_id.sequence_id:
                raise UserError(_('Please define sequence on'
                                  'the journal related to this'
                                  'invoice.'))
            if fees.move_id:
                continue
            ctx = self._context.copy()
            ctx.update({'lang': fees.student_id.lang})
            if not fees.payment_date:
                self.write([fees.id], {'payment_date': time.strftime
                           ('%Y-%m-%d')})
            company_currency = fees.company_id.currency_id.id
            diff_currency_p = fees.currency_id.id != company_currency
            current_currency = fees.currency_id and fees.currency_id.id\
                or company_currency
            account_id = False
            comapny_ac_id = False
            if fees.type in ('in_invoice', 'out_refund'):
                account_id = fees.student_id.property_account_payable.id
                cmpy_id = fees.company_id.partner_id
                comapny_ac_id = cmpy_id.property_account_receivable.id
            elif fees.type in ('out_invoice', 'in_refund'):
                account_id = fees.student_id.property_account_receivable.id
                cmp_id = fees.company_id.partner_id
                comapny_ac_id = cmp_id.property_account_payable.id
            if fees.journal_id.centralisation:
                raise UserError(_('You cannot create an invoice on a'
                                  'centralized'
                                  'journal. UnCheck the centralized'
                                  'counterpart'
                                  'box in the related journal from the'
                                  'configuration menu.'))
            move = {'ref': fees.name,
                    'journal_id': fees.journal_id.id,
                    'date': fees.payment_date or time.strftime('%Y-%m-%d')}
            ctx.update({'company_id': fees.company_id.id})
            move_id = move_obj.create(move)
            context_multi_currency = self._context.copy()
            context_multi_currency.update({'date': time.strftime('%Y-%m-%d')})
            debit = 0.0
            credit = 0.0
            if fees.type in ('in_invoice', 'out_refund'):
                credit = cur_obj.compute(self._cr, self._uid,
                                         fees.currency_id.id, company_currency,
                                         fees.total,
                                         context=context_multi_currency)
            elif fees.type in ('out_invoice', 'in_refund'):
                debit = cur_obj.compute(self._cr, self._uid,
                                        fees.currency_id.id, company_currency,
                                        fees.total,
                                        context=context_multi_currency)
            if debit < 0:
                credit = -debit
                debit = 0.0
            if credit < 0:
                debit = -credit
                credit = 0.0
            sign = debit - credit < 0 and -1 or 1
            cr_id = diff_currency_p and current_currency or False
            am_cr = diff_currency_p and sign * fees.total or 0.0
            date = fees.payment_date or time.strftime('%Y-%m-%d')
            move_line = {'name': fees.name or '/',
                         'move_id': move_id,
                         'debit': debit,
                         'credit': credit,
                         'account_id': account_id,
                         'journal_id': fees.journal_id.id,
                         'parent_id': fees.student_id.parent_id.id,
                         'currency_id': cr_id,
                         'amount_currency': am_cr,
                         'date': date}
            move_line_obj.create(move_line)
            cr_id = diff_currency_p and current_currency or False
            move_line = {'name': fees.name or '/',
                         'move_id': move_id,
                         'debit': credit,
                         'credit': debit,
                         'account_id': comapny_ac_id,
                         'journal_id': fees.journal_id.id,
                         'parent_id': fees.student_id.parent_id.id,
                         'currency_id': cr_id,
                         'amount_currency': am_cr,
                         'date': date}
            move_line_obj.create(move_line)
            fees.write({'move_id': move_id})
            move_obj.post([move_id])
        return True

    @api.multi
    def student_pay_fees(self):
        '''Generate invoice of student fee'''
        for rec in self:
            if rec.number == 'New':
                rec.number = self.env['ir.sequence'
                                      ].next_by_code('student.payslip'
                                                     ) or _('New')
            rec.write({'state': 'pending'})
            partner = rec.student_id and rec.student_id.partner_id
            vals = {'partner_id': partner.id,
                    'date_invoice': rec.date,
                    'account_id': partner.property_account_receivable_id.id,
                    'journal_id': rec.journal_id.id,
                    'slip_ref': rec.number,
                    'student_payslip_id': rec.id,
                    'type': 'out_invoice'}
            invoice_line = []
            for line in rec.line_ids:
                acc_id = ''
                if line.account_id.id:
                    acc_id = line.account_id.id
                else:
                    # check type of invoice
                    if rec.type in ('out_invoice', 'in_refund'):
                        acc_id = rec.journal_id.default_credit_account_id.id
                    else:
                        acc_id = rec.journal_id.default_debit_account_id.id
                invoice_line_vals = {'name': line.name,
                                     'account_id': acc_id,
                                     'quantity': 1.000,
                                     'price_unit': line.amount}
                invoice_line.append((0, 0, invoice_line_vals))
            vals.update({'invoice_line_ids': invoice_line})
            # creates invoice
            account_invoice_id = self.env['account.invoice'].create(vals)
            invoice_obj = self.env.ref('account.invoice_form')
            return {'name': _("Pay Fees"),
                    'view_mode': 'form',
                    'view_type': 'form',
                    'res_model': 'account.invoice',
                    'view_id': invoice_obj.id,
                    'type': 'ir.actions.act_window',
                    'nodestroy': True,
                    'target': 'current',
                    'res_id': account_invoice_id.id,
                    'context': {}}


class StudentPayslipLineLine(models.Model):
    '''Function Line'''
    _name = 'student.payslip.line.line'
    _description = 'Function Line'
    _order = 'sequence'

    slipline_id = fields.Many2one('student.payslip.line', 'Slip Line')
    slipline1_id = fields.Many2one('student.fees.structure.line', 'Slip Line')
    sequence = fields.Integer('Sequence')
    from_month = fields.Many2one('academic.month', 'From Month')
    to_month = fields.Many2one('academic.month', 'To Month')


class AccountInvoice(models.Model):
    _inherit = "account.invoice"

    slip_ref = fields.Char('Fees Slip Reference',
                           help="Payslip Reference")
    student_payslip_id = fields.Many2one('student.payslip',
                                         string="Student Payslip")


class AccountPayment(models.Model):
    _inherit = "account.payment"

    @api.multi
    def post(self):
        '''Method to change state to paid when state in invoice is paid'''
        res = super(AccountPayment, self).post()
        curr_date = datetime.now()
        for rec in self:
            for invoice in rec.invoice_ids:
                vals = {'due_amount': invoice.residual}
                if invoice.student_payslip_id and invoice.state == 'paid':
                    # Calculate paid amount and changes state to paid
                    fees_payment = (invoice.student_payslip_id.paid_amount +
                                    rec.amount)
                    vals = {'state': 'paid',
                            'payment_date': curr_date,
                            'move_id': invoice.move_id.id or False,
                            'paid_amount': fees_payment,
                            'due_amount': invoice.residual}
                if invoice.student_payslip_id and invoice.state == 'open':
                    # Calculate paid amount and due amount and changes state
                    # to pending
                    fees_payment = (invoice.student_payslip_id.paid_amount +
                                    rec.amount)
                    vals = {'state': 'pending',
                            'due_amount': invoice.residual,
                            'paid_amount': fees_payment}
                invoice.student_payslip_id.write(vals)
        return res
