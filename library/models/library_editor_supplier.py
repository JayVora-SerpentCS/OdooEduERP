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
from openerp import tools
from openerp.exceptions import Warning


class library_editor_supplier(models.Model):

    _name = "library.editor.supplier"
    _description = "Editor Relations"
    _auto = False

    name = fields.Many2one('res.partner', 'Editor')
    supplier_id = fields.Many2one('res.partner', 'Supplier')
    sequence = fields.Integer('Sequence')
    delay = fields.Integer('Customer Lead Time')
    min_qty = fields.Float('Minimal Quantity')
    junk = fields.Text(compute=lambda self: dict([(idn, '')
                           for idn in self.ids]),
                       method=True, string=" ", type="text")

    @api.model
    @api.returns('self', lambda value: value)
    def create(self, vals):
        if not (vals['name'] and vals['supplier_id']):
            raise Warning(_("Error ! Please provide proper Information"))
        # search for books of these editor not already linked
        # with this supplier:
        select = """select product_tmpl_id\n"""\
                 """from product_product\n"""\
                 """where editor = %s\n"""\
                 """  and id not in (select product_tmpl_id\
                 from product_supplierinfo where name = %s)"""\
                 % (vals['name'], vals['supplier_id'])
        self._cr.execute(select)
        if not self._cr.rowcount:
            raise Warning(_("Error ! No book to apply this relation"))

        sup_info = self.env['product.supplierinfo']
        last_id = 0
        for book_id in self._cr.fetchall():
            params = {
                'name': vals['supplier_id'],
#                 'product_id': book_id[0],
                'product_tmpl_id': book_id[0],
                'sequence': vals['sequence'],
                'delay': vals['delay'],
                'min_qty': vals['min_qty'],
            }
            tmp_id = sup_info.create(params)
            last_id = last_id < tmp_id.id and last_id or tmp_id.id
        return last_id

    @api.multi
    def write(self, vals):
        res = {}
        update_sequence = "update product_supplierinfo\
                           set sequence = %s where name = %s"
        update_delay = "update product_supplierinfo\
                        set delay = %s where name = %s"
        for rel, idn in zip(self, self.ids):
            # cannot change supplier here. Must create a new relation:
            original_supplier_id = rel.supplier_id.id
            if not original_supplier_id:
                raise Warning(_("Warning ! Cannot set supplier in this form.\
                                 Please create a new relation."))
            new_supplier_id = vals.get('supplier_id', 0)
            supplier_change = new_supplier_id != 0 and (idn < 0
                                or (original_supplier_id != new_supplier_id))
            if supplier_change:
                raise Warning(_("Warning ! Cannot set supplier in this form.\
                                 Please create a new relation."))
            else:
                if 'sequence' in vals:
                    params = [vals.get('sequence', 0), original_supplier_id]
                    self._cr.execute(update_sequence, params)
                if 'delay' in vals:
                    params = [vals.get('delay', 0), original_supplier_id]
                    self._cr.execute(update_delay, params)

                res[str(idn)] = {}
        return res
