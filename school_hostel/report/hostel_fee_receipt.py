# -*- encoding: UTF-8 -*-
##############################################################################
#
#    OpenERP, Open Source Management Solution
#    Copyright (C) 2012-Today Serpent Consulting Services PVT. LTD.
#    (<http://www.serpentcs.com>)
#
#    This program is free software: you can redistribute it and/or modify
#    it under the terms of the GNU General Public License as published by
#    the Free Software Foundation, either version 3 of the License, or
#    (at your option) any later version.
#
#    This program is distributed in the hope that it will be useful,
#    but WITHOUT ANY WARRANTY; without even the implied warranty of
#    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#    GNU General Public License for more details.
#
#    You should have received a copy of the GNU General Public License
#    along with this program.  If not, see <http://www.gnu.org/licenses/>
#
##############################################################################
#
from openerp.report import report_sxw
from openerp import models


class hostel_fee_receipt(report_sxw.rml_parse):

    def __init__(self, cr, uid, name, context):
        super(hostel_fee_receipt, self).__init__(cr, uid, name,
                                                 context=context)


class report_add_exam_result(models.AbstractModel):

    _name = 'report.school_hostel.hostel_fee_reciept'
    _inherit = 'report.abstract_report'
    _template = 'school_hostel.hostel_fee_reciept'
    _wrapped_report_class = hostel_fee_receipt
