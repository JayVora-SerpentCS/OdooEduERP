# -*- coding: utf-8 -*-
# Part of Odoo. See LICENSE file for full copyright and licensing details.

from openerp import models, fields, api, _
from openerp.exceptions import except_orm


class SchoolTeacher(models.Model):
    ''' Defining a Teacher information '''
    _name = 'school.teacher'
    _description = 'Teacher Information'

    employee_id = fields.Many2one('hr.employee', 'Employee ID',
                                  ondelete="cascade",
                                  delegate=True, select=True, required=True)
    standard_id = fields.Many2one('school.standard',
                                  "Responsibility of Academic Class",
                                  help="Standard for which the teacher\
                                  responsible for.")
    stand_id = fields.Many2one('standard.standard', "Course",
                               related="standard_id.standard_id", store=True)
    subject_id = fields.Many2many('subject.subject', 'subject_teacher_rel',
                                  'teacher_id', 'subject_id',
                                  'Course-Subjects')
    school_id = fields.Many2one('school.school', "Campus",
                                related="standard_id.school_id", store=True)
    category_ids = fields.Many2many('hr.employee.category',
                                    'employee_category_rel', 'emp_id',
                                    'category_id', 'Tags')
    department_id = fields.Many2one('hr.department', 'Department')
    job_id = fields.Many2one('hr.job', 'Job Title')
    is_parent = fields.Boolean('Is Parent')
    stu_parent_id = fields.Many2one('school.parent', 'Parent ref')
    student_id = fields.Many2many('student.student',
                                  'students_lecturer_parent_rel',
                                  'students_lecturer_parent_id', 'student_id',
                                  'Children')

    @api.model
    def create(self, vals):
        teacher_id = super(SchoolTeacher, self).create(vals)
        user_vals = {'name': teacher_id.name,
                     'login': teacher_id.work_email,
                     'email': teacher_id.work_email,
                     'teacher_create': teacher_id,
                     'school_id': teacher_id.school_id.id}
        user_id = self.env['res.users'].create(user_vals)
        teacher_id.employee_id.write({'user_id': user_id.id})
        if vals.get('is_parent'):
            self.parent_crt(teacher_id)
        return teacher_id

    @api.multi
    def parent_crt(self, manager_id):
        stu_parent = []
        if manager_id.stu_parent_id:
            stu_parent = manager_id.stu_parent_id
        if not stu_parent:
            emp_user = manager_id.employee_id
            students = [stu.id for stu in manager_id.student_id]
            parent_vals = {'name': manager_id.name,
                           'email': emp_user.work_email,
                           'parent_create_mng': 'parent',
                           'user_ids': [(6, 0, [emp_user.user_id.id])],
                           'partner_id': emp_user.user_id.partner_id.id,
                           'student_id': [(6, 0, students)]}
            stu_parent = self.env['school.parent'].create(parent_vals)
            manager_id.write({'stu_parent_id': stu_parent.id})
        user = stu_parent.user_ids
        user_rec = user[0]
        parent_grp_id = self.env['ir.model.data'
                                 ].get_object('school',
                                              'group_school_parent')
        groups = parent_grp_id
        if user_rec.groups_id:
            groups = user_rec.groups_id
            groups += parent_grp_id
        group_ids = [group.id for group in groups]
        user_rec.write({'groups_id': [(6, 0, group_ids)]})

    @api.multi
    def write(self, vals):
        if vals.get('is_parent'):
            self.parent_crt(self)
        if vals.get('student_id'):
            self.stu_parent_id.write({'student_id': vals.get('student_id')})
        if not vals.get('is_parent'):
            user_rec = self.employee_id.user_id
            ir_obj = self.env['ir.model.data']
            parent_grp_id = ir_obj.get_object('school', 'group_school_parent')
            groups = parent_grp_id
            if user_rec.groups_id:
                groups = user_rec.groups_id
                groups -= parent_grp_id
            group_ids = [group.id for group in groups]
            user_rec.write({'groups_id': [(6, 0, group_ids)]})
        return super(SchoolTeacher, self).write(vals)

    @api.onchange('address_id')
    def onchange_address_id(self):
        if self.address_id:
            self.work_phone = self.address_id.phone,
            self.mobile_phone = self.address_id.mobile

    @api.onchange('department_id')
    def onchange_department_id(self):
        if self.department_id:
            self.parent_id = (self.department_id and
                              self.department_id.manager_id and
                              self.department_id.manager_id.id) or False

    @api.onchange('user_id')
    def onchange_user(self):
        if self.user_id:
            self.name = self.name or self.user_id.name
            self.work_email = self.user_id.email
            self.image = self.image or self.user_id.image

    @api.onchange('school_id')
    def onchange_school(self):
        if self.school_id:
            self.address_id = self.school_id.company_id.partner_id.id
            self.mobile_phone = self.school_id.company_id.partner_id.mobile
            self.work_location = self.school_id.company_id.partner_id.city
            self.work_email = self.school_id.company_id.partner_id.email
            self.work_phone = self.school_id.company_id.partner_id.phone

    @api.constrains('standard_id')
    def check_standard_id(self):
        if self.standard_id:
            if self.standard_id.user_id:
                if self.standard_id.user_id.id != self.id:
                    raise except_orm(_('Warning'),
                                     _(str(self.standard_id.standard_id.name) +
                                       ' Course has already assigned\
                                       Faculty.\n If you need change the\
                                       faculty please change in Course\
                                       configuration.'))
            self.work_phone = self.school_id.company_id.partner_id.phone


class ResUsers(models.Model):

    _inherit = "res.users"

    @api.model
    def create(self, vals):
        user_rec = super(ResUsers, self).create(vals)
        if vals.get('teacher_create'):
            teacher_grp_id = self.pool.get(
                                       'ir.model.data').get_object(
                                                    self._cr,
                                                    self._uid,
                                                    'school',
                                                    'group_school_teacher')
            groups = teacher_grp_id
            if user_rec.groups_id:
                groups = user_rec.groups_id
                groups += teacher_grp_id
            group_ids = [group.id for group in groups]
            user_rec.write({'groups_id': [(6, 0, group_ids)]})
        return user_rec


class StudentFeedback(models.Model):
    _name = 'student.feedback'
    _descripation = 'Student Feedback'
    _rec_name = 'student_id'

    @api.model
    def _get_student(self):
        user_rec = self.env['res.users'].browse(self._uid)
        student_group = self.pool.get('ir.model.data').get_object(
                                                    self._cr,
                                                    self._uid,
                                                    'school',
                                                    'group_school_student')
        groups = [grp.id for grp in user_rec.groups_id]
        if student_group.id in groups:
            student = self.env['student.student'].search([('user_id', '=',
                                                           self._uid)])
            if student:
                return student.id

    student_id = fields.Many2one("student.student", "Student Name",
                                 default=_get_student)
    type = fields.Selection([('feedback', 'Feedback'),
                             ('complain', 'Complain')])
    teacher_id = fields.Many2one('school.teacher', 'Lecturer')
    descripation = fields.Text('Descripation')
    reply_decsripation = fields.Text('Reply')
    state = fields.Selection([('draft', 'Draft'),
                             ('confirm', 'Confirm'),
                             ('done', 'Done')], 'State', default='draft')

    @api.multi
    def set_confirm(self):
        teacher_feedback_obj = self.env['teacher.feedback']
        for rec in self:
            vals = {'student_name': rec.student_id.student_name,
                    'student_feedback_id': rec.id,
                    'type': rec.type,
                    'teacher_id': rec.teacher_id.id,
                    'descripation': rec.descripation,
                    'state': 'confirm'
                    }
            teacher_feedback_obj.create(vals)
        self.state = 'confirm'

    @api.multi
    def set_done(self):
        self.state = 'done'


class TeacherFeedback(models.Model):
    _name = 'teacher.feedback'
    _descripation = 'Teacher Feedback'
    _rec_name = 'student_name'

    student_name = fields.Char("Student Name")
    student_feedback_id = fields.Many2one('student.feedback',
                                          'Student Feedback')
    type = fields.Selection([('feedback', 'Feedback'),
                             ('complain', 'Complain')])
    teacher_id = fields.Many2one('school.teacher', 'Teacher')
    descripation = fields.Text('Descripation')
    reply_decsripation = fields.Text('Reply')
    state = fields.Selection([
                             ('confirm', 'Confirm'),
                             ('done', 'Done')], 'State')

    @api.multi
    def set_done(self):
        for rec in self:
            vals = {'reply_decsripation': rec.reply_decsripation,
                    'state': 'done'}
            rec.student_feedback_id.write(vals)
        self.state = 'done'
