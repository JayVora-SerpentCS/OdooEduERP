# See LICENSE file for full copyright and licensing details.

from odoo import fields, models


class LibraryEditorSupplier(models.Model):
    """Defining Library Editor Supplier."""

    _name = "library.editor.supplier"
    _description = "Editor Relations"

    name = fields.Many2one("res.partner", "Editor", help="Select editor")
    supplier_id = fields.Many2one("res.partner", "Supplier",
        help="Select supplier")
    sequence = fields.Integer("Sequence", help="Enter sequence")
    delay = fields.Integer("Customer Lead Time", help="Customer lead time")
    min_qty = fields.Float("Minimal Quantity", help="Minimal quantity")
    junk = fields.Text(compute_=lambda self: {idn: "" for idn in self.ids},
                       method=True, string="Ref", type="text")
