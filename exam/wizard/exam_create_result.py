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
        result_subject_obj = self.env['exam.subject']

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
                                  ('student_id', '=', student.id)]
                        result_exists = result_obj.search(domain)
                        if not result_exists:
                            standard_id = school_std_rec.standard_id.id
                            rs_dict = {'s_exam_ids': exam.id,
                                       'student_id': student.id,
                                       'standard_id': standard_id}
                            result_id = result_obj.create(rs_dict)

                            for line in exam.standard_id:
                                for subject in line.subject_ids:
                                    sub_dict = {'exam_id': result_id.id,
                                                'subject_id': subject.id or
                                                False,
                                                'minimum_marks': subject.
                                                minimum_marks or 0.0,
                                                'maximum_marks': subject.
                                                maximum_marks or 0.0}
                                    result_subject_obj.create(sub_dict)
            else:
                raise except_orm(_('Error !'),
                                 _('Please Select Standard Id.'))
        return {}
