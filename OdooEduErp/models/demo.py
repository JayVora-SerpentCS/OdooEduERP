# -*- coding: utf-8 -*-
# See LICENSE file for full copyright and licensing details.

from odoo import models, fields


class DemoInstall(models.Model):

    _name = "demo.install"

    name = fields.Char('Name')
