# -*- coding: utf-8 -*-
# See LICENSE file for full copyright and licensing details.
from odoo import models, api


class TerminateReasonEvent(models.TransientModel):
    _inherit = 'terminate.reason'

    @api.multi
    def save_terminate(self):
        '''Override method to delete event participant and cancel event
        registration of student when he is terminated'''
        student = self._context.get('active_id')
        student_obj = self.env['student.student'].browse(student)
        event_regi = self.env['school.event.registration'].\
            search([('part_name_id', '=', student_obj.id)])
        if event_regi:
            for rec in event_regi:
                rec.state = 'cancel'
        event_participant = self.env['school.event.participant'].\
            search([('name', '=', student_obj.id)])
        if event_participant:
            event_participant.unlink()
        return super(TerminateReasonEvent, self).save_terminate()
