# See LICENSE file for full copyright and licensing details.

from odoo import models, fields, api, tools, _
from docutils.parsers.rst.directives import percentage
from _ast import For
import datetime




class StudentPromotion(models.Model):
    ''' Defining a student information '''
    _name = 'student.promotion'
    _table = "student_promotion"
    _description = 'Student Promotion Information'
    
    
    academic_year_from = fields.Many2one('academic.year', 'Academic Year From',required=True,
                                    help="Select Academic Year")

    academic_year_to = fields.Many2one('academic.year', 'Academic Year To',required=True,
                                    help="Select Academic Year")
    standard_id_from = fields.Many2one('school.standard', 'Class From',required=True,)
    standard_id_to = fields.Many2one('school.standard', 'Class To',required=True)
    promotion_lines = fields.One2many('student.promotion.line','promotion_id','Promotion Lines')
    
    state = fields.Selection([('draft',"Draft"), ('loaded',"Students Loaded"), ('promoted',"Promoted")], "State", default='draft')
    
    @api.multi
    def load_students(self):
        '''Method to confirm promotion'''
        for rec in self:
            lines = []
            student_academics = self.env['student.academic'].search([('academic_year_id','=',rec.academic_year_from.id),('standard_id','=',rec.standard_id_from.id), ('state', '=', 'active')])
            for student_academic in student_academics:
                student = student_academic.student_id
                #fees_structure = student.fees_structure.id
                #fees_structure_new = student.fees_structure.id
                product_list_id = student.product_list_id.id
                if rec.product_list_id:
                    product_list_id_new = rec.product_list_id.id
                else:
                    product_list_id_new = student.product_list_id.id
                    
                student_id = student.id
                
                result_obj= self.env['exam.result'].search([('student_id','=',student_id),('standard_id','=',rec.standard_id_from.id)])
                total_marks = 0
                percentage = 0
                stud_result = 'pending'
                if result_obj:
                    total_marks= result_obj.total
                    percentage= result_obj.percentage
                    stud_result = result_obj.result
                                        
                    if stud_result =="Pass":
                        stud_result = "ready_to_promote"
                    elif stud_result =="Fail":
                        stud_result == "fail"
                    else:
                        stud_result == "pending"         
                line_vals = {'name': student_id,
                             'obtain_marks': total_marks,
                             'percentage': percentage,
                             'state': stud_result,
                             #'fees_structure': fees_structure,
                             #'fees_structure_new': fees_structure,
                             'product_list_id': product_list_id,
                             'product_list_id_new': product_list_id_new
                             }
                lines.append((0, 0, line_vals))
            
            rec.write({'promotion_lines': lines})
            rec.state = "loaded"
            
    
    @api.multi
    def promote_students(self):
        '''Method to confirm promotion'''
    
        for rec in self:
            promote_flag = False
            student_ids = []
            
            promotion_ids   = rec.promotion_lines
            for promotion_id in promotion_ids:
                
                student_academic_exist = self.env['student.academic'].search([('student_id','=',promotion_id.name.id),
                                                                              ('academic_year_id','=',rec.academic_year_from.id),
                                                                              ('standard_id','=',rec.standard_id_from.id), ('state', '=', 'active')])
                if promotion_id.state == 'ready_to_promote' and student_academic_exist:
                    promote_flag = True
                    # retriving student exam information
                    student_exam_detail = self.env['exam.result'].search([('student_id','=',promotion_id.name.id)])
                    student_percentage  = student_exam_detail.percentage
                    student_result  = student_exam_detail.result
                    
                    # update student state information
                    student_active = self.env['student.academic'].search([('student_id','=',promotion_id.name.id),('state','=','active')])
                    for std_active in student_active:
                        std_active.write({'state': 'complete'})
                         
                    # insert current student academics information
                    parent_vals = {'student_id': promotion_id.name.id,
                                   'academic_year_id': rec.academic_year_to.id,
                                   'standard_id': rec.standard_id_to.id,
                                   'state': 'active'}
                    self.env['student.academic'].create(parent_vals)
                    
                  
                    # insert student history information
                    history_vals = {'student_id': promotion_id.name.id,
                                   'academic_year_id': rec.academic_year_from.id,
                                   'standard_id': rec.standard_id_from.id,
                                   'percentage': student_percentage,
                                   'result':student_result
                    }
                    self.env['student.history'].create(history_vals)
                    
                    student_ids.append((4, promotion_id.name.id))

                    # update student new class information
                    student_next_class = self.env['student.student'].search([('id','=',promotion_id.name.id)])
                    if student_next_class:
                        student_next_class.write({'year': rec.academic_year_to.id,'standard_id':rec.standard_id_to.id,'product_list_id':rec.product_list_id.id})
                
            if promote_flag:
                
                # Charge Fee to student
                company_id = self.env['res.users'].browse(self._uid).company_id.id
                register_vals = {'name':'Promotion: ' + str(rec.standard_id_from.name) + "-to-" + str(rec.standard_id_to.name), 
                                 'date': datetime.date.today(),
                                 'state': 'draft',
                                 'journal_id': rec.journal_id.id,
                                 'company_id': company_id,
                                 'fees_structure': rec.fees_structure.id,
                                 'standard_id': rec.standard_id_to.id,
                                 'student_ids': student_ids 
                                 }

                fee_register = self.env['student.fees.register'].create(register_vals)
                fee_register.fees_register_confirm()

                rec.state = "promoted"
        
                    
                
class StudentPromotionLine(models.Model):
    _name = "student.promotion.line"
    _table = "student_promotion_line"
    _description = "Student Promotion Line"
    
    name = fields.Many2one('student.student', 'Student Name', required=True)
    promotion_id = fields.Many2one('student.promotion', 'Name')
    obtain_marks = fields.Float(string="Marks")
    percentage = fields.Text(string="Percentage")
    state = fields.Selection([('draft', 'Draft'), ('pending', 'Pending'), ('ready_to_promote', 'Ready to Promote'), ('fail', 'Fail')],
                            required=True, default='draft')
    
