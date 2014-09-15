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

class card_number(osv.TransientModel):
    
    _name="card.number"
    _description="Card Number"
    _columns={
                'card_id': fields.many2one("library.card", "Card No", required=True), 
              }
    
    def card_number_ok(self, cr, uid, ids, context=None):
        if context is None:
            context = {}
        lib_book_obj = self.pool.get('library.book.issue')
        for rec in self.browse(cr,uid,ids,context=context):
                search_card_ids =lib_book_obj.search(cr,uid,[('card_id', '=', rec.card_id.id)],context=context)
                if not search_card_ids:
                        raise osv.except_osv(('Warning !'),('Invalid Card Number.'))
                else:
                    
                    return {'type': 'ir.actions.act_window',
                            'res_model':'book.name',
                            'src_model':'library.book.issue',
                            'target':'new',
                            'view_mode':'form',
                            'view_type':'form',
                            'context' : {'default_card_id' : rec.card_id.id}
                            }
                    
# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4: