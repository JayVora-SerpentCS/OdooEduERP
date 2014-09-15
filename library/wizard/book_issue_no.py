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

class book_name(osv.TransientModel):
    
    _name="book.name"
    _description="Book Name"
    _columns={
                'name': fields.many2one('product.product', 'Book Name', required=True),
                'card_id': fields.many2one("library.card", "Card No", required=True), 
              }
    
    def create_new_books(self, cr, uid, ids,vals, context=None):
        if context is None:
            context = {}
        lib_book_obj = self.pool.get('library.book.issue')
        for rec in self.browse(cr,uid,ids,context=context):
            lib_book_obj.create(cr, uid, {'name':rec.name.id, 'card_id':rec.card_id.id},context=context)
        
        return {}
   
# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4: