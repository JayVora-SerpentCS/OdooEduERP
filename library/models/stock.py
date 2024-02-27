# See LICENSE file for full copyright and licensing details.

from odoo import fields, models


class StockMove(models.Model):
    _inherit = "stock.move"

    origin_ref = fields.Char(string="Origin")


class StockPicking(models.Model):
    _inherit = "stock.picking"
    _order = "create_date desc"

    date_done = fields.Datetime("Picking date")
