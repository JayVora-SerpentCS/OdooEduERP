from datetime import date, datetime
from odoo import models, fields, api, _
from odoo.exceptions import ValidationError
import urllib.request, ssl
from lxml import etree as ET
from lxml.builder import E

class SMSProvider(models.Model):
    _name = 'sms.provider'
    _description = 'SMS Provider'
    name = fields.Char('Provider Name')
    active = fields.Boolean('Active', default='True')


class SMSSettings(models.Model):
    _name = 'sms.settings'
    _description = 'SMS Settings'

    @api.depends('service_provider_id', 'sender_number')
    def _compute_name(self):
        """Method to compute name"""
        for rec in self:
            rec.name = str(rec.service_provider_id.name) + ' - ' + str(rec.sender_number)

    name = fields.Char(compute='_compute_name', string='Name')
    service_provider_id = fields.Many2one('sms.provider', string='Service Provider')
    sender_number = fields.Char(string='Sender Number/ Account ID', help='Sender Number')
    password = fields.Char(string='Password')
    masking = fields.Char(string='Masking')
    active = fields.Boolean('Active', default='True')


class SMSSending(models.Model):
    _name = 'sms.sending'
    _description = 'SMS Sending'

    @api.multi
    def load_students(self):
        student_list = []
        stud_obj = self.env['student.student']
        for rec in self:
            if rec.school_id:
                if rec.standard_id:
                    student_list = [{'roll_no':std.roll_no,  'name':std.id,  'mobile_number':std.contact_mobile} for std in stud_obj.search([('school_id', '=', rec.school_id.id), ('standard_id', '=', rec.standard_id.id), ('state', '=', rec.student_type)])]
            else:
                if rec.school_id:
                    student_list = [{'roll_no':std.roll_no,  'name':std.id,  'mobile_number':std.contact_mobile} for std in stud_obj.search([('school_id', '=', rec.school_id.id), ('state', '=', rec.student_type)])]
                else:
                    student_list = [(0, 0, {'roll_no':std.roll_no,  'name':std.id,  'mobile_number':std.contact_mobile}) for std in stud_obj.search([('standard_id', '=', rec.standard_id.id), ('state', '=', rec.student_type)])]
            rec.update({'recipient_ids': student_list})
            rec.state = 'loaded'

    @api.multi
    def send_sms(self):
        for rec in self:
            sender_number = 8583
            password = rec.service_id.password
            masking = rec.service_id.masking
            network = rec.service_id.service_provider_id.name
            recipient_ids = rec.recipient_ids
            message = rec.message
            system_log = ''
            print(network)
            if network == 'Ufone':
                for recipient in recipient_ids:
                    phone_no = recipient.mobile_number
                    context = ssl._create_unverified_context()
                    msg_string = 'https://bsms.ufone.com/bsms_v8_api/sendapi-0.3.jsp?id=' + str(sender_number) + '&message=' + str(message.replace(' ', '%20')) + '&shortcode=' + str(masking) + '&lang=English&password=' + str(password) + '&mobilenum=' + str(phone_no) + '&groupname=&messagetype=Nontransactional'
                    req = urllib.request(msg_string)
                    response = urllib.response(req, context=context)

                rec.state = 'done'
            else:
                if network == 'Telenore':
                    authentication = 'https://telenorcsms.com.pk:27677/corporate_sms2/api/auth.jsp?msisdn=' + str(sender_number) + '&password=' + str(password)
                    auth_req = urllib.request(authentication)
                    auth_response = urllib.response(auth_req)
                    data = auth_response.read()
                    t = ET.fromstring(data)
                    session_id = ET.fromstring(data)[1].text
                    recv_list = ''
                    valid = 0
                    for recipient in recipient_ids:
                        phone_no = recipient.mobile_number
                        if phone_no:
                            cell_no = phone_no()
                            if len(cell_no) == 12:
                                if cell_no[:3] == '923':
                                    valid = valid + 1
                                    recv_list = recv_list + ',' + str(cell_no)
                                else:
                                    system_log = system_log + str(cell_no) + 'Invalid format'
                            else:
                                system_log = system_log + str(phone_no) + 'not 12 digit no'
                        else:
                            system_log = system_log + 'No field is empty'

                    send_url = 'https://telenorcsms.com.pk:27677/corporate_sms2/api/sendsms.jsp?session_id=' + str(session_id) + '&to=' + str(recv_list) + '&text=' + str(message.replace(' ', '%20')) + '&mask=Edex%20School'
                    send_req = urllib.request(send_url)
                    send_response = urllib.response(send_req)
                    system_log = system_log + '*******' + send_response.read()
                    rec.state = 'done'
                else:
                    if network == 'Smile':
                        import requests
                        recv_list = ''
                        url = 'http://api.smilesn.com/sendsms'
                        req = urllib.request.Request(url)
                        valid = 0
                        for recipient in recipient_ids:
                            phone_no = recipient.mobile_number
                            if phone_no:
                                cell_no = phone_no.strip()
                                if len(cell_no) == 12:
                                    if cell_no[:3] == '923':
                                        valid = valid + 1
                                        recv_list = recv_list + ',' + str(cell_no)
                                    else:
                                        system_log = system_log + str(cell_no) + 'Invalid format'
                                else:
                                    system_log = system_log + str(phone_no) + 'not 12 digit no'
                            else:
                                system_log = system_log + 'No field is empty'

                        data = {'hash':password, 
                         'receivenum':str(recv_list),  'sendernum':str(sender_number),  'textmessage':str(message)}
                        x = requests.post(url, data=data)
                        system_log = system_log + '\n*****Network Response' + x.text
                        rec.state = 'done'

    name = fields.Char(string='Name', required=True)
    service_id = fields.Many2one('sms.settings', string='Service', required=True)
    school_id = fields.Many2one('school.school', string='School', required=True)
    standard_id = fields.Many2one('school.standard', string='Class')
    student_type = fields.Selection([('done', 'Registered'), ('terminate', 'Terminated'), ('alumni', 'Alumni')], 'Student Type',
      default='done', required=True)
    sms_date = fields.Date(string='Date', required=True)
    message = fields.Text(string='Message', required=True)
    recipient_ids = fields.One2many('sms.sending.line', 'sms_sending_id', 'Recipients')
    state = fields.Selection([('draft', 'Draft'), ('loaded', 'Loaded'), ('done', 'Sent')], 'State', default='draft')


class SMSSendingLine(models.Model):
    _name = 'sms.sending.line'
    _description = 'SMS Sending Line'
    name = fields.Many2one('student.student', 'Name')
    roll_no = fields.Integer('Roll No.', help='Roll Number')
    mobile_number = fields.Char('Mobile Number')
    sms_sending_id = fields.Many2one('sms.sending', 'SMS Sending')

