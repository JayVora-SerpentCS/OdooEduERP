# See LICENSE file for full copyright and licensing details.

from odoo import fields, models


class MailTemplate(models.Model):
    _inherit = "mail.template"

    def generate_email(self, res_ids, fields=None):
        '''Method to generate email.'''
        ret = super(MailTemplate, self).generate_email(res_ids, fields=fields)

        if (self._context.get('body_html', False) or
                self._context.get('subject', False) or
                self._context.get('email_to', False)):
            ret['body_html'] = self._context['body_text']
            ret['subject'] = self._context['subject']
            ret['email_to'] = self._context['email_to']
            return ret


class SendMail(models.TransientModel):
    """Defining TransientModel to send mail."""

    _name = "send.email"
    _description = "Send Mail"

    note = fields.Text('Text')

    def send_email(self):
        '''Method to send email.'''
        body = ''
        email_template_obj = self.env['mail.template']
        # search the model student.student
        template_id = email_template_obj.search([
                                        ('model', '=', 'student.student')],
                                        limit=1)
        if template_id:
            for i in self:
                body += '\n' + i.note
            email_template_obj.send_mail(template_id.id,
                                         self._context.get('active_id'),
                                         force_send=True)
        return {'type': 'ir.actions.act_window_close'}
