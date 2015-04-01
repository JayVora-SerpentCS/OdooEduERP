# -*- encoding: utf-8 -*-
##############################################################################
#
#    OpenERP, Open Source Management Solution
#    Copyright (C) 2004-2009 Tiny SPRL (<http://tiny.be>).
#    Copyright (C) 2011-2012 Serpent Consulting Services (<http://www.serpentcs.com>)
#    Copyright (C) 2013-2014 Serpent Consulting Services (<http://www.serpentcs.com>)
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
from openerp.osv import osv
from openerp import models, fields, api, _

class exam_create_result(models.TransientModel):

    _name = 'exam.create.result'

    @api.multi
    def generate_result(self):
        if not self._context.get('active_ids'):
            return {}
        exam_obj = self.env['exam.exam']
        student_obj = self.env['student.student']
        result_obj = self.env['exam.result']
        result_subject_obj = self.env['exam.subject']
        for result in self.browse(self.ids):
            for exam in exam_obj.browse(self._context.get('active_ids')):
                for timetable in exam.standard_id:
                    student_ids = student_obj.search([('standard_id', '=', timetable.standard_id.id), ('division_id', '=', timetable.division_id.id), ('medium_id', '=', timetable.medium_id.id)])
                    for student in student_ids:
                        result_exists = result_obj.search(cr, uid, [('standard_id', '=', timetable.standard.id), ('division_id', '=', timetable.division_id.id), ('medium_id', '=', timetable.medium_id.id), ('student_id','=', student.id)])
                        if not result_exists:
                            result_id = result_obj.create({'s_exam_ids': exam.id,
                                                                    'student_id': student.id,
                                                                    'standard_id': timetable.class_id.id,
                                                                    'division_id': timetable.division_id.id,
                                                                    'medium_id': timetable.medium_id.id})
                            for line in timetable.timetable_ids:
                                result_subject_obj.create({'exam_id': result_id.id,
                                                                    'subject_id': line.subject_id and line.subject_id.id or False,
                                                                    'minimum_marks': line.subject_id and line.subject_id.minimum_marks or 0.0,
                                                                    'maximum_marks': line.subject_id and line.subject_id.maximum_marks or 0.0})
        return {}

# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4: