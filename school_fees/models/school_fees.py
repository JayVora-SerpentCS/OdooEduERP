# -*- coding: utf-8 -*-
# See LICENSE file for full copyright and licensing details.

import time
from odoo import models, fields, api, _
from odoo.exceptions import Warning as UserError
from datetime import datetime


class StudentFeesRegister(models.Model):
    '''Student fees Register'''
    _name = 'student.fees.register'
    _description = 'Student fees Register'

    name = fields.Char('Name', required=True,)
    date = fields.Date('Date', required=True,
                       default=lambda * a: time.strftime('%Y-%m-%d'))
    number = fields.Char('Number', readonly=True,
                         default=lambda obj: obj.env['ir.sequence'].
                         next_by_code('student.fees.register'))
    line_ids = fields.One2many('student.payslip', 'register_id',
                               'PaySlips')
    total_amount = fields.Float("Total", readonly=True)
    state = fields.Selection([('draft', 'Draft'), ('confirm', 'Confirm')],
                             'State', readonly=True, default='draft')
    journal_id = fields.Many2one('account.journal', 'Journal',
                                 required=True)
    company_id = fields.Many2one('res.company', 'Company', required=True,
                                 change_default=True, readonly=True,
                                 default=lambda obj_c: obj_c.env['res.users'].
                                 browse([obj_c._uid])[0].company_id)

    @api.multi
    def fees_register_draft(self):
        self.state = 'draft'
        return True

    @api.multi
    def fees_register_confirm(self):
        student_pool = self.env['student.student']
        slip_pool = self.env['student.payslip']
        student_ids = student_pool.search([])
        for fees_obj in self:
            for vals in fees_obj.browse(fees_obj.ids):
                for stu in student_ids:
                    old_slips = slip_pool.search([('student_id', '=', stu.id),
                                                  ('date', '=', vals.date)])
                    if old_slips:
                        old_slips.write({'register_id': vals.id})
                        for sid in old_slips:
                            sid.signal_workflow('_confirm')
                    else:
                        res = {'student_id': stu.id,
                               'register_id': vals.id,
                               'name': vals.name,
                               'date': vals.date,
                               'journal_id': vals.journal_id.id,
                               'company_id': vals.company_id.id}
                        slip_id = slip_pool.create(res)
                        slip_id.signal_workflow('_confirm')
                amount = 0
                for datas in fees_obj.browse(self.ids):
                    for data in datas.line_ids:
                        amount = amount + data.total
                    student_fees_register_vals = {'total_amount': amount}
                    datas.write(student_fees_register_vals)
                fees_obj.write({'state': 'confirm'})
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
    amount = fields.Float('Amount', digits=(16, 4))
    line_ids = fields.One2many('student.payslip.line.line', 'slipline_id',
                               'Calculations')
    slip_id = fields.Many2one('student.payslip', 'Pay Slip')
    description = fields.Text('Description')
    account_id = fields.Many2one('account.account', string="Account")


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
    amount = fields.Float('Amount', digits=(16, 4))
    sequence = fields.Integer('Sequence')
    line_ids = fields.One2many('student.payslip.line.line', 'slipline1_id',
                               'Calculations')
    account_id = fields.Many2one('account.account', string="Account")


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
                         'The code of the Fees Structure must'
                         'be unique !')]


class StudentPayslip(models.Model):

    @api.multi
    def payslip_draft(self):
        self.state = 'draft'
        return True

    @api.multi
    def payslip_paid(self):
        self.state = 'paid'
        return True

    @api.multi
    def payslip_confirm(self):
        fees_structure_obj = self.env['student.fees.structure']
        student_payslip_line_obj = self.env['student.payslip.line']
        for payslip_obj in self:
            for student_payslip_data in self.read(['fees_structure_id']):
                fee_id = student_payslip_data['fees_structure_id'][1]
                if not student_payslip_data['fees_structure_id']:
                    payslip_obj.write({'state': 'paid'})
                    return True
                fees_ids = fees_structure_obj.search([('name', '=', fee_id)])
                for datas in fees_ids:
                    for data in datas.line_ids or []:
                        line_vals = {'slip_id': self.id,
                                     'name': data.name,
                                     'code': data.code,
                                     'sequence': data.sequence,
                                     'type': data.type,
                                     'account_id': data.account_id.id,
                                     'amount': data.amount}
                        student_payslip_line_obj.create(line_vals)
                amount = 0
                for datas in self.browse(self.ids):
                    for data in datas.line_ids:
                        amount = amount + data.amount
                    student_payslip_vals = {'total': amount}
                    datas.write(student_payslip_vals)
            payslip_obj.write({'state': 'confirm'})
            return True

    _name = 'student.payslip'
    _description = 'Student PaySlip'

    fees_structure_id = fields.Many2one('student.fees.structure',
                                        'Fees Structure',
                                        states={'paid': [('readonly', True)]})
    standard_id = fields.Many2one('standard.standard', 'Class')
    division_id = fields.Many2one('standard.division', 'Division')
    medium_id = fields.Many2one('standard.medium', 'Medium')
    register_id = fields.Many2one('student.fees.register', 'Register')
    name = fields.Char('Description')
    number = fields.Char('Number', readonly=True,
                         default=lambda obj: obj.env['ir.sequence'].
                         next_by_code('student.payslip'))
    student_id = fields.Many2one('student.student', 'Student', required=True)
    date = fields.Date('Date', readonly=True,
                       default=lambda * a: time.strftime('%Y-%m-%d'))
    line_ids = fields.One2many('student.payslip.line', 'slip_id',
                               'PaySlip Line')
    total = fields.Float("Total", readonly=True)
    state = fields.Selection([('draft', 'Draft'), ('confirm', 'Confirm'),
                              ('pending', 'Pending'), ('paid', 'Paid')],
                              'State', readonly=True,
                             default='draft')
    journal_id = fields.Many2one('account.journal', 'Journal', required=True)
    currency_id = fields.Many2one('res.currency', 'Currency')
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
        self.standard_id = self.student_id.standard_id.id
        self.division_id = self.student_id.division_id
        self.medium_id = self.student_id.medium_id

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
    def onchange_journal_id(self, journal_id=False):
        result = {}
        if journal_id:
            journal = self.env['account.journal'].browse(journal_id)
            currency_id = journal and journal.currency_id and\
                journal.currency_id.id\
                or journal.company_id.currency_id.id
            result = {'value': {'currency_id': currency_id}}
        return result

    @api.multi
    def invoice_view(self):
        invoice_search = self.env['account.invoice'].search([(
                                                'student_payslip_id', '=',
                                                 self.id)])
        invoice_form = self.env.ref('account.invoice_form')
        return {'name': _("View Invoice"),
                'view_type': 'form',
                'view_mode': 'form',
                'res_model': 'account.invoice',
                'res_id': invoice_search.id,
                'view_id': invoice_form.id,
                'type': 'ir.actions.act_window',
                'nodestroy': True,
                'target': 'current',
                }

    @api.multi
    def action_move_create(self):
        cur_obj = self.env['res.currency']
        move_obj = self.env['account.move']
        move_line_obj = self.env['account.move.line']
        for fees in self.browse(self.ids):
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
            sign = debit - credit < 0 and - 1 or 1
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
        for student_obj in self:
            student_obj.write({'state': 'pending'})
            if not self.ids:
                return []
            fees = student_obj.browse(student_obj.id)
            vals = {'partner_id': fees.student_id.partner_id.id,
                    'date_invoice': fees.date,
                    'account_id': fees.student_id.partner_id.
                                  property_account_receivable_id.id,
                    'journal_id': fees.journal_id.id,
                    'slip_ref': fees.number,
                    'student_payslip_id': fees.id,
                    'type': 'out_invoice',
                    }
            invoice_line = []
            for line in student_obj.line_ids:
                invoice_line_vals = {
                       'name': line.name,
                       'account_id': line.account_id.id,
                       'quantity': 1.000,
                       'price_unit': line.amount
                       }
                invoice_line.append((0, 0, invoice_line_vals))
            vals.update({'invoice_line_ids': invoice_line})
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

    slip_ref = fields.Char('Fees Slip Refrence')
    student_payslip_id = fields.Many2one('student.payslip',
                                         string="Student Payslip")


class AccountPayment(models.Model):
    _inherit = "account.payment"

    @api.multi
    def post(self):
        res = super(AccountPayment, self).post()
        curr_date = datetime.now()
        for invoice in self.invoice_ids:
            if invoice.student_payslip_id:
                invoice.student_payslip_id.write(
                                    {'state': 'paid',
                                     'payment_date': curr_date,
                                     'move_id': invoice.move_id.id or False})
        return res
