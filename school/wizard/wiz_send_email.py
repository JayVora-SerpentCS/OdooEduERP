# -*- coding: utf-8 -*-
##############################################################################
#
#    OpenERP, Open Source Management Solution
#    Copyright (C) 2004-2009 Tiny SPRL (<http://tiny.be>).
#    Copyright (C) 2011-Today Serpent Consulting Services PVT. LTD.
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


class SendEmail(models.TransientModel):
    _name = "send.email"

    note = fields.Text('Text')

#    def send_email(self, cr, uid, ids, context=None):
#        subject = 'Emergency mail'
#        body = ''
#        email_template = self.pool.get('email.template')
#        template_id = email_template.search(cr, uid, [('model', '=',
#                                              'student.student')],
#                                              context=context)
#        if template_id:
#            email_template_brw = email_template.browse(cr, uid,
#                                                         template_id[0])
#            for i in self.browse(cr, uid, ids):
#                body += '\n' + i.note
#            email_template.send_mail(cr, uid , template_id[0],
#                     context.get('active_id'), force_send=True)
#        return {'type': 'ir.actions.act_window_close'}

    @api.multi
    def send_email(self):
        body = ''
        email_template_obj = self.env['email.template']
        template_id = email_template_obj.search([('model', '=',
                                                'student.student')], limit=1)
        if template_id:
            for i in self:
                body += '\n' + i.note
            email_template_obj.send_mail(template_id.id,
                                         self._context.get('active_id'),
                                         force_send=True)
        return {'type': 'ir.actions.act_window_close'}

# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4:
