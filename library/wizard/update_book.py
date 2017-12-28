# -*- coding: utf-8 -*-
# See LICENSE file for full copyright and licensing details.

from odoo import models, fields, api, _
from odoo.exceptions import ValidationError


class UpdateBooks(models.TransientModel):
    _name = "update.books"
    _description = "Update Books"

    name = fields.Many2one('product.product', 'Book Name', required=True)

    @api.multi
    def action_update_books(self):
        lib_book_obj = self.env['library.book.issue']
        for rec in self:
            if self._context.get('active_ids'):
                for active_id in self._context.get('active_ids'):
                    book_rec = lib_book_obj.browse(active_id)
                    if rec.name.availability == 'notavailable':
                        raise ValidationError(_('''This Book is not available!
                        Please try after sometime !'''))
                    else:
                        book_rec.browse(active_id).write({'name': rec.name.id})
        return {}
