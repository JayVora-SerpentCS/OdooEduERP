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
from openerp import models, api, _
from openerp.exceptions import except_orm


class exam_create_result(models.TransientModel):

    _name = 'exam.create.result'

    @api.multi
    def generate_result(self):
        if not self._context.get('active_ids'):
            return {}
        exam_obj = self.env['exam.exam']
        student_obj = self.env['student.student']
        resobj = self.env['exam.result']
        subject_obj = self.env['exam.subject']
        for result in self:
            for exam in exam_obj.browse(self._context.get('active_ids')):
                if exam.standard_id:
                    for school_std_rec in exam.standard_id:
                        stand_id = school_std_rec.standard_id.id
                        div_id = school_std_rec.division_id.id
                        med_id = school_std_rec.medium_id.id
                        student_ids = student_obj.search([('standard_id', '=',
                                                           stand_id),
                                                          ('division_id', '=',
                                                           div_id),
                                                          ('medium_id', '=',
                                                           med_id)])
                        for stud in student_ids:
                            result = resobj.search([('standard_id', '=',
                                                     stand_id),
                                                    ('student_id.division_id',
                                                     '=', div_id),
                                                    ('student_id.medium_id',
                                                     '=', med_id),
                                                    ('student_id', '=',
                                                     stud.id)])
                            if not result:
                                res = resobj.create({'s_exam_ids': exam.id,
                                                     'student_id': stud.id,
                                                     'standard_id': stand_id,
                                                     'division_id': div_id,
                                                     'medium_id': med_id
                                                     })
                                for line in exam.standard_id:
                                    sub_id = (line.standard_id.subject_id and
                                              line.subject_id.id or False),
                                    min = (line.subject_id and
                                               line.subject_id.minimum_marks
                                               or 0.0)
                                    max = (line.subject_id and
                                               line.subject_id.maximum_marks
                                               or 0.0)
                                    subject_obj.create({'exam_id': res.id,
                                                        'subject_id': sub_id,
                                                        'minimum_marks': min,
                                                        'maximum_marks': max
                                                        })
                else:
                    raise except_orm(_('Error !'), _('Please \
                                                      Select Standard Id.'))
            return {}

# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4:
