# -*- coding: utf-8 -*-
# Part of Odoo. See LICENSE file for full copyright and licensing details.

from openerp import models, api


class update_prices(models.TransientModel):
    _name = "update.prices"

    @api.multi
    def action_update_prices(self):
        lib_price_categ_obj = self.env['library.price.category']
        active_ids = self._context.get('active_ids', False)
        for cat in lib_price_categ_obj.browse(active_ids):
            prod_ids = [x for x in cat.product_ids]
            if prod_ids:
                for prod_line in prod_ids:
                    prod_line.write({'list_price': cat.price})
        return {}
