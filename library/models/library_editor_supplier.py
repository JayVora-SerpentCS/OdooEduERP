# See LICENSE file for full copyright and licensing details.

from odoo import models, fields


class LibraryEditorSupplier(models.Model):
    """Defining Library Editor Supplier."""

    _name = "library.editor.supplier"
    _description = "Editor Relations"

    name = fields.Many2one('res.partner', 'Editor')
    supplier_id = fields.Many2one('res.partner', 'Supplier')
    sequence = fields.Integer('Sequence')
    delay = fields.Integer('Customer Lead Time')
    min_qty = fields.Float('Minimal Quantity')
    junk = fields.Text(compute_=lambda self: dict([(idn, '')
                       for idn in self.ids]),
                       method=True, string=" ", type="text")
