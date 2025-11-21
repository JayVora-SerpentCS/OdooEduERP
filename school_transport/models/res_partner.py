from odoo import fields, models


class ResPartner(models.Model):
    _inherit = "res.partner"

    is_driver = fields.Boolean(
        "Vehicle Driver",
        help="""Activate if thefollowing person is driver""",
    )
