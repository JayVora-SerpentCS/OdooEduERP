# -*- coding: utf-8 -*-
# See LICENSE file for full copyright and licensing details.

import time
import qrcode
import base64
import tempfile
from odoo import models, api


class ReportQrcodeLable(models.AbstractModel):

    _name = 'report.library.qrcode_label'

    @api.multi
    def get_qr_code(self, number):
        qr_img = qrcode.make(number)
        filename = str(tempfile.gettempdir()) + '/Book_QRCode.png'
        qr_img.save(filename)
        return base64.encodestring(file(filename, 'rb').read())

    @api.model
    def render_html(self, docids, data=None):
        self.model = self.env.context.get('active_model')

        docs = self.env[self.model].browse(self.env.context.get('active_ids',
                                                                []))
        number = data['form'].get('number')[0]
        get_student = self.with_context(data['form'].get('used_context', {}))
        get_qr_code = get_student.get_qr_code(number)
        docargs = {
            'doc_ids': docids,
            'doc_model': self.model,
            'data': data['form'],
            'docs': docs,
            'time': time,
            'get_qr_code': get_qr_code,
        }
        render_model = 'library.qrcode_label'
        return self.env['report'].render(render_model, docargs)
