# -*- coding: utf-8 -*-
# See LICENSE file for full copyright and licensing details.


from odoo import models, fields, api


class TerminateReasonTransport(models.TransientModel):
    _inherit = 'terminate.reason'

    transport_info = fields.Text('Transport Info')

    @api.model
    def default_get(self, fields):
        res = super(TerminateReasonTransport, self).default_get(fields)
        student = self._context.get('active_id')
        student_obj = self.env['student.student'].browse(student)
        student_transport = self.env['transport.registration'].\
            search([('part_name', '=', student_obj.id),
                    ('state', 'in', ['confirm', 'pending', 'paid'])])
        transport_msg = ''
        if student_transport:
            for rec in student_transport:
                transport_msg += '\nStudent is registered for the root' + ' '\
                    + rec.name.name + ' ' + 'the vehicle number is' + ' ' +\
                    rec.vehicle_id.vehicle + ' and point number is ' +\
                    rec.point_id.name
        res.update({'transport_info': transport_msg})
        return res
