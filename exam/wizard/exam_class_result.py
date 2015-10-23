# -*- encoding: UTF-8 -*-
##############################################################################
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
##############################################################################

from openerp import models, fields, api, _


class result_print(models.TransientModel):

    _name = 'result.print'
    _description = 'students result'

    standard_id = fields.Many2one('school.standard', 'Standard', required=True)
    exam_id = fields.Many2one('exam.exam', 'Exam')
    year_id = fields.Many2one('academic.year', 'Academic Year', required=True)

    @api.multi
    def get_result(self):
        domain = []
        for result_line in self:
            domain = [('standard_id', '=', result_line.standard_id.id),
                      ('s_exam_ids', '=', result_line.exam_id.id)]
            return {
            'name': _('Result Info'),
            'view_type': 'form',
            "view_mode": 'tree,form',
            'res_model': 'exam.result',
            'type': 'ir.actions.act_window',
            'domain': domain,
            }
        return True
