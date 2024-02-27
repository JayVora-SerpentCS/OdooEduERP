# See LICENSE file for full copyright and licensing details.

from odoo import fields, models


class ResPartner(models.Model):
    _inherit = "res.partner"

    use_parent_address = fields.Boolean(
        help="Avtivate/Deactivate as per use of parent address",
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

    lot_id = fields.Many2one(
        "stock.lot", "Production Lot", help="Select Production lot"
    )
    customer_ref = fields.Char(string="Customer reference", help="Customer reference")


class AccountPaymentRegister(models.TransientModel):
    _inherit = "account.payment.register"

    def action_create_payments(self):
        """
        Override method to write paid amount in for library fine
        """
        res = super(AccountPaymentRegister, self).action_create_payments()
        invoice = False
        if self._context.get("active_model") == "account.move":
            invoice = self.env["account.move"].browse(
                self._context.get("active_ids", [])
            )
        if invoice.book_issue_id and invoice.payment_state == "paid":
            invoice.book_issue_id.penalty = 0.00
            invoice.book_issue_id.lost_penalty = 0.00
            invoice.book_issue_id.state = "paid"
        return res
