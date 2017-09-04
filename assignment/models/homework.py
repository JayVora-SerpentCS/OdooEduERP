# -*- coding: utf-8 -*-
# See LICENSE file for full copyright and licensing details.

from odoo import models, fields, api, _
from odoo.exceptions import ValidationError


class SchoolTeacherAssignment(models.Model):
    _name = 'school.teacher.assignment'
    _description = 'Teacher Assignment Information'

    @api.constrains('assign_date', 'due_date')
    def check_date(self):
        '''Method to check constraint of due date and assign date'''
        if self.due_date < self.assign_date:
            raise ValidationError(_('''Please Configure due date of homework
                                    greater than the assign date!'''))

    name = fields.Char('Assignment Name',
                       help="Name of Assignment")
    subject_id = fields.Many2one('subject.subject', 'Subject', required=True,
                                 help="Select Subject")
    standard_id = fields.Many2one('school.standard', 'Standard',
                                  help="Select Standard")
    teacher_id = fields.Many2one('hr.employee', 'Teacher', required=True,
                                 help="Select Teacher")
    assign_date = fields.Date('Assign Date', required=True,
                              help="Starting date of assignment")
    due_date = fields.Date('Due Date', required=True,
                           help="Ending date of assignment")
    attached_homework = fields.Binary('Attached Home work',
                                      help="Attached Homework")
    state = fields.Selection([('draft', 'Draft'),
                              ('active', 'Active'),
                              ('done', 'Done')],
                             'Status', readonly=True, default='draft')
    student_assign_ids = fields.One2many('school.student.assignment',
                                         'teacher_assignment_id',
                                         string="Student Assignments")

    @api.multi
    def active_assignment(self):
        ''' This method change state as active state
            and create assignment line
            @return : True
        '''
        assignment_obj = self.env['school.student.assignment']
        student_obj = self.env['student.student']
        ir_attachment_obj = self.env['ir.attachment']
        for rec in self:
            students = student_obj.search([('standard_id', '=',
                                            rec.standard_id.id),
                                           ('state', '=', 'done')])
            for std in students:
                ass_dict = {'name': rec.name,
                            'subject_id': rec.subject_id.id,
                            'standard_id': rec.standard_id.id,
                            'assign_date': rec.assign_date,
                            'due_date': rec.due_date,
                            'state': 'active',
                            'attached_homework': rec.attached_homework,
                            'teacher_id': rec.teacher_id.id,
                            'teacher_assignment_id': rec.id,
                            'student_id': std.id,
                            'stud_roll_no': std.roll_no}
                assignment_id = assignment_obj.create(ass_dict)
                if rec.attached_homework:
                    attach = {'name': 'test',
                              'datas': str(rec.attached_homework),
                              'description': 'Assignment attachment',
                              'res_model': 'school.student.assignment',
                              'res_id': assignment_id.id}
                    ir_attachment_obj.create(attach)
            rec.write({'state': 'active'})
        return True

    @api.multi
    def done_assignments(self):
        '''Changes the state to done'''
        self.ensure_one()
        self.state = 'done'
        return True

    @api.multi
    def unlink(self):
        for rec in self:
            if rec.state != 'draft':
                raise ValidationError(_('''You can delete record in
                                        unconfirm state only!'''))
        return super(SchoolTeacherAssignment, self).unlink()


class SchoolStudentAssignment(models.Model):
    _name = 'school.student.assignment'
    _description = 'Student Assignment Information'

    @api.constrains('assign_date', 'due_date')
    def check_date(self):
        if self.due_date < self.assign_date:
            raise ValidationError(_('''Configure due date of homework
                                    greater than Assign date!'''))

    name = fields.Char('Assignment Name',
                       help="Assignment Name")
    subject_id = fields.Many2one('subject.subject', 'Subject', required=True,
                                 help="Select Subject")
    standard_id = fields.Many2one('school.standard', 'Standard', required=True,
                                  help="Select Standard")
    rejection_reason = fields.Text('Reject Reason',
                                   help="Reject Reason")
    teacher_id = fields.Many2one('hr.employee', 'Teacher', required=True,
                                 help='''Teacher responsible to assign
                                 assignment''')
    assign_date = fields.Date('Assign Date', required=True,
                              help="Starting date of assignment")
    due_date = fields.Date('Due Date', required=True,
                           help="End date of assignment")
    state = fields.Selection([('draft', 'Draft'), ('active', 'Active'),
                              ('reject', 'Reject'),
                              ('done', 'Done')], 'Status',
                             help="States of assignment",
                             readonly=True, default='draft')
    student_id = fields.Many2one('student.student', 'Student', required=True,
                                 help="Name of Student")
    stud_roll_no = fields.Integer(string="Roll no",
                                  help="Roll No of student")
    attached_homework = fields.Binary('Attached Home work',
                                      help="Homework Attached by student")
    teacher_assignment_id = fields.Many2one('school.teacher.assignment',
                                            string="Teachers")
    stud_std = fields.Many2one('standard.standard', 'Student Standard')

    @api.onchange('student_id')
    def onchange_stud_std(self):
        for rec in self:
            rec.stud_std = rec.student_id.standard_id.standard_id.id

    @api.multi
    def active_assignment(self):
        '''This method change state as active'''
        self.ensure_one()
        self.state = 'active'

    @api.multi
    def done_assignment(self):
        ''' This method change state as done
            for school student assignment
            @return : True
        '''
        self.ensure_one()
        self.state = 'done'
        return True

    @api.multi
    def reassign_assignment(self):
        '''This method change state as active'''
        self.ensure_one()
        self.state = 'active'
        return True

    @api.multi
    def unlink(self):
        for rec in self:
            if rec.state != 'draft':
                raise ValidationError(_('''You can delete record
                                        in inactive state only!'''))
        return super(SchoolStudentAssignment, self).unlink()
