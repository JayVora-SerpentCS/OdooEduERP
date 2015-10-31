# -*- coding: utf-8 -*-
# Part of Odoo. See LICENSE file for full copyright and licensing details.
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
