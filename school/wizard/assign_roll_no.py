# -*- encoding: utf-8 -*-
##############################################################################
#
#    OpenERP, Open Source Management Solution
#    Copyright (C) 2004-2009 Tiny SPRL (<http://tiny.be>).
#    Copyright (C) 2011-Today Serpent Consulting Services PVT. LTD.
#    (<http://www.serpentcs.com>)
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

from openerp import models, fields, api

# This wizard is designed for assigning the roll number to a student.


class assign_roll_no(models.TransientModel):

    _name = 'assign.roll.no'
    _description = 'Assign Roll Number'

    standard_id = fields.Many2one('standard.standard', 'Class', required=True)
    medium_id = fields.Many2one('standard.medium', 'Medium', required=True)
    division_id = fields.Many2one('standard.division', 'Division',
                                  required=True)

    @api.multi
    def assign_rollno(self):
        res = {}
        student_obj = self.env['student.student']
        for stud_data in self:
            student_ids = student_obj.search([('standard_id', '=',
                                               stud_data.standard_id.id),
                                              ('medium_id', '=',
                                               stud_data.medium_id.id),
                                              ('division_id', '=',
                                               stud_data.division_id.id)])
        number = 1
        for student in student_ids:
            student.write({'roll_no': number})
            number = number + 1
        return res

# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4:
