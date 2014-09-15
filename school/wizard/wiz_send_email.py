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

from openerp.osv import fields, osv
import email

class email_template(osv.osv):
    _inherit = "email.template"
    
    def generate_email(self, cr, uid, template_id, res_id, context=None):
        if context is None:
            context = {}
        ret = super(email_template, self).generate_email(cr, uid, template_id, res_id, context=context)
        if context.get('body_text', False) or context.get('subject', False) or context.get('email_to', False):
            ret['body_text'] = context['body_text']
            ret['subject'] = context['subject']
            ret['email_to'] = context['email_to']
            return ret
        else:
            return ret

class send_email(osv.osv):
    _name = "send.email"
    _columns = {
        'note':fields.text('Text'),      
    }

    def send_email(self, cr, uid, ids, context=None):
        subject = 'Emergency mail'
        body = ''
        
        email_template = self.pool.get('email.template')
        template_id = email_template.search(cr, uid, [('model', '=', 'student.student')], context=context)
        if template_id:
            email_template_brw = email_template.browse(cr, uid, template_id[0])
            
            for i in self.browse(cr, uid, ids):
                body += '\n' + i.note
            email_template.send_mail(cr, uid , template_id[0], context.get('active_id'), force_send=True)
        return {'type': 'ir.actions.act_window_close'} 

# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4: