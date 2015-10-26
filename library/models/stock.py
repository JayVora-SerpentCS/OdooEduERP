# -*- encoding: UTF-8 -*-
##############################################################################
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
##############################################################################

from openerp import models, fields, api
from openerp import workflow


class stock_move(models.Model):

    _inherit = 'stock.move'

    customer_ref = fields.Char('Customer reference')
    origin_ref = fields.Char('Origin')

    @api.multi
    def onchange_qty(self):
        '''  New function to manage the update of the quantities'''
        '''  This method automatically change quantity of stock
        @param self : Object Pointer
        @param cr : Database Cursor
        @param uid : Current Logged in User
        @param ids : Current Records
        @param qty : Field name
        @param context : standard Dictionary
        @return : Dictionary having identifier of the record as key
                  and the value of quantity
        '''
        return {'value': {'product_uos_qty': self.product_uos_qty,
                          'product_qty': self.product_qty}}

    @api.multi
    def action_cancel(self):
        '''  action_cancel OveRidden to avoid the cascading cancellation'''
        '''  This action_cancel OveRidden to avoid the cascading cancellation
        @param self : Object Pointer
        @param cr : Database Cursor
        @param uid : Current Logged in User
        @param ids : Current Records
        @param context : standard Dictionary
        @return : True
        '''
        if not len(self.ids):
            return True
        pickings = {}
        for move in self:
            if move.state in ('confirmed', 'waiting', 'assigned', 'draft'):
                if move.picking_id:
                    pickings[move.picking_id.id] = True
        self.write({'state': 'cancel'})
        for pick_id in pickings:
            workflow.trg_validate(self._uid, 'stock.picking', pick_id,
                                  'button_cancel', self._cr)
        ids2 = []
        for res in self.read(['move_dest_id']):
            if res['move_dest_id']:
                ids2.append(res['move_dest_id'][0])
        for stock_id in self.ids:
            workflow.trg_trigger(self._uid, 'stock.move', stock_id, self._cr)
        return True


class stock_picking(models.Model):

    _inherit = 'stock.picking'
    _order = "create_date desc"

    sale_id = fields.Many2one('sale.order', 'Sale Order', ondelete='set null',
                              select=True, readonly=True, default=False)
    purchase_id = fields.Many2one('purchase.order', 'Purchase Order',
                                  ondelete='set null', readonly=True,
                                  select=True, default=False)
    date_done = fields.Datetime('Picking date', readonly=True)
