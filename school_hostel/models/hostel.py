# -*- encoding: UTF-8 -*-
# -----------------------------------------------------------------------------
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
# -----------------------------------------------------------------------------

from openerp import models, fields, api, _
from openerp.exceptions import except_orm


class hostel_type(models.Model):

    _name = 'hostel.type'

    name = fields.Char('Hostel Name', required=True)
    type = fields.Selection([('boys', 'Boys'), ('girls', 'Girls'),
                             ('common', 'Common')], 'Hostel Type',
                            required=True, default='common')
    other_info = fields.Text('Other Information')
    rector = fields.Many2one('res.partner', 'Rector')
    room_ids = fields.One2many('hostel.room', 'name', 'Room')


class hostel_room(models.Model):

    _name = 'hostel.room'

    @api.one
    @api.depends('student_ids')
    def _check_availability(self):
        room_availability = 0
        for data in self:
            count = 0
            for student in self.student_ids:
                count += 1
            room_availability = data.student_per_room - count
            if room_availability < 0:
                raise except_orm(_("You can not assign room\
                more than %s student" % data.student_per_room))
            else:
                self.availability = room_availability

    name = fields.Many2one('hostel.type', 'Hostel')
    floor_no = fields.Integer('Floor No.', default=1)
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
                         'Room number must be unique!')]
    _sql_constraints = [('floor_per_hostel', 'check(floor_no < 10)',
                         'Error ! Floor per hostel should be less than 10.')]
    _sql_constraints = [('student_per_room_greater',
                         'check(student_per_room < 10)',
                         'Error ! Student per room should be less than 10.')]


class hostel_student(models.Model):

    _name = 'hostel.student'

    @api.one
    @api.depends('room_rent', 'paid_amount')
    def _get_remaining_fee_amt(self):
        if self.room_rent and self.paid_amount:
            self.remaining_amount = self.room_rent - self.paid_amount
        else:
            self.remaining_amount = 0.0

    @api.multi
    def confirm_state(self):
        self.write({'status': 'confirm'})
        return True

    @api.multi
    def reservation_state(self):
        self.write({'status': 'reservation'})
        return True

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
    status = fields.Selection([('draft', 'Draft'),
                               ('reservation', 'Reservation'),
                               ('confirm', 'Confirm')], 'Status',
                              default='draft')

    _sql_constraints = [('admission_date_greater',
                         'check(discharge_date >= admission_date)',
                         'Error ! Discharge Date cannot be set\
                          before Admission Date.')]


class bed_type(models.Model):

    _name = 'bed.type'
    _description = 'Type of Bed in Hostel'

    name = fields.Char('Name', required=True)
    description = fields.Text('Description')
