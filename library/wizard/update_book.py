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


class update_books(models.TransientModel):

    _name = "update.books"
    _description = "Update Books"

    name = fields.Many2one('product.product', 'Book Name', required=True)

    @api.multi
    def action_update_books(self):
        lib_book_obj = self.env['library.book.issue']
        for rec in self:
            if self._context.get('active_ids'):
                for active_id in self._context.get('active_ids'):
                    lib_book_obj.browse(active_id).write({'name': rec.name.id})
        return {}

# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4:
