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
from openerp import models, fields, api

class fee_pay_wizard(models.TransientModel):
    _name = 'fee.pay.wizard'

    student_id = fields.Many2one('student.student', 'Student', required=True)
    journal_id = fields.Many2one('account.journal', 'Payment Method', required=True)
    period_id = fields.Many2one('account.period', 'Period', required=True)
    difference_amount = fields.Float('Difference Amount')
    date = fields.Date('Date', required=True)
    amount_pay = fields.Float('Paid Amount', required=True)

    @api.onchange('amount_pay')
    def onchange_amount_total(self):
        context = self._context
        if self.amount_pay > 0.00:
            diff_amount = context.get('amount_total', 0.00) - self.amount_pay
            self.difference_amount = diff_amount

    @api.multi
    def fee_pay(self):
        reg_obj = self.env['student.fees.register']
        receipt_obj = self.env['student.fee.receipt']
        context = self._context
        active_ids = context.get('active_ids', [])
        for reg in reg_obj.browse(active_ids):
            vals = {
                    'student_id': reg.student_id.id,
                    'class_id': reg.class_id.id,
                    'division_id': reg.division_id.id,
                    'year_id': reg.year_id.id,
                    'name': reg.name,
                    'date': self.date,
                    'journal_id': self.journal_id.id,
                    'period_id': self.period_id.id,
                    'company_id': reg.company_id.id,
                    'paid_amount': reg.paid_amount + self.amount_pay,
                    'remain_amount': reg.amount_total - (reg.paid_amount + self.amount_pay),
                    'amount_total': reg.amount_total,
#                    'change_amount': reg.paid_amount - reg.amount_total,
                    'currency_id': reg.currency_id.id,
                    'fees_register_id': reg.id,
                    }
            print "Vals::::",vals
            reg.write({'paid_amount': reg.paid_amount + self.amount_pay, 'remain_amount': reg.amount_total - (reg.paid_amount + self.amount_pay)})
            if reg.paid_amount == reg.amount_total:
                reg.write({'state': 'paid'})
            else:
                reg.write({'state': 'open'})
            if reg.paid_amount > reg.amount_total:
                vals.update({'change_amount': reg.paid_amount - reg.amount_total, 'remain_amount': 0.00})
                reg.write({'change_amount': reg.paid_amount - reg.amount_total, 'state': 'paid', 'remain_amount': 0.00})
            receipt_obj.create(vals)
        return True