# -*- coding: utf-8 -*-
# Part of Odoo. See LICENSE file for full copyright and licensing details.

from openerp import models, fields, api, _
from openerp.exceptions import Warning as UserError


class SelectElectiveSubject(models.TransientModel):
    '''designed for choose the payment mode for to a student'''

    _name = 'select.subject'
    _description = 'Choose Subjects'

    @api.model
    def _get_semester(self):
        stu_obj = self.env['student.student']
        student_id = stu_obj.sudo().search([('id', '=',
                                             self._context.get('active_id'))])
        return student_id.course_year_id.id

    electives_wiz_ids = fields.Many2many('subject.subject', 'elective_id',
                                         'wiz_id', 'student_elective_wiz_rel',
                                         'Electives')
    semester_id = fields.Many2one('course.years', 'Semester',
                                  default=_get_semester)

    @api.multi
    def subject_selected(self):
        """
        Add the elective subjects in student.
        """
        stu_obj = self.env['student.student']
        student_id = stu_obj.sudo().search([('id', '=',
                                             self._context.get('active_id'))])
        if student_id.state != 'register_done':
            raise UserError(_('You can not select the subjects now.'))
        ele_sub_ids = [ele.id for ele in self.electives_wiz_ids]
        student_id.sudo().write({'electives_sub_ids': [(6, 0, ele_sub_ids)]})
        return True
