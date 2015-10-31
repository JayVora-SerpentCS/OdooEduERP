# -*- encoding: UTF-8 -*-
# -----------------------------------------------------------------------------
#
#    OpenERP, Open Source Management Solution
#    Copyright (C) 2012-Today Serpent Consulting Services PVT. LTD.
#    (<http://www.serpentcs.com>)
#
#    This program is free software: you can redistribute it and/or modify
#    it under the terms of the GNU General Public License as published by
#    the Free Software Foundation, either version 3 of the License, or
#    (at your option) any later version.
#
#    This program is distributed in the hope that it will be useful,
#    but WITHOUT ANY WARRANTY; without even the implied warranty of
#    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#    GNU General Public License for more details.
#
#    You should have received a copy of the GNU General Public License
#    along with this program.  If not, see <http://www.gnu.org/licenses/>
#
# -----------------------------------------------------------------------------

from openerp import models, fields, api, _
from openerp.exceptions import Warning


class card_number(models.TransientModel):

    _name = "card.number"
    _description = "Card Number"

    card_id = fields.Many2one("library.card", "Card No", required=True)

    @api.multi
    def card_number_ok(self):
        lib_book_obj = self.env['library.book.issue']
        for rec in self:
            search_card_ids = lib_book_obj.search([
                                ('card_id', '=', rec.card_id.id)])
            if not search_card_ids:
                raise Warning(_('Invalid Card Number.'))
            else:
                return {
                    'type': 'ir.actions.act_window',
                    'res_model': 'book.name',
                    'src_model': 'library.book.issue',
                    'target': 'new',
                    'view_mode': 'form',
                    'view_type': 'form',
                    'context': {'default_card_id': rec.card_id.id}
                }
