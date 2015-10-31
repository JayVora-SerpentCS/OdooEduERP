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

from openerp import models, api


class update_prices(models.TransientModel):

    _name = "update.prices"

    @api.multi
    def action_update_prices(self):
#         product_obj = self.env['product.product']
        lib_price_categ_obj = self.env['library.price.category']
        for cat in lib_price_categ_obj.browse(self._context.get
                                                        ('active_ids', False)):
            prod_ids = [x for x in cat.product_ids]
            if prod_ids:
                for prod_line in prod_ids:
                    prod_line.write({'list_price': cat.price})
        return {}
