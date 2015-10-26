# -*- coding: UTF-8 -*-
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


class mail_template(models.TransientModel):

    _inherit = "mail.template"

    @api.multi
    def generate_email(self, res_ids, fields=None):
        self._context = dict(self._context or {})
        ret = super(mail_template, self).generate_email(res_ids, fields=fields)
        if self._context.get('body_html', False)\
            or self._context.get('subject', False) or self._context.get(
                                                            'email_to', False):
            ret['body_html'] = self._context['body_text']
            ret['subject'] = self._context['subject']
            ret['email_to'] = self._context['email_to']
            return ret
        else:
            return ret


class send_email(models.TransientModel):

    _name = "send.email"

    note = fields.Text('Text')

    @api.multi
    def send_email(self):
        subject = 'Emergency mail'
        body = ''
        email_template_obj = self.env['email.template']
        template_id = email_template_obj.search([
            ('model', '=', 'student.student')], limit=1)
        if template_id:
            for i in self:
                body += '\n' + i.note
            email_template_obj.send_mail(template_id.id,
                self._context.get('active_id'), force_send=True)
        return {'type': 'ir.actions.act_window_close'}
