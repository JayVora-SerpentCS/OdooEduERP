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
from openerp.osv import osv, fields
from openerp.tools import DEFAULT_SERVER_DATETIME_FORMAT


class procurement_order(osv.Model):

    _inherit = "procurement.order"
    _columns = {
        'production_lot_id': fields.many2one('stock.production.lot',
                                             'Production Lot'),
        'customer_ref': fields.char('Customer reference'),
    }

    def make_po(self, cr, uid, ids, context=None):
        """ Make purchase order from procurement
        @param self : Object Pointer
        @param cr : Database Cursor
        @param uid : Current Logged in User
        @param ids :list of ids
        @param context : context arguments, like lang, time zone
        @return: New created Purchase Orders procurement wise
        """

        res = {}
        if context is None:
            context = {}
        company = self.pool.get('res.users').browse(cr, uid, uid,
                                                    context=context).company_id
        partner_obj = self.pool.get('res.partner')
        uom_obj = self.pool.get('product.uom')
        pricelist_obj = self.pool.get('product.pricelist')
        prod_obj = self.pool.get('product.product')
        acc_pos_obj = self.pool.get('account.fiscal.position')
        seq_obj = self.pool.get('ir.sequence')
        warehouse_obj = self.pool.get('stock.warehouse')
        for procurement in self.browse(cr, uid, ids, context=context):
            res_id = procurement.move_id.id
            partner = procurement.product_id.seller_id
            # Taken Main Supplier of Product of Procurement.
            seller_qty = procurement.product_id.seller_qty
            partner_id = partner.id
            address_id = partner_obj.address_get(cr, uid, [partner_id],
                                                 ['delivery'])['delivery']
            pricelist_id = partner.property_product_pricelist_purchase.id
            warehouse_id = warehouse_obj.search(cr, uid, [('company_id', '=',
                                                           procurement.
                                                           company_id.id or
                                                           company.id)],
                                                context=context)
            uom_id = procurement.product_id.uom_po_id.id

            qty = uom_obj._compute_qty(cr, uid, procurement.product_uom.id,
                                       procurement.product_qty, uom_id)
            if seller_qty:
                qty = max(qty, seller_qty)

            price = pricelist_obj.price_get(cr, uid, [pricelist_id],
                                            procurement.product_id.id,
                                            qty, partner_id,
                                            {'uom': uom_id})[pricelist_id]

            schedule_date = self._get_purchase_schedule_date(cr, uid,
                                                             procurement,
                                                             company,
                                                             context=context)
            purchase_date = self._get_purchase_order_date(cr, uid,
                                                          procurement,
                                                          company,
                                                          schedule_date,
                                                          context=context)

            # Passing partner_id to context for purchase order line integrity
            #    of Line name
            context.update({'lang': partner.lang, 'partner_id': partner_id})

            product = prod_obj.browse(cr, uid, procurement.product_id.id,
                                      context=context)
            taxes_ids = procurement.product_id.product_tmpl_id. \
                supplier_taxes_id
            taxes = acc_pos_obj.map_tax(cr, uid,
                                        partner.property_account_position,
                                        taxes_ids)

            line_vals = {
                'name': product.partner_ref,
                'product_qty': qty,
                'product_id': procurement.product_id.id,
                'product_uom': uom_id,
                'price_unit': price or 0.0,
                'date_planned': schedule_date.strftime
                (DEFAULT_SERVER_DATETIME_FORMAT),
                'move_dest_id': res_id,
                'notes': product.description_purchase,
                'taxes_id': [(6, 0, taxes)],
                'production_lot_id': procurement.production_lot_id and
                procurement.production_lot_id.id or False,
                'customer_ref': procurement.customer_ref,
            }
            name = seq_obj.get(cr, uid,
                               'purchase.order') or('PO:'
                                                    '%s') % procurement.name
            po_vals = {
                'name': name,
                'origin': procurement.origin,
                'partner_id': partner_id,
                'partner_address_id': address_id,
                'location_id': procurement.location_id.id,
                'warehouse_id': warehouse_id and warehouse_id[0] or False,
                'pricelist_id': pricelist_id,
                'date_order': purchase_date.strftime
                (DEFAULT_SERVER_DATETIME_FORMAT),
                'company_id': procurement.company_id.id,
                'fiscal_position': partner.property_account_position and
                partner.property_account_position.id
                or False
            }
            res[procurement.id] = self. \
                create_procurement_purchase_order(cr, uid, procurement,
                                                  po_vals, line_vals,
                                                  context=context)
            self.write(cr, uid, [procurement.id],
                       {'state': 'running',
                        'purchase_id': res[procurement.id]})
        return res

# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4:
