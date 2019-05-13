# See LICENSE file for full copyright and licensing details.

from odoo import models, fields, api, tools, _
from docutils.parsers.rst.directives import percentage




class StudentPromotion(models.Model):
    ''' Defining a student information '''
    _name = 'student.promotion'
    _table = "student_promotion"
    _description = 'Student Promotion Information'
    
    
    academic_year_from = fields.Many2one('academic.year', 'Academic Year From',
                                    help="Select Academic Year")

    academic_year_to = fields.Many2one('academic.year', 'Academic Year To',
                                    help="Select Academic Year")
    standard_id_from = fields.Many2one('school.standard', 'Class From')
    standard_id_to = fields.Many2one('school.standard', 'Class To')
    promotion_lines = fields.One2many('student.promotion.line','promotion_id','Promotion Lines')
    
    
    @api.multi
    def upload_students(self):
        '''Method to confirm promotion'''
        for rec in self:
                      
            lines = []
            students = self.env['student.student'].search([('year','=',rec.academic_year_from.id),('standard_id','=',rec.standard_id_from.id)])
            print("students: ", students)
            for student in students:
                
                fees_structure = student.fees_structure.id
                fees_structure_new = student.fees_structure.id
                print(fees_structure,"fee stucture")
                student_id = student.id
                
                result_obj= self.env['exam.result'].search([('student_id','=',student_id),('standard_id','=',rec.standard_id_from.id)])
                total_marks = 0
                percentage = 0
                if result_obj:
                    total_marks= result_obj.total
                    percentage= result_obj.percentage
                    #state = result_obj.state
                
                line_vals = {'name': student_id,
                             'obtain_marks': total_marks,
                             'percentage': percentage,
                             'status': 'pending',
                             'fees_structure': fees_structure,
                             'fees_structure_new': fees_structure
                             }
                lines.append((0, 0, line_vals))
            
            rec.write({'promotion_lines': lines})
            
            
class StudentPromotionLine(models.Model):
    _name = "student.promotion.line"
    _table = "student_promotion_line"
    _description = "Student Promotion Line"
    
    name = fields.Many2one('student.student', 'Student Name')
    promotion_id = fields.Many2one('student.promotion', 'Name')
    obtain_marks = fields.Float(string="Marks")
    percentage = fields.Text(string="Percentage")
    status = fields.Selection([('pending', 'Pending'), ('done', 'Done')],
                            required=True, default='done')
    
