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

class update_prices(osv.TransientModel):
    
    _name="update.prices"
    
    def action_update_prices(self, cr, uid, ids, context=None):
        product_obj = self.pool.get('product.product')
        for cat in self.pool.get('library.price.category').browse(cr,uid,ids,context=context):
            prod_ids = [x.id for x in cat.product_ids]
            if prod_ids:
                product_obj.write(cr, uid, prod_ids,{'list_price':cat.price})
        return {}
    
# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4: