# See LICENSE file for full copyright and licensing details.

from odoo import api, models


class ResUsers(models.Model):
    _inherit = "res.users"

    @api.model_create_multi
    def create(self, vals):
        """Inherit Method to create user of group teacher or parent."""
        for val in vals:
            val.update({"employee_ids": False})
        res = super().create(vals)
        if self._context.get("teacher_create", False):
            teacher_group_ids = [
                self.env.ref("school.group_school_teacher").id,
                self.env.ref("base.group_user").id,
                self.env.ref("base.group_partner_manager").id,
            ]
            res.write(
                {
                    "groups_id": [(6, 0, teacher_group_ids)],
                    "company_id": self._context.get("school_id"),
                    "company_ids": [(4, self._context.get("school_id"))],
                }
            )
        return res
