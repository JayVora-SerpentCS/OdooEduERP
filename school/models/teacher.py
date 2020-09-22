# See LICENSE file for full copyright and licensing details.

from odoo import api, fields, models


class SchoolTeacher(models.Model):
    '''Defining a Teacher information.'''

    _name = 'school.teacher'
    _description = 'Teacher Information'

    employee_id = fields.Many2one('hr.employee', 'Employee ID',
                                  ondelete="cascade",
                                  delegate=True, required=True,
                                  help='Enter related employee')
    standard_id = fields.Many2one('school.standard',
                                  "Responsibility of Academic Class",
                                  help="Standard for which the teacher\
                                  responsible for.")
    stand_id = fields.Many2one('standard.standard', "Course",
                               related="standard_id.standard_id", store=True,
                               help='''Select standard which are 
                               assigned to teacher''')
    subject_id = fields.Many2many('subject.subject', 'subject_teacher_rel',
                                  'teacher_id', 'subject_id',
                                  'Course-Subjects',
                                  help='Select subject of teacher')
    school_id = fields.Many2one('school.school', "Campus",
                                related="standard_id.school_id", store=True,
                                help='Select school')
    category_ids = fields.Many2many('hr.employee.category',
                                    'teacher_category_rel', 'emp_id',
                                    'categ_id', 'Tags',
                                    help='Select employee category')
    department_id = fields.Many2one('hr.department', 'Department',
                                    help='Select department')
    is_parent = fields.Boolean('Is Parent',
                               help='Select this if it parent')
    stu_parent_id = fields.Many2one('school.parent', 'Related Parent',
                                    help='Enter student parent')
    student_id = fields.Many2many('student.student',
                                  'students_teachers_parent_rel',
                                  'teacher_id', 'student_id',
                                  'Children', help='Select student')
    phone_numbers = fields.Char("Phone Number", help='Student PH no')

    @api.onchange('is_parent')
    def _onchange_isparent(self):
        """Onchange method for is parent"""
        if self.is_parent:
            self.stu_parent_id = False
            self.student_id = False

    @api.onchange('stu_parent_id')
    def _onchangestudent_parent(self):
        """Onchange method for student parent records"""
        stud_list = []
        if self.stu_parent_id and self.stu_parent_id.student_id:
            for student in self.stu_parent_id.student_id:
                stud_list.append(student.id)
            self.student_id = [(6, 0, stud_list)]

    @api.model
    def create(self, vals):
        """Inherited create method to assign value to users for delegation"""
        teacher_id = super(SchoolTeacher, self).create(vals)
        user_obj = self.env['res.users']
        user_vals = {'name': teacher_id.name,
                     'login': teacher_id.work_email,
                     'email': teacher_id.work_email,
                     }
        ctx_vals = {'teacher_create': True,
                    'school_id': teacher_id.school_id.company_id.id}
        user_rec = user_obj.with_context(ctx_vals).create(user_vals)
        teacher_id.employee_id.write({'user_id': user_rec.id})
        if vals.get('is_parent'):
            self.parent_crt(teacher_id)
        return teacher_id

    def parent_crt(self, manager_id):
        """Method to create parent record based on parent field"""
        stu_parent = []
        if manager_id.stu_parent_id:
            stu_parent = manager_id.stu_parent_id
        if not stu_parent:
            emp_user = manager_id.employee_id
            students = [stu.id for stu in manager_id.student_id]
            parent_vals = {'name': manager_id.name,
                           'email': emp_user.work_email,
                           'user_ids': [(6, 0, [emp_user.user_id.id])],
                           'partner_id': emp_user.user_id.partner_id.id,
                           'student_id': [(6, 0, students)]}
            stu_parent = self.env['school.parent'].create(parent_vals)
            manager_id.write({'stu_parent_id': stu_parent.id})
        user = stu_parent.user_ids
        user_rec = user[0]
        parent_grp_id = self.env.ref('school.group_school_parent')
        groups = parent_grp_id
        if user_rec.groups_id:
            groups = user_rec.groups_id
            groups += parent_grp_id
        group_ids = [group.id for group in groups]
        user_rec.write({'groups_id': [(6, 0, group_ids)]})

    def write(self, vals):
        """Inherited write method to assign groups based on parent field"""
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
        """Onchange method for address."""
        self.work_phone = self.address_id.phone or False,
        self.mobile_phone = self.address_id.mobile or False

    @api.onchange('department_id')
    def onchange_department_id(self):
        """Onchange method for deepartment."""
        self.parent_id = (self.department_id and
                          self.department_id.manager_id and
                          self.department_id.manager_id.id) or False

    @api.onchange('user_id')
    def onchange_user(self):
        """Onchange method for user."""
        if self.user_id:
            self.name = self.name or self.user_id.name
            self.work_email = self.user_id.email
            self.image = self.image or self.user_id.image

    @api.onchange('school_id')
    def onchange_school(self):
        """Onchange method for school."""
        self.address_id = self.school_id.company_id.partner_id.id or \
                                                                    False
        self.mobile_phone = self.school_id.company_id.partner_id.mobile or \
                                                                        False
        self.work_location = self.school_id.company_id.partner_id.city or \
                                                                        False
        self.work_email = self.school_id.company_id.partner_id.email or False
        phone = self.school_id.company_id.partner_id.phone or False
        self.work_phone = phone or False
        self.phone_numbers = phone or False
        phone = self.school_id.company_id.partner_id.phone or False
