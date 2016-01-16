# -*- coding: utf-8 -*-
# Part of Odoo. See LICENSE file for full copyright and licensing details.

import time
from openerp import models, fields, api, _
from openerp import workflow
from openerp.exceptions import Warning as UserError


class AccountVoucher(models.Model):
    _inherit = 'account.voucher'
    
    @api.multi
    def proforma_voucher(self):
        super(AccountVoucher, self).proforma_voucher()
        payslip_obj = self.env['student.payslip']
        for rec in self:
            payslip_ids = payslip_obj.search([('voucher_id',
                                               '=',
                                               rec.id)])
            payslip_ids.write({'state' : 'paid'})

class SchoolStandard(models.Model):
    _inherit = 'school.standard'
    
    fee_structure_id = fields.Many2one('student.fees.structure', 'Fee Structure')

class StudentFeesRegister(models.Model):
    '''Student fees Register'''
    _name = 'student.fees.register'
    _description = 'Student fees Register'
    
    @api.one
    @api.depends('line_ids', 'line_ids.total')
    def _get_total_amount(self):
        self.total_amount = 0.0
        for data in self.line_ids:
            self.total_amount = self.total_amount + data.total

    name = fields.Char('Name', required=True,
                       states={'confirm': [('readonly', True)]})
    date = fields.Date('Date', required=True,
                       states={'confirm': [('readonly', True)]},
                       default=lambda * a: time.strftime('%Y-%m-%d'))
    number = fields.Char('Number', readonly=True,
                         default=lambda obj: obj.env['ir.sequence'].
                         get('student.fees.register'))
    line_ids = fields.One2many('student.payslip', 'register_id',
                               'PaySlips',
                               states={'confirm': [('readonly', True)]})
    total_amount = fields.Float("Total", readonly=True, 
                                compute=_get_total_amount)
    state = fields.Selection([('draft', 'Draft'), ('confirm', 'Confirm')],
                             'State', readonly=True, default='draft')
    journal_id = fields.Many2one('account.journal', 'Journal',
                                 required=True,
                                 states={'confirm': [('readonly', True)]})
    company_id = fields.Many2one('res.company', 'Company',
                                 related="school_id.company_id", 
                                 readonly=True)
    school_id = fields.Many2one('school.school', 'School', readonly=True,
                                states={'draft': [('readonly', False)]})
    standard_id = fields.Many2one('school.standard', 'Standard', 
                                  readonly=True,
                                  states={'draft': [('readonly', False)]})

    @api.multi
    def fees_register_draft(self):
        return self.write({'state': 'draft'})

    @api.multi
    def fees_register_confirm(self):
        student_pool = self.env['student.student']
        slip_pool = self.env['student.payslip']
        for fees_obj in self:
            if not fees_obj.school_id:
                raise UserError(_('Please select School!'))
            elif not fees_obj.standard_id:
                raise UserError(_('Please select Standard!'))
            elif not fees_obj.standard_id.fee_structure_id:
                raise UserError(_('Please select Fee Structure in Standard!'))
            fee_structure = fees_obj.standard_id.fee_structure_id
            domain = [('standard_id','=',self.standard_id.id),
                      ('school_id','=',self.school_id.id)]
            student_ids = student_pool.search(domain)
            for stu in student_ids:
                res = {'student_id': stu.id,
                       'register_id': fees_obj.id,
                       'name': fees_obj.name,
                       'date': fees_obj.date,
                       'journal_id': fees_obj.journal_id.id,
                       'company_id': fees_obj.school_id.company_id.id,
                       'fees_structure_id' : fees_obj.standard_id\
                       and fees_obj.standard_id.fee_structure_id\
                       and fees_obj.standard_id.fee_structure_id.id}
                line_vals = []
                total = 0.0
                for line in fee_structure.line_ids:
                    line_vals.append({
                        'name' : line.name,
                        'code' : line.code,
                        'type' : line.type,
                        'amount' : line.amount
                    })
                    total += line.amount
                res['line_ids'] = [(0, 0, val) for val in line_vals]
                res.update({'total' : total})
                slip_pool.create(res)
        return self.write({'state' : 'confirm'})


class StudentPayslipLine(models.Model):
    '''Student PaySlip Line'''
    _name = 'student.payslip.line'
    _description = 'Student PaySlip Line'

    name = fields.Char('Name', required=True)
    code = fields.Char('Code', required=True)
    type = fields.Selection([('month', 'Monthly'),
                             ('year', 'Yearly'),
                             ('range', 'Range')],
                            'Duration', select=True, required=True)
    amount = fields.Float('Amount', digits=(16, 4))
    line_ids = fields.One2many('student.payslip.line.line', 'slipline_id',
                               'Calculations')
    slip_id = fields.Many2one('student.payslip', 'Pay Slip')
    description = fields.Text('Description')


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
                            'Duration', select=True, required=True)
    amount = fields.Float('Amount', digits=(16, 4))
    sequence = fields.Integer('Sequence')
    line_ids = fields.One2many('student.payslip.line.line', 'slipline1_id',
                               'Calculations')


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
        return self.write({'state': 'draft'})

    @api.multi
    def payslip_confirm(self):
        vals = {'state' : 'confirm'}
        for payslip_obj in self:
            if not payslip_obj.line_ids:
                vals.update({'line_ids' : []})
                if payslip_obj.fees_structure_id:
                    line_vals = []
                    for line in payslip_obj.fees_structure_id.line_ids:
                        line_vals.append({
                            'name' : line.name,
                            'code' : line.code,
                            'type' : line.type,
                            'amount' : line.amount
                        })
                    vals['line_ids'] = [(0, 0, val) for val in line_vals]
        return self.write(vals)

    _name = 'student.payslip'
    _description = 'Student PaySlip'

    fees_structure_id = fields.Many2one('student.fees.structure',
                                        'Fees Structure',
                                        readonly=True,
                                        states={'draft': [('readonly', False)]})
    standard_id = fields.Many2one('standard.standard', 'Class',
                                  readonly=True,
                                  states={'draft': [('readonly', False)]})
    division_id = fields.Many2one('standard.division', 'Division',
                                  readonly=True,
                                  states={'draft': [('readonly', False)]})
    medium_id = fields.Many2one('standard.medium', 'Medium',
                                readonly=True,
                                states={'draft': [('readonly', False)]})
    register_id = fields.Many2one('student.fees.register', 'Register',
                                  states={'paid': [('readonly', True)]})
    name = fields.Char('Description',
                       states={'paid': [('readonly', True)]})
    number = fields.Char('Number', readonly=True,
                         default=lambda obj: obj.env['ir.sequence'].
                         get('student.payslip'))
    student_id = fields.Many2one('student.student', 'Student', required=True,
                                 states={'paid': [('readonly', True)]})
    date = fields.Date('Date', readonly=True,
                       default=lambda * a: time.strftime('%Y-%m-%d'))
    line_ids = fields.One2many('student.payslip.line', 'slip_id',
                               'PaySlip Line',
                               states={'paid': [('readonly', True)]})
    total = fields.Float("Total", readonly=True)
    state = fields.Selection([('draft', 'Draft'), ('confirm', 'Confirm'),
                              ('payment_pending', 'Payment Pending'), 
                              ('paid', 'Paid')], 'State', readonly=True,
                             default='draft')
    journal_id = fields.Many2one('account.journal', 'Journal', required=True,
                                 states={'paid': [('readonly', True)]})
    currency_id = fields.Many2one('res.currency', 'Currency')
    move_id = fields.Many2one('account.move', 'Journal Entry', readonly=True,
                              select=1, ondelete='restrict',
                              help='Link to the automatically'
                              'generated Journal Items.')
    payment_date = fields.Date('Payment Date', readonly=True,
                               states={'draft': [('readonly', False)]},
                               select=True,
                               help='Keep empty to use the current date')
    type = fields.Selection([('out_invoice', 'Customer Invoice'),
                             ('in_invoice', 'Supplier Invoice'),
                             ('out_refund', 'Customer Refund'),
                             ('in_refund', 'Supplier Refund'),
                             ], 'Type', required=True, select=True,
                            change_default=True, default='out_invoice')
    company_id = fields.Many2one('res.company', 'Company', required=True,
                                 change_default=True, readonly=True,
                                 states={'draft': [('readonly', False)]},
                                 default=lambda obj_c: obj_c.env['res.users'].
                                 browse([obj_c._uid])[0].company_id)
    voucher_id = fields.Many2one('account.voucher', 'Payment Receipt', copy=False)

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
    @api.onchange('journal_id')
    def onchange_journal_id(self, journal_id=False):
        if self.journal_id:
            self.currency_id = self.journal_id.currency_id and\
                            self.journal_id.currency_id.id\
                            or self.journal_id.company_id.currency_id.id

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
                comapny_ac_id = fees.company_id.partner_id.\
                                property_account_receivable.id
            elif fees.type in ('out_invoice', 'in_refund'):
                account_id = fees.student_id.property_account_receivable.id
                comapny_ac_id = fees.company_id.\
                                partner_id.property_account_payable.id
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
        voucher_obj = self.env['account.voucher']
        for payslip in self:
            line_vals = []
            for line in payslip.line_ids:
                line_vals.append({
                    'name' : line.name,
                    'account_id' : 12,
                    'price_unit' : line.amount
                })
            voucher_vals = {
                'partner_id' : payslip.student_id.partner_id.id,
                'amount' : payslip.total,
                'name' : payslip.name,
                'account_id' : payslip.student_id.partner_id\
        and payslip.student_id.partner_id.property_account_receivable_id\
        and payslip.student_id.partner_id.property_account_receivable_id.id,
                'invoice_type' : 'out_invoice',
                'type' : 'receipt',
                'voucher_type' : 'sale',
                'journal_id' : payslip.journal_id.id,
                'close_after_process': True,
                'line_ids' : [(0,0, vals) for vals in line_vals]
            }
            voucher_id = voucher_obj.with_context({
                            'default_partner_id':
                            payslip.student_id.partner_id.id,
                            'default_amount': payslip.total,
                            'default_name': payslip.name,
                            'close_after_process': True,
                            'invoice_type': 'out_invoice',
                            'default_type': 'receipt',
                            'type': 'receipt'
                        }).create(voucher_vals)
            
            payslip.write({'state': 'payment_pending',
                               'voucher_id' : voucher_id.id})
            data_id = self.env['ir.model.data']._get_id(\
                            'account_voucher','view_sale_receipt_form')
            data = self.env['ir.model.data'].browse(data_id)
            view_id = data.res_id
            return {'name': _("Pay Fees"),
                    'view_mode': 'form',
                    'res_id' : voucher_id.id,
                    'view_id': view_id, 'view_type': 'form',
                    'res_model': 'account.voucher',
                    'type': 'ir.actions.act_window',
                    'nodestroy': True, 'target': 'current',
                    'domain': '[]',
            }

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
