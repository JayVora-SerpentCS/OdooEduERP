# See LICENSE file for full copyright and licensing details.

import time
from odoo import models, api
import datetime

class ReportAddExamResult(models.AbstractModel):
    _name = 'report.exam.exam_result_report'
    _description = "Exam result Report"

    @api.model
    def _get_result_detail(self, subject_ids):
        sub_list = []
        result_data = []
        no =0
        total = 0.0
        obtained_total = 0.0
        per = 0.0
        for sub in subject_ids:
            sub_list.append(sub.id)
        sub_obj = self.env['exam.subject']
        subject_exam_ids = sub_obj.search([('id', 'in', sub_list)])
        for subject in subject_exam_ids:
            no = no+1
            obtained_total = subject.obtain_marks 
            total = subject.maximum_marks
            per = (obtained_total / total) * 100
            
            result_data.append({'no': no or '',
                                'subject': subject.subject_id.name or '',
                                'max_mark': subject.maximum_marks or '',
                                'mini_marks': subject.minimum_marks or '',
                                'obt_marks': subject.obtain_marks or '',
                                'subject_percentage': per or ''})
        return result_data

    @api.model
    def _get_current_date(self):
        return datetime.date.today()

    @api.model
    def _get_student_attendance(self):
        active_model = self._context.get('active_model')
        result_data = self.env[active_model].browse(self._context.get('active_id'))
        student_id = result_data.student_id.id
        standard_id = result_data.standard_id.id
        
        student_att_ids = self.env['daily.attendance'].search([('standard_id','=',standard_id)]).ids
        student_att_lines = self.env['daily.attendance.line'].search([('stud_id','=', student_id),('standard_id','in',student_att_ids)])

        if student_att_lines:
            total_taken = 0;
            total_attended = 0;
            
            for student_att_line in student_att_lines:
                total_taken += 1
                if student_att_line.is_present:
                    total_attended += 1
            return str((total_attended/total_taken)*100) + "%"
            
        else:
            return "__"
    
    @api.model
    def _get_report_values(self, docids, data=None):
        active_model = self._context.get('active_model')
        report_result = self.env['ir.actions.report']._get_report_from_name(
            'exam.exam_result_report')
        result_data = self.env[active_model
                               ].browse(self._context.get('active_id'))
        
        return {'doc_ids': docids,
                'data': data,
                'doc_model': report_result.model,
                'docs': result_data,
                'get_result_detail': self._get_result_detail,
                'get_current_date': self._get_current_date,
                'get_student_attendance': self._get_student_attendance,
                'time': time,
                }
