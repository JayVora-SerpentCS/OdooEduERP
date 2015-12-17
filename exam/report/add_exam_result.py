# -*- coding: utf-8 -*-
##############################################################################
#
#    OpenERP, Open Source Management Solution
#    Copyright (C) 2004-2009 Tiny SPRL (<http://tiny.be>).
#    Copyright (C) 2011-Today Serpent Consulting Services PVT. LTD.
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
from openerp.osv import orm


class AddExamResult(report_sxw.rml_parse):
    def __init__(self, cr, uid, name, context=None):
        super(add_exam_result, self).__init__(cr, uid, name, context=context)
        self.localcontext.update({
            'time': time,
            'get_result_detail': self._get_result_detail,
        })

    def _get_result_detail(self, subject_ids, result):
        sub_list = []
        for sub in subject_ids:
            sub_list.append(sub.id)
        sub_obj = self.pool.get('exam.subject')
        subject_exam_ids = sub_obj.search(self.cr, self.uid,
                                          [('id', 'in', sub_list),
                                           ('exam_id', '=', result.id)])
        result_data = []
        for subject in sub_obj.browse(self.cr, self.uid, subject_exam_ids):
                result_data.append({'subject': (subject.subject_id and
                                                subject.subject_id.name),
                                    'max_mark': subject.maximum_marks or '',
                                    'mini_marks': subject.minimum_marks or '',
                                    'obt_marks': subject.obtain_marks or '',
                                    })
        return result_data


class ReportAddExamResult(orm.AbstractModel):
    _name = 'report.exam.exam_result_report'
    _inherit = 'report.abstract_report'
    _template = 'exam.exam_result_report'
    _wrapped_report_class = AddExamResult
