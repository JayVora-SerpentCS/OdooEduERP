# -*- encoding: utf-8 -*-
##############################################################################
#
#    OpenERP, Open Source Management Solution
#    Copyright (C) 2004-2009 Tiny SPRL (<http://tiny.be>).
#    Copyright (C) 2011-2012 Serpent Consulting Services (<http://www.serpentcs.com>)
#    Copyright (C) 2013-2014 Serpent Consulting Services (<http://www.serpentcs.com>)
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
from openerp.osv import osv,fields
from mx import DateTime
from openerp import workflow

class sale_order_line(osv.Model):
    
    _inherit = 'sale.order.line'

    _columns = {
        'production_lot_id': fields.many2one('stock.production.lot', 'Production Lot'),
        'customer_ref': fields.char(string='Customer reference', size=64),
    }

    _defaults = {
       # 'type': lambda *a: 'make_to_order'
    }

    def button_confirm(self, cr, uid, ids, context=None):
        ''' This method confirm order.
        @param self : Object Pointer
        @param cr : Database Cursor
        @param uid : Current Logged in User
        @param ids : Current Records
        @param context : standard Dictionary
        @return : True 
        '''
        
        l_id = 0
        production_obj = self.pool.get('stock.production.lot')
        for line in self.browse(cr, uid, ids, context=context):
            if line.production_lot_id:
                continue
            l_id += 1
            production_lot_dico = {
                'name': line.order_id and (str(line.order_id.name)+('/%02d'%(l_id,))) or False,
                'product_id': line.product_id and line.product_id.id or False
            }
            production_lot_id = production_obj.create(cr, uid, production_lot_dico)
            self.write(cr, uid, [line.id], {'production_lot_id': production_lot_id}, context=context)
        super(sale_order_line, self).button_confirm(cr, uid, ids, context)
        return True

    def copy(self, cr, uid, id, default=None, context=None):
        ''' This method Duplicate record with given id updating it with default values
        @param self : Object Pointer
        @param cr : Database Cursor
        @param uid : Current Logged in User
        @param id : id of the record to copy
        @param default : dictionary of field values to override in the original values of the copied record
        @param context : standard Dictionary
        @return : id of the newly created record 
        '''
        
        if default is None:
            default = {}
        default.update({
            'production_lot_id': False,
            'customer_ref': ''
        })
        return super(sale_order_line, self).copy(cr, uid, id, default, context)

class sale_order(osv.Model):

    _inherit = "sale.order"
    _order = "create_date desc"

    _defaults = {
      #  'invoice_quantity': lambda *a: 'procurement',
        'picking_policy': lambda *a: 'direct',
        'order_policy': lambda *a: 'picking',
    }

    def action_ship_create(self, cr, uid, ids, context=None):
        ''' This method is Create shipping record 
        @param self : Object Pointer
        @param cr : Database Cursor
        @param uid : Current Logged in User
        @param vals : dict of new values to be set
        @param context : standard Dictionary
        @return :True
        '''
        
        if context is None:
            context = {}
        picking_obj = self.pool.get('stock.picking')
        move_obj = self.pool.get('stock.move')
        procurment_obj = self.pool.get('procurement.order')
        order_line_obj = self.pool.get('sale.order.line')
        picking_id = False
        for order in self.browse(cr, uid, ids, context={}):
            output_id = order.warehouse_id.wh_output_stock_loc_id.id
            picking_id = False
            for line in order.order_line:
                proc_id = False
                date_planned = (DateTime.now() + DateTime.RelativeDateTime(days=line.delay or 0.0)).strftime('%Y-%m-%d')
                if line.state == 'done':
                    continue
                if line.product_id and line.product_id.product_tmpl_id.type in ('product', 'consu'):
                    location_id = order.warehouse_id.lot_stock_id.id
                    if not picking_id:
                        picking_id = picking_obj.create(cr, uid, {
                            'origin': order.name,
                            'type': 'out',
                            'state': 'draft',
                            'move_type': order.picking_policy,
                            'sale_id': order.id,
                            'address_id': order.partner_shipping_id.id,
                            'note': order.note,
                            'invoice_state': (order.order_policy=='picking' and '2binvoiced') or 'none',
                            'carrier_id': order.carrier_id.id,
                        })
                    move_id = move_obj.create(cr, uid, {
                        'name': 'SO:' + order.name or '',
                        'picking_id': picking_id,
                        'origin_ref':order.name,
                        'product_id': line.product_id.id,
                        'date_planned': date_planned,
                       # 'product_qty': line.product_qty,
                        'product_uom_qty': line.product_uom_qty,
                        'product_uom': line.product_uom.id,
                        'product_uos': line.product_uos.id,
                        'product_packaging': line.product_packaging.id,
                        'address_id': line.address_allotment_id.id or order.partner_shipping_id.id,
                        'location_id': location_id,
                        'location_dest_id': output_id,
                        'sale_line_id': line.id,
                        'tracking_id': False,
                        'state': 'waiting',
#                        'note': line.notes,
                        'prodlot_id': line.production_lot_id.id,
                        'customer_ref': line.customer_ref,
                    })
                    proc_id = procurment_obj.create(cr, uid, {
                        'name': order.name,
                        'origin': order.name,
                        'date_planned': date_planned,
                        'product_id': line.product_id.id,
                        'product_qty': line.product_uom_qty,
                        'product_uom': line.product_uom.id,
                        'location_id': order.warehouse_id.lot_stock_id.id,
                        'procure_method': 'make_to_order',
                        'move_id': move_id,
                        'production_lot_id': line.production_lot_id.id,
                        'customer_ref': line.customer_ref,
                    })
                    workflow.trg_validate(uid, 'procurement.order', proc_id, 'button_confirm', cr)
                    order_line_obj.write(cr, uid, [line.id], {'procurement_id': proc_id})
                elif line.product_id and line.product_id.product_tmpl_id.type == 'service':
                    proc_id = procurment_obj.create(cr, uid, {
                        'name': line.name,
                        'origin': order.name,
                        'date_planned': date_planned,
                        'product_id': line.product_id.id,
                        'product_qty': line.product_uom_qty,
                        'product_uom': line.product_uom.id,
                        'location_id': order.warehouse_id.lot_stock_id.id,
                        'procure_method': line.type,
                    })
                    workflow.trg_validate(uid, 'procurement.order', proc_id, 'button_confirm', cr)
                    order_line_obj.write(cr, uid, [line.id], {'procurement_id': proc_id})
                else:
                    #
                    # No procurement because no product in the sale.order.line.
                    #
                    pass

            val = {}
            if picking_id:
                workflow.trg_validate(uid, 'stock.picking', picking_id, 'button_confirm', cr)
                #val = {'picking_ids':[(6,0,[picking_id])]}

            if order.state == 'shipping_except':
                val['state'] = 'progress'
                if (order.order_policy == 'manual') and order.invoice_ids:
                    val['state'] = 'manual'
            self.write(cr, uid, [order.id], val)
        return True

# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4: