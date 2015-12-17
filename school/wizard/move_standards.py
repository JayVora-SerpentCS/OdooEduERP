# -*- coding: utf-8 -*-
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
from openerp import models, fields, api, _
from openerp.exceptions import except_orm


class MoveStandards(models.TransientModel):

    _name = 'move.standards'

    academic_year_id = fields.Many2one('academic.year', 'Academic Year',
                                       required=True)

    @api.multi
    def move_start(self):
        if self._context is None:
            self._context = {}
        if not self._context.get('active_ids'):
            return {}
        academic_obj = self.env['academic.year']
        school_standard_obj = self.env['school.standard']
        standard_obj = self.env["standard.standard"]
        result_obj = self.env['exam.result']
        history_obj = self.env["student.history"]
        for data in self:
            active_ids = self._context.get('active_ids')
            for standards in school_standard_obj.browse(active_ids):
                for student in standards.student_ids:
                    academic_year_id = data.academic_year_id.id
                    stud_year_ids = history_obj.search([('academice_year_id',
                                                         '=',
                                                         academic_year_id),
                                                        ('student_id', '=',
                                                         student.id)])
                    year_id = academic_obj.next_year(student.year.sequence)
                    if year_id and year_id != data.academic_year_id.id:
                        continue
                    if stud_year_ids:
                        raise except_orm(_('Warning !'), _('Please Select \
                                                            Next Academic \
                                                            year.'))
                    else:
                        standard_id = student.standard_id.id
                        division_id = student.division_id.id
                        medium_id = student.medium_id.id
                        res = result_obj.search([('standard_id', '=',
                                                  standard_id),
                                                 ('standard_id.division_id',
                                                  '=', division_id),
                                                 ('standard_id.medium_id',
                                                  '=', medium_id),
                                                 ('student_id', '=',
                                                  student.id)])
                        result_data = False
                        if res:
                            result_data = result_obj.browse(res.id)
                        if result_data and result_data.result == "Pass":
                            seq = standards.standard_id.sequence
                            next_class_id = standard_obj.next_standard(seq)
                            if next_class_id:
                                student.write({'year':
                                               data.academic_year_id.id,
                                               'standard_id': next_class_id,
                                               })
                                year = student.year.id
                                sta_id = standards.standard_id.id
                                div_id = standards.division_id.id
                                med_id = standards.medium_id.id
                                result = result_data.result
                                percent = result_data.percentage
                                history_obj.create({'student_id': student.id,
                                                    'academice_year_id': year,
                                                    'standard_id': sta_id,
                                                    'division_id': div_id,
                                                    'medium_id': med_id,
                                                    'result': result,
                                                    'percentage': percent
                                                    })
                        else:
                            raise except_orm(_("Error!"),
                                             _("Student is not eligible \
                                               for Next Standard."))
        return {}

# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4:
