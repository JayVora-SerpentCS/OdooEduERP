# -*- coding: utf-8 -*-
# Part of Odoo. See LICENSE file for full copyright and licensing details.

from openerp import models, fields, api


class BookName(models.TransientModel):

    _name = "book.name"
    _description = "Book Name"

    name = fields.Many2one('product.product', 'Book Name', required=True)
    card_id = fields.Many2one("library.card", "Card No", required=True)

    @api.multi
    def create_new_books(self):
        for rec in self:
            rec.create({'name': rec.name.id, 'card_id': rec.card_id.id})
        return {}
