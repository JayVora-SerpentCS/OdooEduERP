# -*- coding: utf-8 -*-
# Part of Odoo. See LICENSE file for full copyright and licensing details.

from openerp import models, fields, api
from openerp.tools.translate import _
from openerp.exceptions import except_orm


class transfer_vehicle(models.TransientModel):
    _name = "transfer.vehicle"
    _description = "transfer vehicle"

    name = fields.Many2one('student.student', 'Student Name', readonly=True)
    participation_id = fields.Many2one('transport.participant',
                                       'Participation', required=True)
    root_id = fields.Many2one('student.transport', 'Root', required=True)
    old_vehicle_id = fields.Many2one('transport.vehicle', 'Old Vehicle No',
                                     required=True)
    new_vehicle_id = fields.Many2one('transport.vehicle', 'New Vehicle No',
                                     required=True)

    @api.model
    def default_get(self, fields):
        result = super(transfer_vehicle, self).default_get(fields)
        if self._context.get('active_id'):
            student = self.env['student.student'].browse(
                        self._context.get('active_id'))
            if 'name' in fields:
                result.update({'name': student.id})
        return result

    @api.multi
    def onchange_participation_id(self, transport):
        if not transport:
            return {}
        transport_obj = self.env['transport.participant'].browse(transport)
        return {'value': {'root_id': transport_obj.transport_id.id,
                          'old_vehicle_id': transport_obj.vehicle_id.id}}

    @api.one
    def vehicle_transfer(self):
        stu_prt_obj = self.env['transport.participant']
        vehi_obj = self.env['transport.vehicle']
        for new_data in self.browse(self.id):
            vehi_data = vehi_obj.browse(new_data.old_vehicle_id.id)
            vehi_new_data = vehi_obj.browse(new_data.new_vehicle_id.id)
            #check for transfer in same vehicle
            if new_data.old_vehicle_id.id == new_data.new_vehicle_id.id:
                raise except_orm(_('Error !'),
                    _('Sorry you can not transfer in same vehicle.'))
            # First Check Is there vacancy or not
            person = int(vehi_data.participant) + 1
            if vehi_data.capacity < person:
                raise except_orm(_('Error !'),
                    _('There is No More vacancy on this vehicle.'))
            #remove entry of participant in old vehicle.
            participants = [prt_id.id
                            for prt_id in vehi_data.vehi_participants_ids]
            if new_data.participation_id.id in participants:
                participants.remove(new_data.participation_id.id)
            old_veh_id = vehi_obj.browse(new_data.old_vehicle_id.id)
            old_veh_id.write({'vehi_participants_ids': [(6, 0, participants)]})
            #entry of participant in new vehicle.
            participants = [prt_id.id
                            for prt_id in vehi_new_data.vehi_participants_ids]
            participants.append(new_data.participation_id.id)
            new_veh_id = vehi_obj.browse(new_data.new_vehicle_id.id)
            new_veh_id.write({'vehi_participants_ids': [(6, 0, participants)]})
            stu_prt_id = stu_prt_obj.browse(new_data.participation_id.id)
            stu_prt_id.write({'vehicle_id': new_data.new_vehicle_id.id})
        return {}
