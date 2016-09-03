# -*- coding: utf-8 -*-
# Part of Odoo. See LICENSE file for full copyright and licensing details.

from openerp import models, fields, api
from openerp import workflow


class PurchaseOrderLine(models.Model):
    _inherit = 'purchase.order.line'

    origin = fields.Char('Origin')
    production_lot_id = fields.Many2one('stock.production.lot',
                                        'Production Lot')
    customer_ref = fields.Char('Customer reference')
    origin_ref = fields.Char('Origin')


class PurchaseOrder(models.Model):
    _inherit = 'purchase.order'
    _order = "create_date desc"

    @api.multi
    def action_picking_create(self):
        picking_obj = self.env['stock.picking']
        move_obj = self.env['stock.move']
        picking_id = False
        for order in self:
            loc_id = order.partner_id.property_stock_supplier.id,
            istate = 'none'
            if order.invoice_method == 'picking':
                istate = '2binvoiced'
            address_id = order.dest_address_id.id or order.partner_id.id
            vals = {'origin': 'PO:%d:%s' % (order.id, order.name),
                    'type': 'in',
                    'address_id': address_id,
                    'invoice_state': istate,
                    'purchase_id': order.id or False,
                    'picking_type_id': order.picking_type_id.id or False}
            picking_id = picking_obj.create(vals)
            for order_line in order.order_line:
                if not order_line.product_id:
                    continue
                if order_line.product_id.product_tmpl_id.type in ('product',
                                                                  'consu'):
                    dest = order.location_id.id
                    prodlot_id = order_line.production_lot_id.id
                    move_obj.create({'name': 'PO:' + order_line.name[:50],
                                     'product_id': order_line.product_id.id,
                                     'origin_ref': order.name,
                                     'product_uos_qty': order_line.product_qty,
                                     'product_uom': order_line.product_uom.id,
                                     'date_planned': order_line.date_planned,
                                     'location_id': loc_id,
                                     'location_dest_id': dest,
                                     'picking_id': picking_id.id,
                                     'move_dest_id': (order.location_id and
                                                      order.location_id.id),
                                     'state': 'assigned',
                                     'prodlot_id': prodlot_id,
                                     'customer_ref': order_line.customer_ref,
                                     'purchase_line_id': order_line.id})
            purchase_order_dict = {'picking_ids': [(4, picking_id.id)]}
            order.write(purchase_order_dict)
            workflow.trg_validate(self._uid, 'stock.picking', picking_id.id,
                                  'button_confirm', self._cr)
        return picking_id.id

    @api.multi
    def wkf_confirm_order(self):
        production_obj = self.env['stock.production.lot']
        for order in self:
            l_id = 0
            for line in order.order_line:
                if line.production_lot_id:
                    continue
                l_id += 1
                name = line.order_id and (str(line.order_id.name) + '/Line' +
                                          str(l_id)) or False
                production_lot_dict = {'product_id': line.product_id.id,
                                       'name': name}
                production_lot_id = production_obj.create(production_lot_dict)
                line.write({'production_lot_id': production_lot_id.id})
        super(PurchaseOrder, self).wkf_confirm_order()
        return True

    @api.model
    def default_get(self, fields_list):
        res = super(PurchaseOrder, self).default_get(fields_list)
        res.update({'invoice_method': 'picking'})
        return res
