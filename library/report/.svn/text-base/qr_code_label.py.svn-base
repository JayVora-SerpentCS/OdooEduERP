# -*- coding: utf-8 -*-
##############################################################################
#
#    OpenERP, Open Source Management Solution
#    Copyright (C) 2004-2010 Tiny SPRL (<http://tiny.be>).
#
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
from report import report_sxw
import qrcode
import base64
import tempfile

class qr_code_label(report_sxw.rml_parse):

    def __init__(self, cr, uid, name, context):
        super(qr_code_label, self).__init__(cr, uid, name, context=context)
        self.localcontext.update({
            'time': time,
            'get_qr_code':self.get_qr_code,
        })
    
    def get_qr_code(self,number):
        qr_img = qrcode.make(number)
        filename = str(tempfile.gettempdir()) + '/Book_QRCode.png'
        qr_img.save(filename)
        return base64.encodestring(file(filename, 'rb').read())
        

report_sxw.report_sxw('report.qr_code_label', 'product.product',
        'library/report/qrcode_label.rml',parser=qr_code_label, header=False)


# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4:
