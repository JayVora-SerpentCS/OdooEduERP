# -*- encoding: utf-8 -*-
##############################################################################
#
#    OpenERP, Open Source Management Solution
#    Copyright (C) 2004-2009 Tiny SPRL (<http://tiny.be>).
#    Copyright (C) 2011-2012 Serpent Consulting Services
#    (<http://www.serpentcs.com>)
#    Copyright (C) 2013-2014 Serpent Consulting Services
#    (<http://www.serpentcs.com>)
#    This program is free software: you can redistribute it and/or modify
#    it under the terms of the GNU Affero General Public License as
#    published by the Free Software Foundation, either version 3 of the
#    License, or (at your option) any later version.
#
#    This program is distributed in the hope that it will be useful,
#    but WITHOUT ANY WARRANTY; without even the implied warranty of
#    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#    GNU Affero General Public License for more details.
#
#    You should have received a copy of the GNU Affero General Public License
#    along with this program.  If not, see <http://www.gnu.org/licenses/>.
#
##############################################################################
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
#     junk = fields.Text(compute="get_junk", method=True, string=" ", )
    junk = fields.Text(compute=lambda self: dict([(idn, '') for idn in
                                                  self.ids]),
                       method=True, string=" ", type="text")

    @api.v7
    def init(self, cr):
        tools.sql.drop_view_if_exists(cr, self._table)
        cr.execute("""
            create view library_editor_supplier as (
                select
                    case when min(ps.id) is null then - min(pp.id)
                    else min(ps.id) end as id,
                    case when pp.editor is null then 1 else pp.
                    editor end as name,
                    case when ps.name is null then 1 else ps.
                    name end as supplier_id,
                    case when ps.sequence is null then 0 else ps.
                    sequence end as sequence,
                    ps.delay as delay,
                    ps.min_qty as min_qty
                from
                    product_supplierinfo ps full outer join product_product pp
                    on (ps.name = pp.product_tmpl_id)
                where
                    ((pp.editor is not null) or (ps.name is not null))
                group by pp.editor, ps.name, ps.sequence, ps.delay, ps.min_qty
            )""")

    @api.model
    @api.returns('self', lambda value: value)
    def create(self, vals):
        if not (vals['name'] and vals['supplier_id']):
            # raise osv.except_osv(_("Error"), _("Please provide proper
            #    Information"))
            raise Warning(_("Error ! Please provide proper Information"))
        # search for books of these editor not already linked with this
        #    supplier :
        select = """select product_tmpl_id\n"""\
                 """from product_product\n"""\
                 """where editor = %s\n"""\
                 """  and id not in (select product_tmpl_id from
                 product_supplierinfo"
                 "where name = %s)""" % (vals['name'], vals['supplier_id'])
        self._cr.execute(select)
        if not self._cr.rowcount:
            raise Warning(_("Error ! No book to apply this relation"))

        sup_info = self.env['product.supplierinfo']
        last_id = 0
        for book_id in self._cr.fetchall():
            params = {
                'name': vals['supplier_id'],
                # 'product_id': book_id[0],
                'product_tmpl_id': book_id[0],
                'sequence': vals['sequence'],
                'delay': vals['delay'],
                'min_qty': vals['min_qty'],
            }
            tmp_id = sup_info.create(params)
            last_id = last_id < tmp_id.id and last_id or tmp_id.id
        return last_id

    @api.model
    def unlink(self, ids):
        supplier_obj = self.env['product.supplierinfo']
        for rel in self:
            if not (rel.name and rel.supplier_id):
                continue
            # search for the equivalent ids in product_supplierinfo
            #    (unpack the group)
            self._cr.execute("""select si.id\n"""
                             """from product_supplierinfo si\n"""
                             """join product_product pp\n"""
                             """  on (si.product_id = pp.product_tmpl_id )\n"""
                             """where pp.editor = %s and si.name = %s""" %
                             (rel.name.id, rel.supplier_id.id))

            ids = [x[0] for x in self._cr.fetchall()]
            supplier_obj.unlink(ids)
        return True

    @api.multi
    def write(self, vals):
        res = {}
        update_sequence = "update product_supplierinfo set sequence = %s"\
                          "where name = %s"
        update_delay = "update product_supplierinfo set delay = %s"\
                       "where name = %s"
#         relations = self.browse(cr, user, ids)
#         for rel, idn in zip(relations, ids):
        for rel, idn in zip(self, self.ids):
            #   cannot change supplier here. Must create a new relation:
            original_supplier_id = rel.supplier_id.id
            if not original_supplier_id:
                raise Warning(_("Warning ! Cannot set supplier in this form."
                                "Please create a new relation."))

            new_supplier_id = vals.get('supplier_id', 0)
            supplier_change = new_supplier_id != 0 and (idn < 0 or
                                                        (original_supplier_id
                                                         != new_supplier_id))
            if supplier_change:
                raise Warning(_("Warning ! Cannot set supplier in this form."
                                "Please create a new relation."))
            else:
                if 'sequence' in vals:
                    params = [vals.get('sequence', 0), original_supplier_id]
                    self._cr.execute(update_sequence, params)
                if 'delay' in vals:
                    params = [vals.get('delay', 0), original_supplier_id]
                    self._cr.execute(update_delay, params)

                res[str(idn)] = {}
        return res

# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4:
