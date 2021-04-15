# See LICENSE file for full copyright and licensing details.

from odoo import fields, models


class ResPartner(models.Model):
    _inherit = "res.partner"

    use_parent_address = fields.Boolean(
        "Use Parent Address",
        help="""Avtivate/Deactivate as per use
        of parent address""",
    )


class AccountMove(models.Model):
    _inherit = "account.move"

    book_issue_id = fields.Many2one(
        "library.book.issue", "Book issue", help="Select book issue"
    )
    book_issue_reference = fields.Char(
        "Book Issue Ref", help="Enter book issue reference"
    )


class AccountMoveLine(models.Model):

    _inherit = "account.move.line"

    production_lot_id = fields.Many2one("stock.production.lot",
                            "Production Lot", help="Select Production lot")
    customer_ref = fields.Char("Customer reference", help="Customer reference")


class AccountPayment(models.Model):
    _inherit = "account.payment"

    def action_post(self):
        """Override method to change state when invoice is paid"""
        res = super(AccountPayment, self).action_post()
        for rec in self:
            invoice = rec.move_id
            if invoice.book_issue_id and invoice.payment_state == "paid":
                invoice.book_issue_id.state = "paid"
        return res
