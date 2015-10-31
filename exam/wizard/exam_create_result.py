# -*- coding: utf-8 -*-
# Part of Odoo. See LICENSE file for full copyright and licensing details.

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
        result_obj = self.env['exam.result']
        result_subject_obj = self.env['exam.subject']

        for result in self:

            for exam in exam_obj.browse(self._context.get('active_ids')):
                if exam.standard_id:

                    for school_std_rec in exam.standard_id:
                        student_ids = student_obj.search([
                          ('standard_id', '=', school_std_rec.standard_id.id),
                          ('division_id', '=', school_std_rec.division_id.id),
                          ('medium_id', '=', school_std_rec.medium_id.id)])

                        for student in student_ids:
                            result_exists = result_obj.search([
                               ('standard_id', '=',
                                school_std_rec.standard_id.id),
                               ('student_id.division_id', '=',
                                school_std_rec.division_id.id),
                               ('student_id.medium_id', '=',
                                school_std_rec.medium_id.id),
                               ('student_id', '=', student.id)])

                            if not result_exists:
                                result_id = result_obj.create({
                                    's_exam_ids': exam.id,
                                    'student_id': student.id,
                                    'standard_id':
                                     school_std_rec.standard_id.id,
                                    'division_id':
                                     school_std_rec.division_id.id,
                                    'medium_id': school_std_rec.medium_id.id})
                                for line in exam.standard_id:
                                    result_subject_obj.create({
                                       'exam_id': result_id.id,
                                       'subject_id':
                                        line.standard_id.subject_id
                                        and line.subject_id.id or False,
                                       'minimum_marks': line.subject_id
                                        and line.subject_id.minimum_marks
                                        or 0.0,
                                       'maximum_marks': line.subject_id
                                        and line.subject_id.maximum_marks
                                        or 0.0})
                else:
                    raise except_orm(_('Error !'),
                                     _('Please Select Standard Id.'))
            return {}
