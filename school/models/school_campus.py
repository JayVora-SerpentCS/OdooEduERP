# -*- coding: utf-8 -*-
# Part of Odoo. See LICENSE file for full copyright and licensing details.

from openerp import models, fields, api, _
from openerp.exceptions import Warning as UserError


class CampusManager(models.Model):
    ''' Defining a Teacher information '''
    _name = 'campus.manager'
    _description = 'Campus manager Information'

    employee_id = fields.Many2one('hr.employee', 'Employee ID',
                                  ondelete="cascade", copy=False,
                                  delegate=True, select=True, required=True)
    campus_id = fields.Many2one('school.school', "Campus", copy=False,
                                help="Campus for which he/she responsible.")
    is_parent = fields.Boolean('Is Parent')
    stu_parent_id = fields.Many2one('school.parent', 'Parent ref')
    student_id = fields.Many2many('student.student',
                                  'students_campus_parent_rel',
                                  'students_campus_parent_id', 'student_id',
                                  'Children')

    @api.model
    def create(self, vals):
        c_manager_id = super(CampusManager, self).create(vals)
        if c_manager_id.campus_id:
            cm_ids = self.search([('campus_id', '=',
                                   c_manager_id.campus_id.id),
                                  ('id', '!=', c_manager_id.id)])
            if cm_ids:
                raise UserError(_(str(c_manager_id.campus_id.name) +
                                  ' Campus is already assigned to user ' +
                                  str(c_manager_id.name)))
            c_manager_id.campus_id.write(
                             {'campus_manager_id': c_manager_id.id,
                              'campus_manager_write': True})
        user_vals = {'name': c_manager_id.name,
                     'login': c_manager_id.work_email,
                     'email': c_manager_id.work_email,
                     'campus_manager_create': c_manager_id}
        user_id = self.env['res.users'].create(user_vals)
        c_manager_id.employee_id.write({'user_id': user_id.id})
        if vals.get('is_parent'):
            self.parent_crt(c_manager_id)
        return c_manager_id

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
        if vals.get('campus_id'):
            self.campus_id.write(
                              {'campus_manager_id': False,
                               'campus_manager_write': True})
            vals_id = self.campus_id.search([('id', '=',
                                              vals.get('campus_id'))])
            vals_id.write({'campus_manager_id': self.id,
                           'campus_manager_write': True})
        return super(CampusManager, self).write(vals)

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
        if vals.get('campus_manager_create'):
            ir_obj = self.pool.get('ir.model.data')
            grps = c_grp = ir_obj.get_object(self._cr, self._uid,
                                             'school',
                                             'group_university_campus_manager')
            if user_rec.groups_id:
                grps = user_rec.groups_id
                grps += c_grp
            group_ids = [group.id for group in grps]
            user_rec.write({'groups_id': [(6, 0, group_ids)]})
        return user_rec
