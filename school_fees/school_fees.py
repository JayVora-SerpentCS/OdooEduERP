# -*- encoding: utf-8 -*-
##############################################################################
#
#    OpenERP, Open Source Management Solution
#    Copyright (C) 2004-2009 Tiny SPRL (<http://tiny.be>).
#    Copyright (C) 2011-2012 Serpent Consulting Services (<http://www.serpentcs.com>)
#    Copyright (C) 2013-2014 Serpent Consulting Services (<http://www.serpentcs.com>)
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
import time
from openerp import workflow
from openerp import models, fields, api, _
from openerp.exceptions import except_orm, Warning, RedirectWarning

class student_fees_register(models.Model):
    """
    Student fees Register
    """
    _name = 'student.fees.register'
    _description = 'Student fees Register'

    name  = fields.Char('Name', size=64, required=True, states={'confirm':[('readonly', True)]})
    date = fields.Date('Date', required=True, states={'confirm':[('readonly', True)]},default=lambda * a: time.strftime('%Y-%m-%d'))
    number = fields.Char('Number', size=64, readonly=True,default=lambda obj:obj.env['ir.sequence'].get('student.fees.register'))
    line_ids = fields.One2many('student.payslip', 'register_id', 'Payslips', states={'confirm':[('readonly', True)]})
    total_amount = fields.Float("Total", readonly=True)
    state = fields.Selection([('draft', 'Draft'), ('confirm', 'Confirm')], 'State', readonly=True,default='draft')
    journal_id = fields.Many2one('account.journal', 'Journal', required=True, states={'confirm':[('readonly', True)]})
    period_id = fields.Many2one('account.period', 'Force Period', required=True, domain=[('state', '<>', 'done')],states={'confirm':[('readonly', True)]}, help="Keep empty to use the period of the validation(invoice) date.")
    company_id = fields.Many2one('res.company', 'Company', required=True, change_default=True, readonly=True, states={'draft':[('readonly', False)]},default=lambda self, cr, uid, c: self.pool.get('res.users').browse(cr, uid, [uid], c)[0].company_id.id)
    
    @api.multi
    def fees_register_draft(self):
        self.write({'state' : 'draft'})
        return True
    
    @api.multi
    def fees_register_confirm(self):
        
        student_pool = self.env['student.student']
        slip_pool = self.env['student.payslip']
        student_ids = student_pool.search([])
        for vals in self.browse(self.ids):
            for stu in student_ids:
                old_slips = slip_pool.search([('student_id', '=', stu.id), ('date', '=', vals.date)])
                if old_slips:
                    old_slips.write({'register_id':vals.id})
                    for sid in old_slips:
                        workflow.trg_validate(self._uid, 'student.payslip', sid, 'payslip_confirm', self._cr)
                else:
                    res = {
                        'student_id':stu.id,
                        'register_id':vals.id,
                        'name':vals.name,
                        'date':vals.date,
                        'journal_id': vals.journal_id.id,
                        'period_id': vals.period_id.id,
                        'company_id': vals.company_id.id
                    }
                    slip_id = slip_pool.create(res)
                    workflow.trg_validate(self._uid, 'student.payslip', slip_id, 'payslip_confirm', self._cr)
            amount = 0
            for datas in self.browse(self.ids):
                for data in datas.line_ids:
                    amount = amount + data.total
                student_fees_register_vals = {'total_amount':amount}
                datas.write(student_fees_register_vals)
        self.write({'state' : 'confirm'})
        return True

    
#    def fees_register_confirm(self, cr, uid, ids, context=None):
#        ''' This method confirm fees registration
#        @param self : Object Pointer
#        @param cr : Database Cursor
#        @param uid : Current Logged in User
#        @param ids : Current Records
#        @param context : standard Dictionary
#        @return : True 
#        '''
#        
#        student_pool = self.pool.get('student.student')
#        slip_pool = self.pool.get('student.payslip')
#        if context is None:
#            context = {}
#        student_ids = student_pool.search(cr, uid, [], context=context)
#        for vals in self.browse(cr, uid, ids, context=context):
#            for stu in student_pool.browse(cr, uid, student_ids, context=context):
#                old_slips = slip_pool.search(cr, uid, [('student_id', '=', stu.id), ('date', '=', vals.date)], context=context)
#                if old_slips:
#                    slip_pool.write(cr, uid, old_slips, {'register_id':vals.id}, context=context)
#                    for sid in old_slips:
#                        workflow.trg_validate(uid, 'student.payslip', sid, 'payslip_confirm', cr)
#                else:
#                    res = {
#                        'student_id':stu.id,
#                        'register_id':vals.id,
#                        'name':vals.name,
#                        'date':vals.date,
#                        'journal_id': vals.journal_id.id,
#                        'period_id': vals.period_id.id,
#                        'company_id': vals.company_id.id
#                    }
#                    slip_id = slip_pool.create(cr, uid, res, context=context)
#                    workflow.trg_validate(uid, 'student.payslip', slip_id, 'payslip_confirm', cr)
#                    
#            amount = 0
#            for datas in self.browse(cr, uid, ids, context=context):
#                for data in datas.line_ids:
#                    amount = amount + data.total
#                student_fees_register_vals = {'total_amount':amount}
#                self.write(cr, uid, datas.id, student_fees_register_vals, context=context)
#        self.write(cr, uid, ids, {'state' : 'confirm'}, context=context)
#        return True

class student_payslip_line(models.Model):
    '''
    Student Payslip Line
    '''
    _name = 'student.payslip.line'
    _description = 'Student Payslip Line'

    name = fields.Char('Name', size=256, required=True)
    code = fields.Char('Code', size=64, required=True)
    type = fields.Selection([
        ('month', 'Monthly'),
        ('year', 'Yearly'),
        ('range', 'Range'),
    ], 'Duration', select=True, required=True)
    amount = fields.Float('Amount', digits=(16, 4))
    line_ids = fields.One2many('student.payslip.line.line', 'slipline_id', 'Calculations')
    slip_id = fields.Many2one('student.payslip', 'Pay Slip')
    description = fields.Text('Description')

class student_fees_structure_line(models.Model):
    '''
    Student Fees Structure Line
    '''
    _name = 'student.fees.structure.line'
    _description = 'Student Fees Structure Line'
    _order = 'sequence'

    name = fields.Char('Name', size=256, required=True)
    code = fields.Char('Code', size=64, required=True)
    type = fields.Selection([
        ('month', 'Monthly'),
        ('year', 'Yearly'),
        ('range', 'Range'),
    ], 'Duration', select=True, required=True)
    amount = fields.Float('Amount', digits=(16, 4))
    sequence = fields.Integer('Sequence')
    line_ids = fields.One2many('student.payslip.line.line', 'slipline1_id', 'Calculations')

class student_fees_structure(models.Model):
    """
    Fees structure
    """
    _name = 'student.fees.structure'
    _description = 'Student Fees Structure'
    
    name = fields.Char('Name', size=256, required=True)
    code = fields.Char('Code', size=64, required=True)
    line_ids = fields.Many2many('student.fees.structure.line', 'fees_structure_payslip_rel', 'fees_id', 'slip_id', 'Fees Structure')
    
    _sql_constraints = [
        ('code_uniq','unique(code)', 'The code of the Fees Structure must be unique !')
    ]

class student_payslip(models.Model):

    @api.multi
    def payslip_draft(self):
        self.write({'state' : 'draft'})
        return True
    
    @api.multi
    def payslip_paid(self):
        self.write({'state' : 'paid'})
        return True
    
    @api.multi
    def payslip_confirm(self):
        
        student_fees_structure_obj = self.env['student.fees.structure']
        student_payslip_line_obj = self.env['student.payslip.line']
        for student_payslip_datas in self.read(['fees_structure_id']):
            if not student_payslip_datas['fees_structure_id']:
                self.write({'state' : 'paid'})   
                return True
            student_fees_structure_domain = [('name', '=', student_payslip_datas['fees_structure_id'][1])]
            student_fees_structure_search_ids = student_fees_structure_obj.search(student_fees_structure_domain)
            for datas in student_fees_structure_search_ids:
                for data in datas.line_ids or []:
                    student_payslip_line_vals = {
                            'slip_id':self.id,
                            'name':data.name,
                            'code':data.code,
                            'sequence':data.sequence,
                            'type':data.type,
                            'amount':data.amount,
                    }
                    student_payslip_line_obj.create(student_payslip_line_vals)
            amount = 0
            for datas in self.browse(self.ids):
                for data in datas.line_ids:
                    amount = amount + data.amount
                student_payslip_vals = {'total':amount}
                datas.write(student_payslip_vals)
        self.write({'state' : 'confirm'})
        return True

    _name = 'student.payslip'
    _description = 'Student Payslip'


    fees_structure_id = fields.Many2one('student.fees.structure', 'Fees Structure', states={'paid':[('readonly', True)]})
    standard_id = fields.Many2one('standard.standard', 'Class')
    division_id = fields.Many2one('standard.division', 'Division')
    medium_id = fields.Many2one('standard.medium', 'Medium')
    register_id = fields.Many2one('student.fees.register', 'Register', states={'paid':[('readonly', True)]})
    name = fields.Char('Description', size=64, states={'paid':[('readonly', True)]})
    number = fields.Char('Number', size=64, readonly=True,default=lambda obj:obj.env['ir.sequence'].get('student.payslip'))
    student_id = fields.Many2one('student.student', 'Student', required=True, states={'paid':[('readonly', True)]})
    date = fields.Date('Date', readonly=True,default=lambda * a: time.strftime('%Y-%m-%d'))
    line_ids = fields.One2many('student.payslip.line', 'slip_id', 'Payslip Line', states={'paid':[('readonly', True)]})
    total = fields.Float("Total", readonly=True)
    state = fields.Selection([('draft', 'Draft'), ('confirm', 'Confirm'), ('paid', 'Paid')], 'State', readonly=True,default='draft')
    journal_id = fields.Many2one('account.journal', 'Journal', required=True, states={'paid':[('readonly', True)]})
    currency_id = fields.Many2one('res.currency', 'Currency')
    move_id = fields.Many2one('account.move', 'Journal Entry', readonly=True, select=1, ondelete='restrict', help="Link to the automatically generated Journal Items.")
    payment_date = fields.Date('Payment Date', readonly=True, states={'draft':[('readonly', False)]}, select=True, help="Keep empty to use the current date")
    type = fields.Selection([
        ('out_invoice', 'Customer Invoice'),
        ('in_invoice', 'Supplier Invoice'),
        ('out_refund', 'Customer Refund'),
        ('in_refund', 'Supplier Refund'),
        ], 'Type', required=True, select=True, change_default=True,default='out_invoice')
    
    company_id = fields.Many2one('res.company', 'Company', required=True, change_default=True, readonly=True, states={'draft':[('readonly', False)]})
    period_id = fields.Many2one('account.period', 'Force Period', required=True, domain=[('state', '<>', 'done')], help="Keep empty to use the period of the validation(invoice) date.")

    _sql_constraints = [
        ('code_uniq','unique(student_id,date,state)', 'The code of the Fees Structure must be unique !')
    ]
   
    @api.model   
    def copy(self):
        if default is None:
            default =  {}
        default.update({
            'state':'draft',
            'number':False,
            'move_id':False,
            'line_ids':[],
        })
        return super(student_payslip, self).copy(default)

    @api.multi
    def onchange_journal_id(self,journal_id=False):
        
        result = {}
        if journal_id:
            journal = self.env['account.journal'].browse(journal_id)
            currency_id = journal.currency and journal.currency.id or journal.company_id.currency_id.id
            result = {'value': {
                    'currency_id': currency_id,
                    }
                }
        return result
    
    @api.multi
    def action_move_create(self):
        cur_obj = self.env['res.currency']
        move_obj = self.env['account.move']
        move_line_obj = self.env['account.move.line']
        for fees in self.browse(self.ids):
            if not fees.journal_id.sequence_id:
                raise except_orm(_('Error !'), _('Please define sequence on the journal related to this invoice.'))
            if fees.move_id:
                continue
            ctx = self._context.copy()
            ctx.update({'lang': fees.student_id.lang})
            if not fees.payment_date:
                self.write(cr, uid, [fees.id], {'payment_date':time.strftime('%Y-%m-%d')})
            company_currency = fees.company_id.currency_id.id
            diff_currency_p = fees.currency_id.id <> company_currency
            current_currency = fees.currency_id and fees.currency_id.id or company_currency
            account_id = False
            comapny_ac_id = False
            if fees.type in ('in_invoice', 'out_refund'):
                account_id = fees.student_id.property_account_payable.id
                comapny_ac_id = fees.company_id.partner_id.property_account_receivable.id
            elif fees.type in ('out_invoice', 'in_refund'):
                account_id = fees.student_id.property_account_receivable.id
                comapny_ac_id = fees.company_id.partner_id.property_account_payable.id
            if fees.journal_id.centralisation:
                raise except_orm(_('UserError'),
                        _('You cannot create an invoice on a centralised journal. Uncheck the centralised counterpart box in the related journal from the configuration menu.'))
            move = {
                'ref': fees.name,
                'journal_id': fees.journal_id.id,
                'date': fees.payment_date or time.strftime('%Y-%m-%d'),
            }
            ctx.update({'company_id': fees.company_id.id})
            move_id = move_obj.create(move)
            context_multi_currency = self._context.copy()
            context_multi_currency.update({'date': time.strftime('%Y-%m-%d')})
            debit = 0.0
            credit = 0.0
            if fees.type in ('in_invoice', 'out_refund'):
                credit = cur_obj.compute(self._cr, self._uid, fees.currency_id.id, company_currency, fees.total, context=context_multi_currency)
            elif fees.type in ('out_invoice', 'in_refund'):
                debit = cur_obj.compute(self._cr, self._uid, fees.currency_id.id, company_currency, fees.total, context=context_multi_currency)
            if debit < 0:
                credit = -debit
                debit = 0.0
            if credit < 0:
                debit = -credit
                credit = 0.0
            sign = debit - credit < 0 and - 1 or 1
            move_line = {
                'name': fees.name or '/',
                'move_id': move_id,
                'debit': debit,
                'credit': credit,
                'account_id': account_id,
                'journal_id': fees.journal_id.id,
                'parent_id': fees.student_id.parent_id.id,
                'period_id': fees.period_id.id,
                'currency_id': diff_currency_p and  current_currency or False,
                'amount_currency': diff_currency_p and sign * fees.total or 0.0,
                'date': fees.payment_date or time.strftime('%Y-%m-%d'),
            }
            move_line_obj.create(move_line)
            move_line = {
                'name': fees.name or '/',
                'move_id': move_id,
                'debit': credit,
                'credit': debit,
                'account_id': comapny_ac_id,
                'journal_id': fees.journal_id.id,
                'parent_id': fees.student_id.parent_id.id,
                'period_id': fees.period_id.id,
                'currency_id': diff_currency_p and  current_currency or False,
                'amount_currency': diff_currency_p and sign * fees.total or 0.0,
                'date': fees.payment_date or time.strftime('%Y-%m-%d'),
            }
            move_line_obj.create(move_line)
            fees.write({'move_id': move_id})
            move_obj.post([move_id])
        return True
    
    @api.multi
    def student_pay_fees(self):
        self.write({'state' : 'paid'})
        if not self.ids: return []
        fees = self.browse(self.id)
        return {
        'name':_("Pay Fees"),
            'view_mode': 'form',
            'view_id': False,
            'view_type': 'form',
            'res_model': 'account.voucher',
            'type': 'ir.actions.act_window',
            'nodestroy': True,
            'target': 'current',
            'domain': '[]',
            'context': {
                'default_partner_id': fees.student_id.partner_id.id,
                'default_amount': fees.total,
                'default_name':fees.name,
                'close_after_process': True,
                'invoice_type': 'out_invoice',
                'default_type': 'receipt',
                'type': 'receipt'
            }
        }

class student_payslip_line_line(models.Model):
    '''
    Function Line
    '''
    _name = 'student.payslip.line.line'
    _description = 'Function Line'
    _order = 'sequence'
    slipline_id = fields.Many2one('student.payslip.line', 'Slip Line')
    slipline1_id = fields.Many2one('student.fees.structure.line', 'Slip Line')
    sequence = fields.Integer('Sequence')
    from_month = fields.Many2one('academic.month', 'From Month')
    to_month = fields.Many2one('academic.month', 'To Month')

# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4:
