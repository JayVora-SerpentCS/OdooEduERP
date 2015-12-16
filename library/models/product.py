# -*- coding: utf-8 -*-
# Part of Odoo. See LICENSE file for full copyright and licensing details.

import time
from openerp import models, fields, api


class ProductState(models.Model):
    _name = "product.state"
    _description = "States of Books"

    name = fields.Char('State', select=1, required=True)
    code = fields.Char('Code', required=True)
    active = fields.Boolean('Active', select=2)


class Many2manySym(fields.Many2many):

    @api.multi
    def get(self, offset=0):
        res = {}
        if not self.ids:
            return res
        ids_s = ','.join(map(str, self.ids))
        for self_ids in self.ids:
            res[self_ids] = []
        limit_str = self._limit is not None and ' limit %d' % self._limit or ''
        for (self._id2, self._id1) in [(self._id2, self._id1),
                                       (self._id1, self._id2)]:
            self._cr.execute('select ' + self._id2 + ',' + self._id1
                             + ' from ' + self._rel + ' where ' + self._id1
                             + ' in ('
                             + ids_s + ')' + limit_str + ' offset %s',
                             (offset,))
            for r in self._cr.fetchall():
                res[r[1]].append(r[0])
        return res


class ProductTemplate(models.Model):
    _inherit = "product.template"

    name = fields.Char('Name', required=True, select=True)

    @api.multi
    def _state_get(self):
        self._cr.execute('select name, name from product_state order by name')
        return self._cr.fetchall()


class ProductLang(models.Model):
    '''Book language'''
    _name = "product.lang"

    code = fields.Char('Code', required=True, select=True)
    name = fields.Char('Name', required=True, select=True, translate=True)

    _sql_constraints = [('name_uniq', 'unique (name)',
                         'The name of the product must be unique !')]


class ProductProduct(models.Model):
    """Book variant of product"""
    _inherit = "product.product"

    @api.multi
    def name_get(self):
        ''' This method Returns the preferred display value
            (text representation) for the records with the given IDs.
        @param self : Object Pointer
        @param cr : Database Cursor
        @param uid : Current Logged in User
        @param ids :list of IDs
        @param context : context arguments, like language, time zone
        @return : tuples with the text representation of requested objects
                  for to-many relationships
         '''

        if not len(self.ids):
            return []

        def _name_get(d):
            name = d.get('name', '')
            ean = d.get('ean13', False)
            if ean:
                name = '[%s] %s' % (ean or '', name)
            return (d['id'], name)
        return map(_name_get, self.read(['name', 'ean13']))

    @api.multi
    def _default_categ(self):
        ''' This method put default category of product
        @param self : Object Pointer
        @param cr : Database Cursor
        @param uid : Current Logged in User
        @param context : context arguments, like language, time zone
        '''

        if self._context is None:
            self._context = {}
        if 'category_id' in self._context and self._context['category_id']:
            return self._context['category_id']
        md = self.env['ir.model.data']
        res = False
        try:
            res = md.get_object_reference('library', 'product_category_1')[1]
        except ValueError:
            res = False
        return res

    @api.multi
    def _tax_incl(self):
        ''' This method include tax in product
        @param self : Object Pointer
        @param cr : Database Cursor
        @param uid : Current Logged in User
        @param ids :list of IDs
        @param field_name : name of fields
        @param arg : other arguments
        @param context : context arguments, like language, time zone
        @return : Dictionary
         '''
        res = {}

        for product in self:
            val = 0.0
            for c in self.env['account.tax'].compute(product.taxes_id,
                                                     product.list_price, 1,
                                                     False):
                val += round(c['amount'], 2)
            res[product.id] = round(val + product.list_price, 2)
        return res

    @api.multi
    def _get_partner_code_name(self, product, parent_id):
        ''' This method get the partner code name
        @param self : Object Pointer
        @param cr : Database Cursor
        @param uid : Current Logged in User
        @param ids :list of IDs
        @param product : name of field
        @param partner_id : name of field
        @param context : context arguments, like language, time zone
        @return : Dictionary
         '''
        for supinfo in product.seller_ids:
            if supinfo.name.id == parent_id:
                return {'code': supinfo.product_code or product.default_code,
                        'name': supinfo.product_name or product.name}
        res = {'code': product.default_code, 'name': product.name}
        return res

    @api.multi
    def _product_code(self):
        ''' This method get the product code
        @param self : Object Pointer
        @param cr : Database Cursor
        @param uid : Current Logged in User
        @param ids :list of IDs
        @param name : name of field
        @param arg : other argument
        @param context : context arguments, like language, time zone
        @return : Dictionary
         '''
        res = {}
        parent_id = self._context.get('parent_id', None)
        for p in self:
            res[p.id] = self._get_partner_code_name(p, parent_id)['code']
        return res

    @api.multi
    def copy(self, default=None):
        ''' This method Duplicate record
            with given id updating it with default values
        @param self : Object Pointer
        @param cr : Database Cursor
        @param uid : Current Logged in User
        @param id : id of the record to copy
        @param default : dictionary of field values
               to override in the original values of the copied record
        @param context : standard Dictionary
        @return : id of the newly created record
        '''

        if default is None:
            default = {}
        default.update({'author_ids': []})
        return super(ProductProduct, self).copy(default)

    @api.model
    def create(self, vals):
        ''' This method is Create new student
        @param self : Object Pointer
        @param cr : Database Cursor
        @param uid : Current Logged in User
        @param vals : dictionary of new values to be set
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
            supplier_model = self.env['library.editor.supplier']
            domain = [('name', '=', editor_id)]
            supplier_ids = [idn.id for idn
                            in supplier_model.search(domain)
                            if idn.id > 0]
            suppliers = supplier_model.browse(supplier_ids)
            for obj in suppliers:
                supplier = [0, 0,
                            {'pricelist_ids': [],
                             'name': obj.supplier_id.id,
                             'sequence': obj.sequence,
                             'qty': 0,
                             'delay': 1,
                             'product_code': False,
                             'product_name': False}]
                if 'seller_ids' not in vals:
                    vals['seller_ids'] = [supplier]
                else:
                    vals['seller_ids'].append(supplier)
        return super(ProductProduct, self).create(vals)

    isbn = fields.Char('ISBN Code', unique=True,
                       help="Shows International Standard Book Number")
    catalog_num = fields.Char('Catalog number',
                              help="Shows Identification number of books")
    lang = fields.Many2one('product.lang', 'Language')
    editor = fields.Many2one('res.partner', 'Editor', change_default=True)
    author = fields.Many2one('library.author', 'Author')
    code = fields.Char(compute="_product_code", method=True, string='Acronym',
                       store=True)
    catalog_num = fields.Char('Catalog number',
                              help="Reference number of book")
    date_parution = fields.Date('Release date',
                                help="Release(Issue) Date of book")
    creation_date = fields.Datetime('Creation date', readonly=True,
                                    help="Record creation date",
                                    default=lambda *a:
                                        time.strftime('%Y-%m-%d %H:%M:%S'))
    date_retour = fields.Date('Return Date', readonly=True,
                              help='Book Return date',
                              default=lambda *a:str(int(time.strftime("%Y")))
                              + time.strftime("-%m-%d"))
    tome = fields.Char('TOME',
                       help="Stores information of work in several volume")
    nbpage = fields.Integer('Number of pages')
    rack = fields.Many2one('library.rack', 'Rack',
                           help="Shows position of book")
    availability = fields.Selection([('available', 'Available'),
                                     ('notavailable', 'Not Available')],
                                    'Book Availability', default='available')
    link_ids = Many2manySym('product.product', 'book_book_rel', 'product_id1',
                            'product_id2', 'Related Books')
    back = fields.Selection([('hard', 'HardBack'), ('paper', 'PaperBack')],
                            'Binding Type', help="Shows books-binding type",
                            default='paper')
    collection = fields.Many2one('library.collection', 'Collection',
                                 help='Show collection in which'
                                      'book is resides')
    pocket = fields.Char('Pocket')
    num_pocket = fields.Char('Collection No.',
                             help='Shows collection number in which'
                                  'book resides')
    num_edition = fields.Integer('No. edition', help="Edition number of book")
    format = fields.Char('Format',
                         help="The general physical appearance of a book")
    price_cat = fields.Many2one('library.price.category', "Price category")
    day_to_return_book = fields.Many2one('library.book.returnday',
                                         'Book return Days')
    attchment_ids = fields.One2many('book.attachment', 'product_id',
                                    'Book Attachments')

    _sql_constraints = [('unique_ean13', 'unique(ean13)',
                         'ean13 field must be unique across all the products'),
                        ('code_uniq', 'unique (code)',
                         'Code of the product must be unique !')]


class BookAttachment(models.Model):
    _name = "book.attachment"
    _description = "Stores attachments of the book"

    name = fields.Char("Description", required=True)
    product_id = fields.Many2one("product.product", "Product")
    date = fields.Date("Attachment Date", required=True, default=lambda *a:
                       time.strftime('%Y-%m-%d'))
    attachment = fields.Binary("Attachment")


class LibraryAuthor(models.Model):
    _inherit = 'library.author'

    book_ids = fields.Many2many('product.product', 'author_book_rel',
                                'author_id', 'product_id', 'Books', select=1)
