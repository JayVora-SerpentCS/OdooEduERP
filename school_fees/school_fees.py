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
from openerp.osv import osv, fields
import time
from openerp import workflow
from openerp.tools.translate import _

class student_fees_register(osv.Model):
    """
    Student fees Register
    """
    _name = 'student.fees.register'
    _description = 'Student fees Register'

    _columns = {
        'name':fields.char('Name', size=64, required=True, states={'confirm':[('readonly', True)]}),
        'date': fields.date('Date', required=True, states={'confirm':[('readonly', True)]}),
        'number':fields.char('Number', size=64, readonly=True),
        'line_ids':fields.one2many('student.payslip', 'register_id', 'Payslips', states={'confirm':[('readonly', True)]}),
        'total_amount': fields.float("Total", readonly=True),
        'state':fields.selection([('draft', 'Draft'), ('confirm', 'Confirm')], 'State', readonly=True),
        'journal_id': fields.many2one('account.journal', 'Journal', required=True, states={'confirm':[('readonly', True)]}),
        'period_id': fields.many2one('account.period', 'Force Period', required=True, domain=[('state', '<>', 'done')],states={'confirm':[('readonly', True)]}, help="Keep empty to use the period of the validation(invoice) date."),
        'company_id': fields.many2one('res.company', 'Company', required=True, change_default=True, readonly=True, states={'draft':[('readonly', False)]}),
    }
    _defaults = {
        'number': lambda obj, cr, uid, context:obj.pool.get('ir.sequence').get(cr, uid, 'student.fees.register'),
        'date': lambda * a: time.strftime('%Y-%m-%d'),
        'state':'draft',
        'company_id':lambda self, cr, uid, c: self.pool.get('res.users').browse(cr, uid, [uid], c)[0].company_id.id,
    }

    def fees_register_draft(self, cr, uid, ids, context=None):
        ''' This method draft fees registration
        @param self : Object Pointer
        @param cr : Database Cursor
        @param uid : Current Logged in User
        @param ids : Current Records
        @param context : standard Dictionary
        @return : True 
        '''
        self.write(cr, uid, ids, {'state' : 'draft'}, context=context)
        return True

    def fees_register_confirm(self, cr, uid, ids, context=None):
        ''' This method confirm fees registration
        @param self : Object Pointer
        @param cr : Database Cursor
        @param uid : Current Logged in User
        @param ids : Current Records
        @param context : standard Dictionary
        @return : True 
        '''
        
        student_pool = self.pool.get('student.student')
        slip_pool = self.pool.get('student.payslip')
        if context is None:
            context = {}
        student_ids = student_pool.search(cr, uid, [], context=context)
        for vals in self.browse(cr, uid, ids, context=context):
            for stu in student_pool.browse(cr, uid, student_ids, context=context):
                old_slips = slip_pool.search(cr, uid, [('student_id', '=', stu.id), ('date', '=', vals.date)], context=context)
                if old_slips:
                    slip_pool.write(cr, uid, old_slips, {'register_id':vals.id}, context=context)
                    for sid in old_slips:
                        workflow.trg_validate(uid, 'student.payslip', sid, 'payslip_confirm', cr)
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
                    slip_id = slip_pool.create(cr, uid, res, context=context)
                    workflow.trg_validate(uid, 'student.payslip', slip_id, 'payslip_confirm', cr)
                    
            amount = 0
            for datas in self.browse(cr, uid, ids, context=context):
                for data in datas.line_ids:
                    amount = amount + data.total
                student_fees_register_vals = {'total_amount':amount}
                self.write(cr, uid, datas.id, student_fees_register_vals, context=context)
        self.write(cr, uid, ids, {'state' : 'confirm'}, context=context)
        return True

class student_payslip_line(osv.Model):
    '''
    Student Payslip Line
    '''
    _name = 'student.payslip.line'
    _description = 'Student Payslip Line'

    _columns = {
        'name':fields.char('Name', size=256, required=True),
        'code':fields.char('Code', size=64, required=True),
		'type':fields.selection([
            ('month', 'Monthly'),
            ('year', 'Yearly'),
            ('range', 'Range'),
        ], 'Duration', select=True, required=True),
        'amount': fields.float('Amount', digits=(16, 4)),
        'line_ids':fields.one2many('student.payslip.line.line', 'slipline_id', 'Calculations'),
        'slip_id':fields.many2one('student.payslip', 'Pay Slip'),
        'description': fields.text('Description')
    }

class student_fees_structure_line(osv.Model):
    '''
    Student Fees Structure Line
    '''
    _name = 'student.fees.structure.line'
    _description = 'Student Fees Structure Line'
    _order = 'sequence'

    _columns = {
        'name':fields.char('Name', size=256, required=True),
        'code':fields.char('Code', size=64, required=True),
        'type':fields.selection([
            ('month', 'Monthly'),
            ('year', 'Yearly'),
            ('range', 'Range'),
        ], 'Duration', select=True, required=True),
        'amount': fields.float('Amount', digits=(16, 4)),
        'sequence': fields.integer('Sequence'),
        'line_ids':fields.one2many('student.payslip.line.line', 'slipline1_id', 'Calculations'),
    }

class student_fees_structure(osv.Model):
    """
    Fees structure
    """
    _name = 'student.fees.structure'
    _description = 'Student Fees Structure'
    
    
    _columns = {
        'name':fields.char('Name', size=256, required=True),
        'code':fields.char('Code', size=64, required=True),
        'line_ids':fields.many2many('student.fees.structure.line', 'fees_structure_payslip_rel', 'fees_id', 'slip_id', 'Fees Structure'),    
    }
    _sql_constraints = [
        ('code_uniq','unique(code)', 'The code of the Fees Structure must be unique !')
    ]

class student_payslip(osv.Model):

    def payslip_draft(self, cr, uid, ids, context=None):
        ''' This method payslip in draft state
        @param self : Object Pointer
        @param cr : Database Cursor
        @param uid : Current Logged in User
        @param ids : Current Records
        @param context : standard Dictionary
        @return : True 
        '''
        
        self.write(cr, uid, ids, {'state' : 'draft'}, context=context)
        return True
    def payslip_paid(self, cr, uid, ids, context=None):
        ''' This method payslip in paid state
        @param self : Object Pointer
        @param cr : Database Cursor
        @param uid : Current Logged in User
        @param ids : Current Records
        @param context : standard Dictionary
        @return : True 
        '''
        
        self.write(cr, uid, ids, {'state' : 'paid'}, context=context)
        return True

    def payslip_confirm(self, cr, uid, ids, context=None):
        ''' This method confirm Payslip
        @param self : Object Pointer
        @param cr : Database Cursor
        @param uid : Current Logged in User
        @param ids : Current Records
        @param context : standard Dictionary
        @return : True 
        '''
        
        student_fees_structure_obj = self.pool.get('student.fees.structure')
        student_payslip_line_obj = self.pool.get('student.payslip.line')
        for student_payslip_datas in self.read(cr, uid, ids, ['fees_structure_id'], context=context):
            if not student_payslip_datas['fees_structure_id']:
                self.write(cr, uid, ids, {'state' : 'paid'}, context=context)   
                return True
            student_fees_structure_domain = [('name', '=', student_payslip_datas['fees_structure_id'][1])]     
            student_fees_structure_search_ids = student_fees_structure_obj.search(cr, uid, student_fees_structure_domain, context=context)
            for datas in student_fees_structure_obj.browse(cr, uid, student_fees_structure_search_ids, context=context):
                for data in datas.line_ids or []:
                    student_payslip_line_vals = {
                            'slip_id':ids[0],
                            'name':data.name,
                            'code':data.code,
                            'sequence':data.sequence,
                            'type':data.type,
                            'amount':data.amount,
                    }
                    student_payslip_line_obj.create(cr, uid, student_payslip_line_vals, context=context)
            amount = 0
            for datas in self.browse(cr, uid, ids, context=context):
                for data in datas.line_ids:
                    amount = amount + data.amount
                student_payslip_vals = {'total':amount}
                self.write(cr, uid, datas.id, student_payslip_vals, context=context)
        self.write(cr, uid, ids, {'state' : 'confirm'}, context=context)
        return True

    _name = 'student.payslip'
    _description = 'Student Payslip'

    _columns = {
        'fees_structure_id':fields.many2one('student.fees.structure', 'Fees Structure', states={'paid':[('readonly', True)]}),
        'standard_id':fields.many2one('standard.standard', 'Class'),
        'division_id':fields.many2one('standard.division', 'Division'),
        'medium_id':fields.many2one('standard.medium', 'Medium'),
        'register_id':fields.many2one('student.fees.register', 'Register', states={'paid':[('readonly', True)]}),
        'name':fields.char('Description', size=64, states={'paid':[('readonly', True)]}),
        'number':fields.char('Number', size=64, readonly=True),
        'student_id':fields.many2one('student.student', 'Student', required=True, states={'paid':[('readonly', True)]}),
        'date': fields.date('Date', readonly=True),
        'line_ids':fields.one2many('student.payslip.line', 'slip_id', 'Payslip Line', states={'paid':[('readonly', True)]}),
        'total': fields.float("Total", readonly=True),
        'state':fields.selection([('draft', 'Draft'), ('confirm', 'Confirm'), ('paid', 'Paid')], 'State', readonly=True),
        'journal_id': fields.many2one('account.journal', 'Journal', required=True, states={'paid':[('readonly', True)]}),
        'currency_id': fields.many2one('res.currency', 'Currency'),
        'move_id': fields.many2one('account.move', 'Journal Entry', readonly=True, select=1, ondelete='restrict', help="Link to the automatically generated Journal Items."),
        'payment_date': fields.date('Payment Date', readonly=True, states={'draft':[('readonly', False)]}, select=True, help="Keep empty to use the current date"),
        'type': fields.selection([
            ('out_invoice', 'Customer Invoice'),
            ('in_invoice', 'Supplier Invoice'),
            ('out_refund', 'Customer Refund'),
            ('in_refund', 'Supplier Refund'),
            ], 'Type', required=True, select=True, change_default=True),
        'company_id': fields.many2one('res.company', 'Company', required=True, change_default=True, readonly=True, states={'draft':[('readonly', False)]}),
        'period_id': fields.many2one('account.period', 'Force Period', required=True, domain=[('state', '<>', 'done')], help="Keep empty to use the period of the validation(invoice) date."),
    }
    _defaults = {
        'number': lambda obj, cr, uid, context:obj.pool.get('ir.sequence').get(cr, uid, 'student.payslip'),
        'date': lambda * a: time.strftime('%Y-%m-%d'),
        'state':'draft',
        'type': 'out_invoice',
    }
    _sql_constraints = [
        ('code_uniq','unique(student_id,date,state)', 'The code of the Fees Structure must be unique !')
    ]
    def copy(self, cr, uid, id, default=None, context=None):
        ''' This method Duplicate record with given id updating it with default values
        @param self : Object Pointer
        @param cr : Database Cursor
        @param uid : Current Logged in User
        @param id : id of the record to copy
        @param default : dictionary of field values to override in the original values of the copied record
        @param context : standard Dictionary
        @return : True 
        '''
        default = default or {}
        default.update({
            'state':'draft',
            'number':False,
            'move_id':False,
            'line_ids':[],
        })
        return super(student_payslip, self).copy(cr, uid, id, default, context)

    def onchange_journal_id(self, cr, uid, ids, journal_id=False):
        '''This method automatically change value of journal 
        @param self : Object Pointer
        @param cr : Database Cursor
        @param uid : Current Logged in User
        @param ids : Current Records
        @param journal_id : Apply method on this Field name
        @param context : standard Dictionary
        @return : Dictionary having identifier of the record as key and the value of journal
        '''
        
        result = {}
        if journal_id:
            journal = self.pool.get('account.journal').browse(cr, uid, journal_id)
            currency_id = journal.currency and journal.currency.id or journal.company_id.currency_id.id
            result = {'value': {
                    'currency_id': currency_id,
                    }
                }
        return result

    def action_move_create(self, cr, uid, ids, context=None):
        """Creates student related financial move lines
        @param self : Object Pointer
        @param cr : Database Cursor
        @param uid : Current Logged in User
        @param ids : Current Records
        @param context : standard Dictionary
        @return : True 
        """
        cur_obj = self.pool.get('res.currency')
        move_obj = self.pool.get('account.move')
        move_line_obj = self.pool.get('account.move.line')
        if context is None:
            context = {}
        for fees in self.browse(cr, uid, ids, context=context):
            if not fees.journal_id.sequence_id:
                raise osv.except_osv(_('Error !'), _('Please define sequence on the journal related to this invoice.'))
            if fees.move_id:
                continue
            ctx = context.copy()
            ctx.update({'lang': fees.student_id.lang})
            if not fees.payment_date:
                self.write(cr, uid, [fees.id], {'payment_date':time.strftime('%Y-%m-%d')}, context=ctx)
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
                raise osv.except_osv(_('UserError'),
                        _('You cannot create an invoice on a centralised journal. Uncheck the centralised counterpart box in the related journal from the configuration menu.'))
            move = {
                'ref': fees.name,
                'journal_id': fees.journal_id.id,
                'date': fees.payment_date or time.strftime('%Y-%m-%d'),
            }
            ctx.update({'company_id': fees.company_id.id})
            move_id = move_obj.create(cr, uid, move, context=ctx)
            context_multi_currency = context.copy()
            context_multi_currency.update({'date': time.strftime('%Y-%m-%d')})
            debit = 0.0
            credit = 0.0
            if fees.type in ('in_invoice', 'out_refund'):
                credit = cur_obj.compute(cr, uid, fees.currency_id.id, company_currency, fees.total, context=context_multi_currency)
            elif fees.type in ('out_invoice', 'in_refund'):
                debit = cur_obj.compute(cr, uid, fees.currency_id.id, company_currency, fees.total, context=context_multi_currency)
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
            move_line_obj.create(cr, uid, move_line, context)
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
            move_line_obj.create(cr, uid, move_line, context)
            self.write(cr, uid, [fees.id], {'move_id': move_id}, context=ctx)
            move_obj.post(cr, uid, [move_id], context=context)
        return True

    def student_pay_fees(self, cr, uid, ids, context=None):
        """Creates student related account voucher
        @param self : Object Pointer
        @param cr : Database Cursor
        @param uid : Current Logged in User
        @param ids : Current Records
        @param context : standard Dictionary
        @return : new form of account.voucher model
        """
        
        self.write(cr, uid, ids, {'state' : 'paid'}, context=context)
        if not ids: return []
        fees = self.browse(cr, uid, ids[0], context=context)
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

class student_payslip_line_line(osv.Model):
    '''
    Function Line
    '''
    _name = 'student.payslip.line.line'
    _description = 'Function Line'
    _order = 'sequence'
    _columns = {
        'slipline_id':fields.many2one('student.payslip.line', 'Slip Line'),
        'slipline1_id':fields.many2one('student.fees.structure.line', 'Slip Line'),
        'sequence':fields.integer('Sequence'),
        'from_month': fields.many2one('academic.month', 'From Month'),
        'to_month': fields.many2one('academic.month', 'To Month'),
    }

# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4:
