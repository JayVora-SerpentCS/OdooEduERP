# -*- coding: utf-8 -*-
# Part of Odoo. See LICENSE file for full copyright and licensing details.

from openerp import models, fields, api, _
from openerp.exceptions import except_orm
from datetime import datetime


class HostelType(models.Model):

    _name = 'hostel.type'

    name = fields.Char('HOSTEL Name', required=True)
    type = fields.Selection([('boys', 'Boys'), ('girls', 'Girls'),
                             ('common', 'Common')], 'HOSTEL Type',
                            required=True, default='common')
    other_info = fields.Text('Other Information')
    rector = fields.Many2one('hr.employee', 'Rector')
    room_ids = fields.One2many('hostel.room', 'name', 'Room')
    school_id = fields.Many2one('school.school', 'School')


class HostelRoom(models.Model):

    _name = 'hostel.room'
    _rec_name = 'full_name'
    
    @api.one
    @api.depends('name', 'room_no', 'floor_no')
    def _get_name(self):
        self.full_name = str(self.name and self.name.name or '')
        self.full_name += "/"+str(self.floor_no and \
                  self.floor_no.name or '')
        self.full_name += "/"+str(self.room_no or '')
        if not self.name and not self.room_no and not self.floor_no:
            self.full_name = ''

    @api.one
    @api.depends('student_ids', 'student_per_room')
    def _check_availability(self):
        self.availability = 0
        students = len([stu for stu in self.student_ids\
                          if stu.state not in ['draft', 'discharge']])
        room_availability = self.student_per_room - students
        if room_availability < 0:
            raise except_orm(_("You can not assign \
            more than %s student" % self.student_per_room))
        self.availability = room_availability

    full_name = fields.Char('Identification Number', compute="_get_name")
    name = fields.Many2one('hostel.type', 'HOSTEL')
    floor_no = fields.Many2one('hostel.floor', 'Floor No.')
    room_no = fields.Char('Room No.', required=True)
    student_per_room = fields.Integer('Student Per Room', required=True)
    availability = fields.Float(compute='_check_availability',
                                string="Availability")
    student_ids = fields.One2many('hostel.student',
                                  'hostel_room_id', 'Student')
    telephone = fields.Boolean('Telephone access')
    ac = fields.Boolean('Air Conditioning')
    private_bathroom = fields.Boolean('Private Bathroom')
    guest_sofa = fields.Boolean('Guest sofa-bed')
    tv = fields.Boolean('Television')
    internet = fields.Boolean('Internet Access')
    refrigerator = fields.Boolean('Refrigerator')
    microwave = fields.Boolean('Microwave')

    _sql_constraints = [('room_no_unique', 'unique(room_no)',
                         'Room number must be unique!'),
                        ('student_per_room_greater',
                         'check(student_per_room < 10)',
                         'Error ! Student per room should be less than 10.')]


class HostelStudent(models.Model):

    _name = 'hostel.student'
    _rec_name = 'hostel_id'

    @api.one
    @api.depends('room_rent', 'paid_amount')
    def _get_remaining_fee_amt(self):
        self.remaining_amount = 0.0
        if self.room_rent and self.paid_amount:
            self.remaining_amount = self.room_rent - self.paid_amount

    @api.multi
    def confirm_state(self):
        today = datetime.now()
        return self.write({'state': 'confirm',
                           'admission_date' : today})

    @api.multi
    def reservation_state(self):
        return self.write({'state': 'reservation'})
    
    @api.multi
    def discharge_state(self):
        today = datetime.today()
        return self.write({'state' : 'discharge',
                           'discharge_date' : today})

    @api.multi
    def print_fee_receipt(self):
        data = self.read([])[0]
        datas = {
            'ids': [data['id']],
            'form': data,
            'model': 'hostel.student',
        }
        return {'type': 'ir.actions.report.xml',
                'report_name': 'school_hostel.hostel_fee_reciept',
                'datas': datas}

    hostel_room_id = fields.Many2one('hostel.room', 'Hostel Room')
    hostel_id = fields.Char('Hostel ID', readonly=True,
                            default=lambda obj:
                            obj.env['ir.sequence'].get('hostel.student'))
    student_id = fields.Many2one('student.student', 'Student')
    school_id = fields.Many2one('school.school', 'School')
    room_rent = fields.Float('Total Room Rent', required=True)
    bed_type = fields.Many2one('bed.type', 'Bed Type')
    admission_date = fields.Datetime('Admission Date')
    discharge_date = fields.Datetime('Discharge Date')
    paid_amount = fields.Float('Paid Amount')
    remaining_amount = fields.Float(compute='_get_remaining_fee_amt',
                                    string='Remaining Amount')
    state = fields.Selection([('draft', 'Draft'),
                              ('reservation', 'Reserved'),
                              ('confirm', 'Confirmed'),
                              ('discharge', 'Discharged')], 'Status',
                              default='draft')

    _sql_constraints = [('admission_date_greater',
                         'check(discharge_date >= admission_date)',
                         'Error ! Discharge Date cannot be set\
                          before Admission Date.')]


class BedType(models.Model):

    _name = 'bed.type'
    _description = 'Type of Bed in HOSTEL'

    name = fields.Char('Name', required=True)
    description = fields.Text('Description')


class HostelFloor(models.Model):
    
    _name = 'hostel.floor'
    _inherit = 'bed.type'