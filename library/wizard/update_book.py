# See LICENSE file for full copyright and licensing details.

from odoo import models, fields, _
from odoo.exceptions import ValidationError


class UpdateBooks(models.TransientModel):
    """Defining update books."""

    _name = "update.books"
    _description = "Update Books"

    name = fields.Many2one('product.product', 'Book Name', required=True)

    def action_update_books(self):
        lib_book_obj = self.env['library.book.issue']
        for rec in self:
            for active_id in self._context.get('active_ids'):
                book_rec = lib_book_obj.browse(active_id)
                if rec.name.availability == 'notavailable':
                    raise ValidationError(_(
"This Book is not available! Please try after sometime!"))
                else:
                    book_rec.name = rec.name.id
