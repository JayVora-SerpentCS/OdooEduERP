# -*- coding: utf-8 -*-
# Part of Odoo. See LICENSE file for full copyright and licensing details.

from openerp import models, api
import openerp
import logging
from openerp import SUPERUSER_ID

_logger = logging.getLogger(__name__)


class ResUsers(models.Model):

    _inherit = 'res.users'

    def _login(self, db, login, password):
        if not password:
            return False
        user_id = False
        try:
            with self.pool.cursor() as cr:
                res = self.search(cr, SUPERUSER_ID, [('login', '=', login)])
                if res:
                    user_id = res[0]
                    stu_obj = self.pool.get('student.student')
                    stu_id = stu_obj.search(cr, SUPERUSER_ID,
                                            [('user_id', '=', user_id),
                                             ('state', 'in', ('terminate',
                                                              'alumni',
                                                              'withdraw')
                                              )])
                    if stu_id:
                        raise openerp.exceptions.AccessDenied()
                    self.check_credentials(cr, user_id, password)
                    self._update_last_login(cr, user_id)
        except openerp.exceptions.AccessDenied:
            _logger.info("Login failed for db:%s login:%s", db, login)
            user_id = False
        return user_id

    @api.model
    def create(self, vals):
        if vals.get('email', False):
            vals['login'] = vals['login']
            vals['email'] = vals['email']
        user_rec = super(ResUsers, self).create(vals)
        if not vals.get('website_user'):
            ir_obj = self.env['ir.model.data']
            admisn_grp = ir_obj.get_object('school',
                                           'group_school_student_inadmission')
            home_action_id = ir_obj.get_object('school',
                                               'school_dashboard_act')
            user_obj = self.env['res.users']
            grps = [group.id
                    for group in user_obj.browse(self.user_id.id).groups_id]
            if admisn_grp.id not in grps:
                user_rec.write({'action_id': home_action_id.id})
        return user_rec

    def _get_group(self, cr, uid, context=None):
        dataobj = self.pool.get('ir.model.data')
        result = []
        try:
            dummy, group_id = dataobj.get_object_reference(cr, SUPERUSER_ID,
                                                           'base',
                                                           'group_user')
            result.append(group_id)
        except ValueError:
            # If these groups does not exists anymore
            pass
        return result

    _defaults = {
        'groups_id': _get_group,
    }
