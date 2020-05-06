# See LICENSE file for full copyright and licensing details.

from odoo import models, fields


class ResPartner(models.Model):
    _inherit = 'res.partner'

    use_parent_address = fields.Boolean('Use Parent Address')


class AccountMove(models.Model):
    _inherit = 'account.move'

    book_issue = fields.Many2one('library.book.issue', 'Book issue')
    book_issue_reference = fields.Char('Book Issue Ref')


class AccountMoveLine(models.Model):

    _inherit = 'account.move.line'

    production_lot_id = fields.Many2one('stock.production.lot',
                                        'Production Lot')
    customer_ref = fields.Char('Customer reference')


class AccountPayment(models.Model):
    _inherit = "account.payment"

    def post(self):
        '''Override method to change state when invoice is paid'''
        res = super(AccountPayment, self).post()
        for rec in self:
            for invoice in rec.invoice_ids:
                if invoice.book_issue and invoice.invoice_payment_state == 'paid':
                    invoice.book_issue.write({'state': 'paid'})
        return res
