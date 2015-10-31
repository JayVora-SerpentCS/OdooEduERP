# -*- coding: utf-8 -*-
# Part of Odoo. See LICENSE file for full copyright and licensing details.

import time
import qrcode
import base64
import tempfile
from openerp.report import report_sxw
from openerp.osv import osv


class qr_code_label(report_sxw.rml_parse):

    def __init__(self, cr, uid, name, context):
        super(qr_code_label, self).__init__(cr, uid, name, context=context)
        self.localcontext.update({
            'time': time,
            'get_qr_code': self.get_qr_code,
        })

    def get_qr_code(self, number):
        qr_img = qrcode.make(number)
        filename = str(tempfile.gettempdir()) + '/Book_QRCode.png'
        qr_img.save(filename)
        return base64.encodestring(file(filename, 'rb').read())


class report_qrcode_lable(osv.AbstractModel):

    _name = 'report.library.qrcode_label'
    _inherit = 'report.abstract_report'
    _template = 'library.qrcode_label'
    _wrapped_report_class = qr_code_label
