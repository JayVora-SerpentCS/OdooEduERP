# -*- coding: utf-8 -*-
# See LICENSE file for full copyright and licensing details.

from odoo import models, api, _
from odoo.exceptions import except_orm


class ExamCreateResult(models.TransientModel):
    _name = 'exam.create.result'

    @api.multi
    def generate_result(self):
        if not self._context.get('active_ids'):
            return {}
        exam_obj = self.env['exam.exam']
        student_obj = self.env['student.student']
        result_obj = self.env['exam.result']
#        result_subject_obj = self.env['exam.subject']
        result_list = []

        for exam in exam_obj.browse(self._context.get('active_ids')):
            if exam.standard_id:
                for school_std_rec in exam.standard_id:
                    domain = [('standard_id', '=',
                               school_std_rec.standard_id.id),
                              ('division_id', '=',
                               school_std_rec.division_id.id),
                              ('medium_id', '=', school_std_rec.medium_id.id)]
                    student_ids = student_obj.search(domain)
                    for student in student_ids:
                        domain = [('standard_id', '=',
                                   school_std_rec.standard_id.id),
                                  ('student_id.division_id', '=',
                                   school_std_rec.division_id.id),
                                  ('student_id.medium_id', '=',
                                   school_std_rec.medium_id.id),
                                  ('student_id', '=', student.id),
                                  ('s_exam_ids', '=', exam.id)]
                        result_exists = result_obj.search(domain)
                        if result_exists:
                            [result_list.append(res.id) for res in\
                                        result_exists]

                        if not result_exists:
                            standard_id = school_std_rec.standard_id.id
                            division_id = school_std_rec.division_id.id
                            rs_dict = {'s_exam_ids': exam.id,
                                       'student_id': student.id,
                                       'standard_id': standard_id,
                                       'division_id': division_id,
                                       'medium_id':
                                            school_std_rec.medium_id.id,
                                       'grade_system': exam.grade_system.id
                                       }
                            exam_line = []
                            for line in exam.exam_timetable_ids:
                                for sub_line in line.timetable_ids:
                                    sub_vals = {'subject_id': sub_line.
                                                              subject_id.id,
                                                'minimum_marks': sub_line
                                                                .subject_id
                                                                .minimum_marks,
                                                'maximum_marks': sub_line
                                                               .subject_id
                                                               .maximum_marks,
                                              }
                                    exam_line.append((0, 0, sub_vals))
                            rs_dict.update({'result_ids': exam_line})
                            result = result_obj.create(rs_dict)
                            result_list.append(result.id)

            else:
                raise except_orm(_('Error !'),
                                 _('Please Select Standard Id.'))

        return {'name': _('Result Info'),
                'view_type': 'form',
                'view_mode': 'tree,form',
                'res_model': 'exam.result',
                'type': 'ir.actions.act_window',
                'res_id': result_list}
