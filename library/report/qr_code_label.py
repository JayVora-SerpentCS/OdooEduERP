# -*- encoding: utf-8 -*-
##############################################################################
#
#    OpenERP, Open Source Management Solution
#    Copyright (C) 2004-2009 Tiny SPRL (<http://tiny.be>).
#    Copyright (C) 2011-2012 Serpent Consulting Services
#    (<http://www.serpentcs.com>)
#    Copyright (C) 2013-2014 Serpent Consulting Services
#    (<http://www.serpentcs.com>)
#    This program is free software: you can redistribute it and/or modify
#    it under the terms of the GNU Affero General Public License as
#    published by the Free Software Foundation, either version 3 of the
#    License, or (at your option) any later version.
#
#    This program is distributed in the hope that it will be useful,
#    but WITHOUT ANY WARRANTY; without even the implied warranty of
#    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#    GNU Affero General Public License for more details.
#
#    You should have received a copy of the GNU Affero General Public License
#    along with this program.  If not, see <http://www.gnu.org/licenses/>.
#
##############################################################################
import time
from openerp.report import report_sxw
import qrcode
import base64
import tempfile
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

# report_sxw.report_sxw('report.qr.code.label', 'product.product',
#         'library/report/qrcode_label.rml',parser=qr_code_label, header=False)

# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4:
