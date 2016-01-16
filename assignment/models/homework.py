# -*- coding: utf-8 -*-
# Part of Odoo. See LICENSE file for full copyright and licensing details.

from openerp import models, fields, api


class SchoolTeacherAssignment(models.Model):
    _name = 'school.teacher.assignment'
    _description = 'Teacher Assignment Information'

    name = fields.Char('Assignment Name')
    subject_id = fields.Many2one('subject.subject', 'Subject', required=True)
    standard_id = fields.Many2one('school.standard', 'Standard')
    teacher_id = fields.Many2one('hr.employee', 'Teacher', required=True)
    assign_date = fields.Date('Assign Date', required=True)
    due_date = fields.Date('Due Date', required=True)
    attached_homework = fields.Binary('Attached Home work')
    state = fields.Selection([('draft', 'Draft'), ('active', 'Active')],
                             'Status', readonly=True, default='draft')
    school_id = fields.Many2one('school.school', 'School Name',
                                related='standard_id.school_id')
    cmp_id = fields.Many2one('res.company', 'Company Name',
                             related='school_id.company_id')

#    @api.model
#    def default_get(self, fields_list):
#        res = super(SchoolTeacherAssignment, self).default_get(fields_list)
#        res.update({'state': 'draft'})
#        return res

    @api.multi
    def active_assignment(self):
        ''' This method change state as active state
            and create assignment line
        @return : True
        '''
        assignment_obj = self.env['school.student.assignment']
        att_obj = self.env['ir.attachment']
#        std_ids = []
        for rec in self:
            self._cr.execute('''select id from student_student\
                                where standard_id=%s
                                and state!='draft'
                                '''
                                % (rec.standard_id.id))
            student = self._cr.fetchall()
#            if student:
#                for stu in student:
#                    std_ids.append(stu[0])
            if student:
                for std in student:
                    assign_dict = {'name': rec.name,
                                'subject_id': rec.subject_id.id,
                                'standard_id': rec.standard_id.id,
                                'assign_date': rec.assign_date,
                                'due_date': rec.due_date,
                                'state': 'active',
                                'attached_homework': rec.attached_homework,
                                'teacher_id': rec.teacher_id.id,
                                'student_id': std[0]}
                    assignment_id = assignment_obj.create(assign_dict)
                    if rec.attached_homework:
                        att_obj.create({
                            'name': rec.name,
                            'datas': str(rec.attached_homework),
                            'description': 'Assignment attachment',
                            'res_model': 'school.student.assignment',
                            'res_id': assignment_id.id
                        })
        self.write({'state': 'active'})
        return True


class SchoolStudentAssignment(models.Model):
    _name = 'school.student.assignment'
    _description = 'Student Assignment Information'

    name = fields.Char('Assignment Name')
    subject_id = fields.Many2one('subject.subject', 'Subject', required=True)
    standard_id = fields.Many2one('school.standard', 'Standard', required=True)
    teacher_id = fields.Many2one('hr.employee', 'Teacher', required=True)
    assign_date = fields.Date('Assign Date', required=True)
    due_date = fields.Date('Due Date', required=True)
    state = fields.Selection([('draft', 'Draft'), ('active', 'Active'),
                              ('done', 'Done')], 'Status',
                             default='draft', readonly=True)
    student_id = fields.Many2one('student.student', 'Student', required=True)
    attached_homework = fields.Binary('Attached Home work')

    @api.multi
    def done_assignment(self):
        ''' This method change state as done
            for school student assignment
        @return : True
        '''
        return self.write({'state': 'done'})
