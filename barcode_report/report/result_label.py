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
from openerp.report import report_sxw
from openerp import models


class result_label(report_sxw.rml_parse):

    def __init__(self, cr, uid, name, context=None):
        super(result_label, self).__init__(cr, uid, name, context=context)
        self.localcontext.update({'get_student_info': self.get_student_info,
                                })

    def get_student_info(self, standard_id, division_id, medium_id, year_id):
        student_obj = self.pool.get('student.student')
        student_ids = student_obj.search(self.cr, self.uid,
                                         [('standard_id', '=', standard_id),
                                          ('division_id', '=', division_id),
                                          ('medium_id', '=', medium_id),
                                          ('year', '=', year_id)])
        result = []
        for student in student_obj.browse(self.cr, self.uid, student_ids):
            result.append(student.pid)
        return result


class report_label(models.AbstractModel):
    _name = 'report.barcode_report.result_label'
    _inherit = 'report.abstract_report'
    _template = 'barcode_report.result_label'
    _wrapped_report_class = result_label

# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4:
