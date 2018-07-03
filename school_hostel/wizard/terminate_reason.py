# -*- coding: utf-8 -*-
# See LICENSE file for full copyright and licensing details.


from odoo import models, fields, api


class TerminateReasonHostel(models.TransientModel):
    _inherit = 'terminate.reason'

    hostel_info = fields.Text('Hostel Info')

    @api.model
    def default_get(self, fields):
        '''Override method to dispaly message if student is registered in
        hostel while terminationg'''
        res = super(TerminateReasonHostel, self).default_get(fields)
        student = self._context.get('active_id')
        student_obj = self.env['student.student'].browse(student)
        student_hostel = self.env['hostel.student'].\
            search([('student_id', '=', student_obj.id),
                    ('status', 'in', ['reservation', 'pending', 'paid'])])
        hostel_msg = ''
        if student_hostel:
            hostel_msg += '\nStudent is registered in the hostel' +\
                ' ' + student_hostel.hostel_info_id.name + ' ' +\
                'the hostel id is' + ' ' + student_hostel.hostel_id +\
                'and room number is ' + student_hostel.room_id.room_no
        res.update({'hostel_info': hostel_msg})
        return res

    @api.multi
    def save_terminate(self):
        student = self._context.get('active_id')
        student_obj = self.env['student.student'].browse(student)
        student_hostel = self.env['hostel.student'].\
            search([('student_id', '=', student_obj.id),
                    ('status', 'in', ['reservation', 'pending', 'paid'])])
        if student_hostel:
            student_hostel.update({'active': False})
            student_hostel.room_id._compute_check_availability()
        return super(TerminateReasonHostel, self).save_terminate()
