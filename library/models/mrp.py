# -*- coding: utf-8 -*-
# Part of Odoo. See LICENSE file for full copyright and licensing details.

from odoo import models, fields, api
from odoo.tools.translate import _
from odoo.tools import DEFAULT_SERVER_DATETIME_FORMAT


class ProcurementOrder(models.Model):
    _inherit = 'procurement.order'

    production_lot_id = fields.Many2one('stock.production.lot',
                                        'Production Lot')
    customer_ref = fields.Char('Customer reference')

    @api.v7
    def make_po(self, cr, uid, ids, context=None):
        """ Make purchase order from procurement
        @param self : Object Pointer
        @param cr : Database Cursor
        @param uid : Current Logged in User
        @param ids :list of IDs
        @param context : context arguments, like language, time zone
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
            # Taking Main Supplier of Product of Procurement.
            partner = procurement.product_id.seller_id
            seller_qty = procurement.product_id.seller_qty
            partner_id = partner.id
            address_id = partner_obj.address_get(cr, uid, [partner_id],
                                                 ['delivery'])['delivery']
            pricelist_id = partner.property_product_pricelist_purchase.id
            domain = [('company_id', '=',
                       procurement.company_id.id or company.id)]
            warehouse_id = warehouse_obj.search(cr, uid,
                                                domain, context=context)
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
            purchase_date = self._get_purchase_order_date(cr, uid, procurement,
                                                          company,
                                                          schedule_date,
                                                          context=context)
            # Passing partner_id to context
            # for purchase order line integrity of Line name
            context.update({'lang': partner.lang, 'partner_id': partner_id})
            product = prod_obj.browse(cr, uid, procurement.product_id.id,
                                      context=context)
            taxes_ids = procurement.product_id.product_tmpl_id.\
                        supplier_taxes_id
            taxes = acc_pos_obj.map_tax(cr, uid,
                                        partner.property_account_position,
                                        taxes_ids)
            date = schedule_date.strftime(DEFAULT_SERVER_DATETIME_FORMAT)
            line_vals = {'name': product.partner_ref,
                         'product_qty': qty,
                         'product_id': procurement.product_id.id,
                         'product_uom': uom_id,
                         'price_unit': price or 0.0,
                         'date_planned': date,
                         'move_dest_id': res_id,
                         'notes': product.description_purchase,
                         'taxes_id': [(6, 0, taxes)],
                         'production_lot_id': procurement.production_lot_id
                             and procurement.production_lot_id.id or False,
                         'customer_ref': procurement.customer_ref}
            name = seq_obj.get(cr, uid, 'purchase.order')\
                    or _('PO: %s') % procurement.name
            date = purchase_date.strftime(DEFAULT_SERVER_DATETIME_FORMAT)
            warehouse_id = warehouse_id and warehouse_id[0] or False
            po_vals = {'name': name,
                       'origin': procurement.origin,
                       'partner_id': partner_id,
                       'partner_address_id': address_id,
                       'location_id': procurement.location_id.id,
                       'warehouse_id': warehouse_id,
                       'pricelist_id': pricelist_id,
                       'date_order': date,
                       'company_id': procurement.company_id.id,
                       'fiscal_position': partner.property_account_position
                                    and partner.property_account_position.id
                                    or False}
            res[procurement.id] = self.create_procurement_purchase_order(cr,
                                    uid, procurement, po_vals, line_vals,
                                    context=context)
            self.write(cr, uid, [procurement.id],
                       {'state': 'running',
                        'purchase_id': res[procurement.id]})
        return res
