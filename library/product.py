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
import time

class product_state(osv.Model):
    
    _name = "product.state"
    _description = "States of Books"

    _columns={
        'name': fields.char('State', size=64, select=1, required=True),
        'code': fields.char('Code', size=64, required=True),
        'active': fields.boolean('Active', select=2),
    }

class many2manysym(fields.many2many):

    def get(self, cr, obj, ids, name, user=None, offset=0, context=None, values={}):
        if context is None:
            context
        res = {}
        if not ids:
            return res
        ids_s = ','.join(map(str, ids))
        for id in ids:
            res[id] = []
        limit_str = self._limit is not None and ' limit %d' % self._limit or ''
        for (self._id2, self._id1) in [(self._id2, self._id1), (self._id1, self._id2)]:
            cr.execute('select '+self._id2+','+self._id1+' from '+self._rel+' where '+self._id1+' in ('+ids_s+')'+limit_str+' offset %s', (offset,))
            for r in cr.fetchall():
                res[r[1]].append(r[0])
        return res

class product_template(osv.Model):
    
    _inherit = "product.template"

    _columns = {
        'name': fields.char('Name', size=256, required=True, select=True),
    }

def _state_get(self, cr, uid,context):
    cr.execute('select name, name from product_state order by name')
    return cr.fetchall()

class product_lang(osv.Model):
    
    """Book language"""
    _name = "product.lang"

    _columns = {
        'code' : fields.char('Code', size=4, required=True, select=True),
        'name': fields.char('Name', size=128, required=True, select=True, translate=True),
    }
    
    _sql_constraints = [
                        ('name_uniq', 'unique (name)', 'The name of the product must be unique !')
        ]

class product_product(osv.Model):
    """Book variant of product"""
    _inherit = "product.product"

    def name_get(self, cr, user, ids, context=None):
        ''' This method Returns the preferred display value (text representation) for the records with the given ids. 
        @param self : Object Pointer
        @param cr : Database Cursor
        @param uid : Current Logged in User
        @param ids :list of ids
        @param context : context arguments, like lang, time zone
        @return : tuples with the text representation of requested objects for to-many relationships
         '''
        
        if context is None:
            context = {}
            
        if isinstance(ids, (int, long)):
            ids = [ids]
            
        if not len(ids):
            return []

        def _name_get(d):
            name = d.get('name', '')
            ean = d.get('ean13', False)
            if ean:
                name = '[%s] %s' % (ean or '', name)
            return (d['id'], name)

        return map(_name_get, self.read(cr, user, ids, ['name', 'ean13'], context))

    def _default_categ(self, cr, uid, context=None):
        ''' This method put default category of product 
        @param self : Object Pointer
        @param cr : Database Cursor
        @param uid : Current Logged in User
        @param context : context arguments, like lang, time zone
         '''
        
        if context is None:
            context = {}
        if 'category_id' in context and context['category_id']:
            return context['category_id']
        md = self.pool.get('ir.model.data')
        res = False
        try:
            res = md.get_object_reference(cr, uid, 'library', 'product_category_1')[1]
        except ValueError:
            res = False
        return res
    
    def _tax_incl(self, cr, uid, ids, field_name, arg, context=None):
        ''' This method include tax in product 
        @param self : Object Pointer
        @param cr : Database Cursor
        @param uid : Current Logged in User
        @param ids :list of ids
        @param field_name : name of fields
        @param arg : other arguments
        @param context : context arguments, like lang, time zone
        @return : Dics
         '''
        
        res = {}
        for product in self.browse(cr, uid, ids):
            val = 0.0
            for c in self.pool.get('account.tax').compute(cr, uid, product.taxes_id, product.list_price, 1, False):
                val += round(c['amount'], 2)
            res[product.id] = round(val + product.list_price, 2)
        return res

    def _get_partner_code_name(self, cr, uid, ids, product, parent_id, context=None):
        ''' This method get the partner code name 
        @param self : Object Pointer
        @param cr : Database Cursor
        @param uid : Current Logged in User
        @param ids :list of ids
        @param product : name of field
        @param partner_id : name of field
        @param context : context arguments, like lang, time zone
        @return : Dics
         '''
        for supinfo in product.seller_ids:
            if supinfo.name.id == parent_id:
                return {'code': supinfo.product_code or product.default_code, 'name': supinfo.product_name or product.name}
        res = {'code': product.default_code, 'name': product.name}
        return res

    def _product_code(self, cr, uid, ids, name, arg, context=None):
        ''' This method get the product code 
        @param self : Object Pointer
        @param cr : Database Cursor
        @param uid : Current Logged in User
        @param ids :list of ids
        @param name : name of field
        @param arg : other argument
        @param context : context arguments, like lang, time zone
        @return : Dics
         '''
        
        res = {}
        if context is None:
            context = {}
        for p in self.browse(cr, uid, ids, context=context):
            res[p.id] = self._get_partner_code_name(cr, uid, [], p, context.get('parent_id', None), context=context)['code']
        return res

    def copy(self, cr, uid, id, default=None, context={}):
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
        default.update({'author_ids': []})
        return super(product_product, self).copy(cr, uid, id, default, context)

    def create(self, cr, uid, vals, context= None):
        ''' This method is Create new student 
        @param self : Object Pointer
        @param cr : Database Cursor
        @param uid : Current Logged in User
        @param vals : dict of new values to be set
        @param context : standard Dictionary
        @return :ID of newly created record.
        '''
        
        def _uniq(seq):
            keys = {}
            for e in seq:
                keys[e] = 1
            return keys.keys()

        # add link from editor to supplier:
        if 'editor' in vals:
            editor_id = vals['editor']
            supplier_model = self.pool.get('library.editor.supplier')
            supplier_ids = [idn for idn in supplier_model.search(cr, uid, [('name', '=', editor_id)]) if idn > 0]
            suppliers = supplier_model.browse(cr, uid, supplier_ids, context)
            for obj in suppliers:
                supplier = [
                    0, 0, {'pricelist_ids': [], 'name': obj.supplier_id.id, 'sequence': obj.sequence, 'qty': 0,
                    'delay': 1, 'product_code': False, 'product_name': False}
                ]
                if 'seller_ids' not in vals:
                    vals['seller_ids'] = [supplier]
                else:
                    vals['seller_ids'].append(supplier)
        return super(product_product, self).create(cr, uid, vals, context=context)

    _columns = {
#        'author_ids': fields.many2many('library.author', 'author_book_rel', 'product_id', 'author_id', 'Authors'),
        'isbn': fields.char('Isbn code', size=64, unique=True, help ="It show the International Standard Book Number"),
        'catalog_num': fields.char('Catalog number', size=64, help ="It show the Identification number of books"),
#        'author_om_ids': fields.one2many('author.book.rel', 'product_id', 'Authors'),
        'lang': fields.many2one('product.lang','Language'),
        'editor': fields.many2one('res.partner', 'Editor', change_default=True),
        'author': fields.many2one('library.author','Author',size=30),
        'code': fields.function(_product_code, method=True, type='char', string='Acronym',store=True),
        'catalog_num': fields.char('Catalog number', size=64 , help="The reference number of the book"),
        'date_parution': fields.date('Release date', help="Release(Issue) date of the book"),
        'creation_date': fields.datetime('Creation date', readonly=True, help="Record creation date"),
        'date_retour': fields.date('Return Date',readonly=True, help='Book Return date'),
        'tome': fields.char('Tome', size=8, help = "It will store the information of work in serveral volume"),
        'nbpage': fields.integer('Number of pages', size=8),
        'rack': fields.many2one('library.rack', 'Rack', size=16, help="it will be show the position of book"),
        'availability': fields.selection([('available','Available'),('notavailable','Not Available')], 'Book Availability'),
        'link_ids': many2manysym('product.product', 'book_book_rel', 'product_id1', 'product_id2', 'Related Books'),
        'back': fields.selection([('hard', 'Hardback'), ('paper', 'Paperback')], 'Reliure',help="It show the books binding type"),
        'collection': fields.many2one('library.collection', 'Collection',help="It show the collection in which book is resides"),
        'pocket': fields.char('Pocket', size=32),
        'num_pocket': fields.char('Collection Num.', size=32,help="It show the collection number in which book is resides"),
        'num_edition': fields.integer('Num. edition', help="Edition number of book"),
        'format': fields.char('Format', size=128, help="The general physical appearance of a book"),
        'price_cat': fields.many2one('library.price.category', "Price category"),
        'day_to_return_book': fields.many2one("library.book.returnday","Book return Days"),
        "attchment_ids" : fields.one2many("book.attachment", "product_id", "Book Attachments"),
    }

    _defaults = {
        'creation_date': lambda *a: time.strftime('%Y-%m-%d %H:%M:%S'),
        'back': lambda *a: 'paper',
        #'procure_method': lambda *a: 'make_to_order',
        'date_retour': lambda *a: str(int(time.strftime("%Y"))) + time.strftime("-%m-%d"),
        'availability': 'available',
#         'categ_id': lambda self,cr,uid:self.pool.get('product.category').browse(cr,uid).categ_id.name[1],
    }

    _sql_constraints = [
        ('unique_ean13', 'unique(ean13)', 'The ean13 field must be unique across all the products'),
        ('code_uniq', 'unique (code)', 'The code of the product must be unique !')
    ]

class book_attachment(osv.Model):
    
    _name = "book.attachment"
    
    _description = "Stores the attachments of the book"
    
    _columns = {
        "name" : fields.char("Description", size=20, required=True),
        "product_id" : fields.many2one("product.product", "Product"),    
        "date" : fields.date("Attachment Date", required=True),
        "attachment" : fields.binary("Attachment"),
    }
    
    _defaults = {
        'date': lambda *a: time.strftime('%Y-%m-%d'),
    }

class library_author(osv.Model):
    
    _inherit = 'library.author'

    _columns = {
        'book_ids': fields.many2many('product.product', 'author_book_rel', 'author_id', 'product_id', 'Books', select=1),
    }

# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4:
