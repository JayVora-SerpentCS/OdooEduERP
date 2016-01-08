# -*- coding: utf-8 -*-
# Part of Odoo. See LICENSE file for full copyright and licensing details.

from openerp import models, api, _
from openerp.exceptions import except_orm


class ExamCreateResult(models.TransientModel):
    _name = 'exam.create.result'

    @api.multi
    def generate_result(self):
        if not self._context.get('active_ids'):
            return {}
        exam_obj = self.env['exam.exam']
        result_obj = self.env['exam.result']
        result_subject_obj = self.env['exam.subject']
        for exam in exam_obj.browse(self._context.get('active_ids')):
            for timetable in exam.exam_timetable_ids:
                students = timetable.standard_id and \
                            timetable.standard_id.student_ids
                for student in students:
                    if student.state != 'draft':
                        domain = [('standard_id', '=',
                                   timetable.standard_id.id),
                                  ('student_id', '=', student.id),
                                  ('s_exam_ids', '=', exam.id)]
                        result_exists = result_obj.search(domain)
                        if not result_exists:
                            standard_id = timetable.standard_id.id
                            rs_dict = {'s_exam_ids': exam.id,
                                       'student_id': student.id,
                                       'standard_id': standard_id,
                                       }
                            result_id = result_obj.create(rs_dict)
                            for line in timetable.timetable_ids:
                                minimum_marks = line.subject_id and \
                                            line.subject_id.minimum_marks or 0.0
                                maximum_marks = line.subject_id and \
                                            line.subject_id.maximum_marks or 0.0
                                result_subject_obj.create({
                                    'subject_id': line.subject_id.id,
                                    'exam_id': result_id.id,
                                    'student_id': student.id,
                                    'minimum_marks': minimum_marks,
                                    'maximum_marks': maximum_marks
                                })
#            if not exam.standard_id:
#                raise except_orm(_('Error !'),
#                                 _('Please Select Standard Id.'))
#            for school_std_rec in exam.exam_timetable_ids:
#                domain = [('standard_id', '=',
#                           school_std_rec.standard_id.id),
#                          ('division_id', '=',
#                           school_std_rec.division_id.id),
#                          ('medium_id', '=', school_std_rec.medium_id.id)]
#                student_ids = student_obj.search(domain)
#                for student in student_ids:
#                    domain = [('standard_id', '=',
#                               school_std_rec.standard_id.id),
#                              ('student_id.division_id', '=',
#                               school_std_rec.division_id.id),
#                              ('student_id.medium_id', '=',
#                               school_std_rec.medium_id.id),
#                              ('student_id', '=', student.id)]
#                    result_exists = result_obj.search(domain)
#
#                    if not result_exists:
#                        standard_id = school_std_rec.standard_id.id
#                        division_id = school_std_rec.division_id.id
#                        rs_dict = {'s_exam_ids': exam.id,
#                                   'student_id': student.id,
#                                   'standard_id': standard_id,
#                                   'division_id': division_id,
#                                   'medium_id': school_std_rec.medium_id.id
#                                   }
#                        result_id = result_obj.create(rs_dict)
#
#                        for line in exam.standard_id:
#                            sub_dict = {'exam_id': result_id.id,
#                                        'subject_id':
#                                         line.standard_id.subject_id
#                                         and line.subject_id.id or False,
#                                        'minimum_marks': line.subject_id
#                                         and line.subject_id.minimum_marks
#                                         or 0.0,
#                                        'maximum_marks': line.subject_id
#                                         and line.subject_id.maximum_marks
#                                         or 0.0}
#                            result_subject_obj.create(sub_dict)
        return True
