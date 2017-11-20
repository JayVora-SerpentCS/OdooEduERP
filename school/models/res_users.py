# -*- coding: utf-8 -*-
# See LICENSE file for full copyright and licensing details.

from odoo import models, api


class ResUsers(models.Model):

    _inherit = "res.users"

    @api.model
    def create(self, vals):
        '''Inherit Method to create user of group teacher or parent'''
        vals.update({'employee_ids': False})
        user_rec = super(ResUsers, self).create(vals)
        school = self.env['school.school'].browse(vals.get('school_id'))
        if vals.get('parent_create'):
            parent_grp_id = self.env.ref('school.group_school_parent')
            emp_grp = self.env.ref('base.group_user')
            parent_group_ids = [emp_grp.id, parent_grp_id.id]
            user_rec.write({'groups_id': [(6, 0, parent_group_ids)]})
        if vals.get('teacher_create'):
            teacher_grp_id = self.env.ref('school.group_school_teacher')
            user_base_grp = self.env.ref('base.group_user')
            contact_create = self.env.ref('base.group_partner_manager')
            teacher_group_ids = [user_base_grp.id, teacher_grp_id.id,
                                 contact_create.id]
            user_rec.write({'groups_id': [(6, 0, teacher_group_ids)],
                            'company_id': school.company_id.id,
                            'company_ids': [(4, school.company_id.id)]})
        return user_rec
