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
from openerp import models, fields, api
from mx import DateTime
from openerp import workflow


class sale_order_line(models.Model):

    _inherit = 'sale.order.line'

    production_lot_id = fields.Many2one('stock.production.lot',
                                        'Production Lot')
    customer_ref = fields.Char(string='Customer reference')

    @api.multi
    def button_confirm(self):
        ''' This method confirm order.
        @param self : Object Pointer
        @param cr : Database Cursor
        @param uid : Current Logged in User
        @param ids : Current Records
        @param context : standard Dictionary
        @return : True
        '''

        l_id = 0
        production_obj = self.env['stock.production.lot']
        for line in self:
            if line.production_lot_id:
                continue
            l_id += 1
            production_lot_dico = {
                'name': line.order_id and (str(line.order_id.name) +
                                           ('/%02d' % (l_id,))) or False,
                'product_id': line.product_id and line.product_id.id or False
            }
            production_lot_id = production_obj.create(production_lot_dico)
            line.write({'production_lot_id': production_lot_id.id})
        super(sale_order_line, self).button_confirm()
        return True

    @api.model
    def copy(self, default=None):
        ''' This method Duplicate record with given id updating it with
        default values
        @param self : Object Pointer
        @param cr : Database Cursor
        @param uid : Current Logged in User
        @param id : id of the record to copy
        @param default : dictionary of field values to override in the
        original values of the copied record
        @param context : standard Dictionary
        @return : id of the newly created record
        '''
        if default is None:
            default = {}
        default.update({
            'production_lot_id': False,
            'customer_ref': ''
        })
        return super(sale_order_line, self).copy(default)


class sale_order(models.Model):

    _inherit = "sale.order"
    _order = "create_date desc"

    @api.model
    def default_get(self, fields_list):
        res = super(sale_order, self).default_get(fields_list)
        res.update({'picking_policy': 'direct',
                    'order_policy': 'picking'})
        return res

    @api.multi
    def action_ship_create(self):
        ''' This method is Create shipping record
        @param self : Object Pointer
        @param cr : Database Cursor
        @param uid : Current Logged in User
        @param vals : dict of new values to be set
        @param context : standard Dictionary
        @return :True
        '''
        picking_obj = self.env['stock.picking']
        move_obj = self.env['stock.move']
        procurment_obj = self.env['procurement.order']
        picking_id = False
        for order in self:
            output_id = order.warehouse_id.wh_output_stock_loc_id.id
            picking_id = False
            for line in order.order_line:
                proc_id = False
                date_planned = (DateTime.now() + DateTime.RelativeDateTime
                                (days=line.delay or 0.0)).strftime('%Y-%m-%d')
                if line.state == 'done':
                    continue
                if line.product_id and line.product_id.product_tmpl_id.type \
                in ('product', 'consu'):
                    location_id = order.warehouse_id.lot_stock_id.id
                    if not picking_id:
                        picking_id = picking_obj.create({
                            'origin': order.name,
                            'type': 'out',
                            'state': 'draft',
                            'move_type': order.picking_policy,
                            'sale_id': order.id,
                            'address_id': order.partner_shipping_id.id,
                            'note': order.note,
                            'invoice_state': (order.order_policy == 'picking'
                                              and '2binvoiced') or 'none',
                            'carrier_id': order.carrier_id.id,
                            'picking_type_id': order.warehouse_id and
                            order.warehouse_id.out_type_id and
                            order.warehouse_id.out_type_id.id or False
                        })
                    move_id = move_obj.create({
                        'name': 'SO:' + order.name or '',
                        'picking_id': picking_id.id,
                        'origin_ref': order.name,
                        'product_id': line.product_id.id,
                        'date_planned': date_planned,
                        'product_uom_qty': line.product_uom_qty,
                        'product_uom': line.product_uom.id,
                        'product_uos': line.product_uos.id,
                        'product_packaging': line.product_packaging.id,
                        'address_id': line.address_allotment_id.id or
                        order.partner_shipping_id.id,
                        'location_id': location_id,
                        'location_dest_id': output_id,
                        'sale_line_id': line.id,
                        'tracking_id': False,
                        'state': 'waiting',
                        'prodlot_id': line.production_lot_id.id,
                        'customer_ref': line.customer_ref,
                    })
                    proc_id = procurment_obj.create({
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
                    workflow.trg_validate(self._uid, 'procurement.order',
                                          proc_id.id, 'button_confirm',
                                          self._cr)
                    line.write({'procurement_id': proc_id.id})
                elif line.product_id and line.product_id.product_tmpl_id.type \
                == 'service':
                    proc_id = procurment_obj.create({'name': line.name,
                                                     'origin': order.name,
                                                     'date_planned':
                date_planned,
                                                     'product_id':
                line.product_id.id,
                                                     'product_qty':
                line.product_uom_qty,
                                                     'product_uom':
                line.product_uom.id,
                                                     'location_id':
                order.warehouse_id.lot_stock_id.id,
                                                     'procure_method':
                line.type,
                })
                    workflow.trg_validate(self._uid, 'procurement.order',
                                          proc_id.id, 'button_confirm',
                                          self._cr)
                    line.write({'procurement_id': proc_id.id})
                else:
                    #
                    # No procurement because no product in the sale.order.line.
                    #
                    pass

            val = {}
            if picking_id:
                workflow.trg_validate(self._uid, 'stock.picking',
                                      picking_id.id, 'button_confirm',
                                      self._cr)

            if order.state == 'shipping_except':
                val['state'] = 'progress'
                if (order.order_policy == 'manual') and order.invoice_ids:
                    val['state'] = 'manual'
            order.write(val)
        return True

# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4:
