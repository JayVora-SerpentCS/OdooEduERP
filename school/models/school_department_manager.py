# -*- coding: utf-8 -*-
# Part of Odoo. See LICENSE file for full copyright and licensing details.

from openerp import models, fields, api, _
from openerp.exceptions import Warning as UserError


class DepartmentManager(models.Model):
    ''' Defining a Teacher information '''
    _name = 'department.manager'
    _description = 'Department Manager Information'

    employee_id = fields.Many2one('hr.employee', 'Employee ID',
                                  ondelete="cascade", copy=False,
                                  delegate=True, select=True, required=True)
    d_id = fields.Many2one('standard.standard', "Department", copy=False,
                           help="Department for which he/she responsible.")
    is_parent = fields.Boolean('Is Parent')
    stu_parent_id = fields.Many2one('school.parent', 'Parent ref')
    student_id = fields.Many2many('student.student',
                                  'students_department_parent_rel',
                                  'students_dep_parent_id', 'student_id',
                                  'Children')

    @api.model
    def create(self, vals):
        d_manager_id = super(DepartmentManager, self).create(vals)
        if d_manager_id.d_id:
            fm_ids = self.search([('department_id', '=',
                                   d_manager_id.d_id.id),
                                  ('id', '!=', d_manager_id.id)])
            if fm_ids:
                raise UserError(_(str(d_manager_id.d_id.name) +
                                  ' Department is already assigned to user ' +
                                  str(d_manager_id.name)))
            d_manager_id.d_id.write(
                             {'d_manager_id': d_manager_id.id,
                              'department_manager_write': True})
        user_vals = {'name': d_manager_id.name,
                     'login': d_manager_id.work_email,
                     'email': d_manager_id.work_email,
                     'department_manager_create': d_manager_id}
        user_id = self.env['res.users'].create(user_vals)
        d_manager_id.employee_id.write({'user_id': user_id.id})
        if vals.get('is_parent'):
            self.parent_crt(d_manager_id)
        return d_manager_id

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
        if vals.get('department_id'):
            self.d_id.write({'department_manager_id': False,
                             'department_manager_write': True})
            vals_id = self.d_id.search([('id', '=',
                                         vals.get('d_id'))])
            vals_id.write({'d_manager_id': self.id,
                           'department_manager_write': True})
        return super(DepartmentManager, self).write(vals)

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
        if vals.get('department_manager_create'):
            department_grp_id = self.pool.get(
                                       'ir.model.data').get_object(
                                                    self._cr,
                                                    self._uid,
                                                    'school',
                                                    'group_department_manager')
            groups = department_grp_id
            if user_rec.groups_id:
                groups = user_rec.groups_id
                groups += department_grp_id
            group_ids = [group.id for group in groups]
            user_rec.write({'groups_id': [(6, 0, group_ids)]})
        return user_rec
