# -*- coding: utf-8 -*-
# Part of Odoo. See LICENSE file for full copyright and licensing details.

from openerp import models, fields, api, _
from openerp.exceptions import except_orm


class MoveStandards(models.TransientModel):
    _name = 'move.standards'

    academic_year_id = fields.Many2one('academic.year',
                                       'Academic Year',
                                       required=True)
    semester_id = fields.Many2one('course.years', 'Semester',
                                  required=True)

    @api.multi
    def move_start(self):
        active_ids = self._context.get('active_ids')
        if not active_ids:
            return {}
        school_standard_obj = self.env['school.standard']
        stud_history_obj = self.env["student.history"]
        for data in self:
            for standards in school_standard_obj.browse(active_ids):
                semester_list = []
                courses = standards.standard_id.course_year_ids
                [semester_list.append(sem.id) for sem in courses]
                semester_list.sort()
                sem_last_id = semester_list[-1]
                for student_id in standards.student_ids:
                    student_list = []
                    stud_year_domain = [('academice_year_id',
                                         '=',
                                         data.academic_year_id.id),
                                        ('semester_id',
                                         '=',
                                         data.semester_id.id),
                                        ('student_id', '=', student_id.id)]
                    stud_year_ids = stud_history_obj.search(stud_year_domain)
                    if stud_year_ids:
                        raise except_orm(_('Warning !'),
                                         _('Please Select'
                                           'Next Academic year.'))
                    else:
                        rec = []
                        d_one = {}
                        [rec.append(std_history.id)
                         for std_history in student_id.history_ids]
                        rec.sort()
                        if data.semester_id.id == sem_last_id:
                            d_one = {'year': data.academic_year_id.id,
                                     'course_year_id': data.semester_id.id,
                                     'electives_sub_ids': [(6, 0,
                                                            student_list)]}
                            student_id.write(d_one)
                            student_id.get_semester()
                        else:
                            d_one = {'year': data.academic_year_id.id,
                                     'course_year_id': data.semester_id.id
                                     }
                            student_id.write(d_one)
                            ctx = dict(self._context or {})
                            ctx['move_standard'] = True
                            student_id.with_context(ctx).get_semester()
        return {}
