# -*- coding: utf-8 -*-
# Part of Odoo. See LICENSE file for full copyright and licensing details.

from openerp import models, fields, api


class FeesManager(models.Model):
    ''' Defining a Teacher information '''
    _name = 'fees.manager'
    _description = 'Campus manager Information'

    employee_id = fields.Many2one('hr.employee', 'Employee ID',
                                  ondelete="cascade", copy=False,
                                  delegate=True, select=True, required=True)
    campus_id = fields.Many2many('school.school',
                                 'school_fees_rel',
                                 'school_feesmng_id', 'campus_id',
                                 'Campus',
                                 help="Campus for which he/she responsible.")
    is_parent = fields.Boolean('Is Parent')
    stu_parent_id = fields.Many2one('school.parent', 'Parent ref')
    student_id = fields.Many2many('student.student',
                                  'students_fees_parent_rel',
                                  'students_fees_parent_id', 'student_id',
                                  'Children')

    @api.model
    def create(self, vals):
        f_manager_id = super(FeesManager, self).create(vals)
        user_vals = {'name': f_manager_id.name,
                     'login': f_manager_id.work_email,
                     'email': f_manager_id.work_email,
                     'fees_manager_create': f_manager_id}
        user_id = self.env['res.users'].create(user_vals)
        f_manager_id.employee_id.write({'user_id': user_id.id})
        if vals.get('is_parent'):
            self.parent_crt(f_manager_id)
        return f_manager_id

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
        return super(FeesManager, self).write(vals)

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


class ResUsers(models.Model):

    _inherit = "res.users"

    @api.model
    def create(self, vals):
        user_rec = super(ResUsers, self).create(vals)
        if vals.get('fees_manager_create'):
            ir_obj = self.pool.get('ir.model.data')
            groups = fees_grp_id = ir_obj.get_object(self._cr, self._uid,
                                                     'school',
                                                     'group_fees_manager')
            if user_rec.groups_id:
                groups = user_rec.groups_id
                groups += fees_grp_id
            group_ids = [group.id for group in groups]
            user_rec.write({'groups_id': [(6, 0, group_ids)]})
        return user_rec
