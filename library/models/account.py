# -*- coding: utf-8 -*-
# See LICENSE file for full copyright and licensing details.

from odoo import models, fields


class ResPartner(models.Model):
    _inherit = 'res.partner'

    use_parent_address = fields.Boolean('Use Parent Address')


class AccountInvoiceLine(models.Model):

    _inherit = 'account.invoice.line'

    production_lot_id = fields.Many2one('stock.production.lot',
                                        'Production Lot')
    customer_ref = fields.Char('Customer reference')
