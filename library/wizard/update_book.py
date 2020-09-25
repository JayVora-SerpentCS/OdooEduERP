# See LICENSE file for full copyright and licensing details.

from odoo import _, fields, models
from odoo.exceptions import ValidationError


class UpdateBooks(models.TransientModel):
    """Defining update books."""

    _name = "update.books"
    _description = "Update Books"

    name = fields.Many2one(
        "product.product", "Book Name", required=True, help="Book name"
    )

    def action_update_books(self):
        lib_book_obj = self.env["library.book.issue"]
        for rec in self:
            if self._context.get("active_ids"):
                for active_id in self._context.get("active_ids"):
                    book_rec = lib_book_obj.browse(active_id)
                    book_rec.name = rec.name.id
                    if rec.name.availability == "notavailable":
                        raise ValidationError(
                            _(
                                """This Book is not available! \
Please try after sometime !"""
                            )
                        )
