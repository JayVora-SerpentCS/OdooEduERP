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
from openerp.tools import DEFAULT_SERVER_DATE_FORMAT
from dateutil.relativedelta import relativedelta
from datetime import datetime
import time


class product_state(models.Model):

    _name = "product.state"
    _description = "States of Books"

    name = fields.Char('State', select=1, required=True)
    code = fields.Char('Code', required=True)
    active = fields.Boolean('Active', select=2)


class many2manysym(fields.Many2many):

    @api.multi
    def get(self, offset=0):
        res = {}
        if not self.ids:
            return res
        ids_s = ','.join(map(str, self.ids))
        for ids in self.ids:
            res[ids] = []
        limit_str = self._limit is not None and ' limit %d' % self._limit or ''
        for (self._id2, self._id1) in [(self._id2, self._id1),
                                       (self._id1, self._id2)]:
            self._cr.execute('select ' + self._id2 + ',' + self._id1 +
                             ' from ' + self._rel + ' where ' + self._id1 +
                             ' in (' + ids_s + ')' + limit_str +
                             ' offset %s', (offset,))
            for r in self._cr.fetchall():
                res[r[1]].append(r[0])
        return res


class product_template(models.Model):

    _inherit = "product.template"

    name = fields.Char('Name', required=True, select=True)

    @api.multi
    def _state_get(self):
        self._cr.execute('select name, name from product_state order by name')
        return self._cr.fetchall()


class product_lang(models.Model):

    """Book language"""
    _name = "product.lang"

    code = fields.Char('Code', required=True, select=True)
    name = fields.Char('Name', required=True, select=True, translate=True)

    _sql_constraints = [('name_uniq', 'unique (name)',
                         'The name of the product must be unique !')
                        ]


class product_product(models.Model):
    """Book variant of product"""
    _inherit = "product.product"

    @api.multi
    def name_get(self):
        ''' This method Returns the preferred display value
        (text representation)
        for the records with the given ids.
        @param self : Object Pointer
        @param cr : Database Cursor
        @param uid : Current Logged in User
        @param ids :list of ids
        @param context : context arguments, like lang, time zone
        @return : tuples with the text representation of requested objects
        for to-many relationships
         '''

        if isinstance(self.ids, (int, long)):
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
        @param context : context arguments, like lang, time zone
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
        @param ids :list of ids
        @param field_name : name of fields
        @param arg : other arguments
        @param context : context arguments, like lang, time zone
        @return : Dics
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
        @param ids :list of ids
        @param product : name of field
        @param partner_id : name of field
        @param context : context arguments, like lang, time zone
        @return : Dics
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
        @param ids :list of ids
        @param name : name of field
        @param arg : other argument
        @param context : context arguments, like lang, time zone
        @return : Dics
         '''

        res = {}
#         if context is None:
#             context = {}
        for p in self:
            res[p.id] = self._get_partner_code_name(p, self._context.get
                                                    ('parent_id',
                                                     None))['code']
        return res

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
        default.update({'author_ids': []})
        return super(product_product, self).copy(default)

    @api.model
    def create(self, vals):
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
            supplier_model = self.env['library.editor.supplier']
            supplier_ids = [idn.id for idn in
                            supplier_model.search([('name', '=', editor_id)])
                            if idn.id > 0]
            suppliers = supplier_model.browse(supplier_ids)
            for obj in suppliers:
                supplier = [
                    0, 0, {'pricelist_ids': [], 'name': obj.supplier_id.id,
                           'sequence': obj.sequence, 'qty': 0,
                           'delay': 1, 'product_code': False,
                           'product_name': False}
                ]
                if 'seller_ids' not in vals:
                    vals['seller_ids'] = [supplier]
                else:
                    vals['seller_ids'].append(supplier)
        return super(product_product, self).create(vals)

    @api.onchange('date_parution')
    def _cal_parution_date(self):
        """
        This method calculates the resign date with
        """
        for date_rec in self:
            if date_rec.date_parution:
                r_date = datetime.strptime(date_rec.date_parution,
                                           DEFAULT_SERVER_DATE_FORMAT)
                l_date = r_date + relativedelta(days=date_rec.
                                                day_to_return_book.day)
                date_rec.date_retour = l_date.strftime
                (DEFAULT_SERVER_DATE_FORMAT)
    isbn = fields.Char('Isbn code', unique=True,
                       help="It show the International Standard Book Number")
    catalog_num = fields.Char('Catalog number',
                              help="It show the Identification"
                              "number of books")
    lang = fields.Many2one('product.lang', 'Language')
    editor = fields.Many2one('res.partner', 'Editor', change_default=True)
    author = fields.Many2one('library.author', 'Author')
    code = fields.Char(compute="_product_code", method=True, string='Acronym',
                       store=True)
    catalog_num = fields.Char('Catalog number',
                              help="The reference number of the book")
    date_parution = fields.Date('Release date',
                                help="Release(Issue) date of the book")
    creation_date = fields.Datetime('Creation date', readonly=True,
                                    help="Record creation date",
                                    default=lambda *a: time.strftime
                                    ('%Y-%m-%d %H:%M:%S'))
    date_retour = fields.Date('Return Date', help='Book Return date',
                              default=lambda *a:
                              str(int(time.strftime("%Y"))) +
                              time.strftime("-%m-%d"))
    tome = fields.Char('Tome', help="It will store the information of work"
                       "in serveral volume")
    nbpage = fields.Integer('Number of pages')
    rack = fields.Many2one('library.rack', 'Rack',
                           help="it will be show the position of book")
    availability = fields.Selection([('available', 'Available'),
                                     ('notavailable', 'Not Available')],
                                    'Book Availability', default='available')
    link_ids = many2manysym('product.product', 'book_book_rel', 'product_id1',
                            'product_id2', 'Related Books')
    back = fields.Selection([('hard', 'Hardback'), ('paper', 'Paperback')],
                            'Reliure', help="It show the books binding type",
                            default='paper')
    collection = fields.Many2one('library.collection', 'Collection',
                                 help="It show the collection in which book"
                                 "is resides")
    pocket = fields.Char('Pocket')
    num_pocket = fields.Char('Collection Num.',
                             help="It show the collection number in which book"
                             "is resides")
    num_edition = fields.Integer('Num. edition', help="Edition number of book")
    format = fields.Char('Format',
                         help="The general physical appearance of a book")
    price_cat = fields.Many2one('library.price.category', "Price category")
    day_to_return_book = fields.Many2one("library.book.returnday",
                                         "Book return Days")
    attchment_ids = fields.One2many("book.attachment", "product_id",
                                    "Book Attachments")

    _sql_constraints = [
        ('unique_ean13', 'unique(ean13)',
         'The ean13 field must be unique across all the products'),
        ('code_uniq', 'unique (code)',
         'The code of the product must be unique !')
    ]


class book_attachment(models.Model):

    _name = "book.attachment"

    _description = "Stores the attachments of the book"

    name = fields.Char("Description", required=True)
    product_id = fields.Many2one("product.product", "Product")
    date = fields.Date("Attachment Date", required=True,
                       default=lambda *a: time.strftime('%Y-%m-%d'))
    attachment = fields.Binary("Attachment")


class library_author(models.Model):

    _inherit = 'library.author'

    book_ids = fields.Many2many('product.product', 'author_book_rel',
                                'author_id', 'product_id', 'Books', select=1)

# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4:
