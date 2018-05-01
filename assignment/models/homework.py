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
            raise ValidationError(_('Due date of homework should \
                                    be greater than assign date'))

    name = fields.Char('Assignment Name',
                       help="Name of Assignment")
    subject_id = fields.Many2one('subject.subject', 'Subject', required=True,
                                 help="Select Subject")
    standard_id = fields.Many2one('school.standard', 'Class',
                                  help="Select Standard")
    teacher_id = fields.Many2one('school.teacher', 'Teacher', required=True,
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
                             'Status', default='draft')
    student_assign_ids = fields.One2many('school.student.assignment',
                                         'teacher_assignment_id',
                                         string="Student Assignments")
    type_submission = fields.Selection([('hardcopy', 'Hardcopy(Paperwork)'),
                                        ('softcopy', 'Softcopy')],
                                       default="hardcopy",
                                       string="Submission Type")
    file_format = fields.Many2one('file.format', 'File Format')
    attach_files = fields.Char("File Name")
    subject_standard_assignment = fields.Many2one("standard.standard")

    @api.onchange('standard_id')
    def onchange_subject_standard(self):
        self.subject_standard_assignment = self.standard_id.standard_id.id

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
            if not rec.attached_homework:
                raise ValidationError(_('''Please attach the homework!'''))
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
                            'stud_roll_no': std.roll_no,
                            'student_standard': std.standard_id.standard_id.id,
                            'submission_type': self.type_submission,
                            'attachfile_format': self.file_format.name}
                assignment_id = assignment_obj.create(ass_dict)
                attach = {'name': 'test',
                          'datas': rec.attached_homework,
                          'description': 'Assignment attachment',
                          'res_model': 'school.student.assignment',
                          'res_id': assignment_id.id}
                ir_attachment_obj.create(attach)
            rec.write({'state': 'active'})
        return True

    @api.multi
    def done_assignments(self):
        '''Changes the state to done'''
        self.write({'state': 'done'})

    @api.multi
    def unlink(self):
        for rec in self:
            if rec.state != 'draft':
                raise ValidationError(_('''You can delete record in unconfirm
                state only!'''))
        return super(SchoolTeacherAssignment, self).unlink()


class SchoolStudentAssignment(models.Model):
    _name = 'school.student.assignment'
    _description = 'Student Assignment Information'

    @api.constrains('assign_date', 'due_date')
    def check_date(self):
        if self.due_date < self.assign_date:
            raise ValidationError(_('Due date of homework should be greater \
                                   than Assign date!'))

    name = fields.Char('Assignment Name',
                       help="Assignment Name")
    subject_id = fields.Many2one('subject.subject', 'Subject', required=True,
                                 help="Select Subject")
    standard_id = fields.Many2one('school.standard', 'Class', required=True,
                                  help="Select Standard")
    rejection_reason = fields.Text('Reject Reason',
                                   help="Reject Reason")
    teacher_id = fields.Many2one('school.teacher', 'Teacher', required=True,
                                 help='''Teacher responsible to assign
                                 assignment''')
    assign_date = fields.Date('Assign Date', required=True,
                              help="Starting date of assignment")
    due_date = fields.Date('Due Date', required=True,
                           help="End date of assignment")
    state = fields.Selection([('draft', 'Draft'), ('active', 'Active'),
                              ('reject', 'Reject'),
                              ('done', 'Done')], 'Status',
                             default="draft",
                             help="States of assignment",
                             )
    student_id = fields.Many2one('student.student', 'Student', required=True,
                                 help="Name of Student")
    stud_roll_no = fields.Integer(string="Roll no",
                                  help="Roll No of student")
    attached_homework = fields.Binary('Attached Home work',
                                      help="Homework Attached by student")
    teacher_assignment_id = fields.Many2one('school.teacher.assignment',
                                            string="Teachers")
    student_standard = fields.Many2one('standard.standard', 'Student Standard')
    submission_type = fields.Selection([('hardcopy', 'Hardcopy(Paperwork)'),
                                        ('softcopy', 'Softcopy')],
                                       default="hardcopy",
                                       string="Submission Type")
    attachfile_format = fields.Char("Submission Fileformat")
    submit_assign = fields.Binary("Submit Assignment")
    file_name = fields.Char("File Name")

    @api.constrains('submit_assign', 'file_name')
    def check_file_format(self):
        if self.file_name:
            file_format = self.file_name.split('.')
            if len(file_format) == 2:
                file_format = file_format[1]
            else:
                raise ValidationError(_('''Kindly attach file with
                format: %s!''') % self.attachfile_format)
            if (file_format in self.attachfile_format or
                    self.attachfile_format in file_format):
                    return True
            raise ValidationError(_('''Kindly attach file with
                format: %s!''') % self.attachfile_format)

    @api.onchange('student_id')
    def onchange_student_standard(self):
        '''Method to get standard of selected student'''
        self.student_standard = self.student_id.standard_id.standard_id.id

    @api.multi
    def active_assignment(self):
        '''This method change state as active'''
        if not self.attached_homework:
            raise ValidationError(_('''Kindly attach homework!'''))
        self.write({'state': 'active'})

    @api.multi
    def done_assignment(self):
        ''' This method change state as done
            for school student assignment
            @return : True
        '''
        if self.submission_type == 'softcopy' and not self.submit_assign:
            raise ValidationError(_('''You have not attached the homework!
            Please attach the homework!'''))
        self.write({'state': 'done'})

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
                raise ValidationError(_('''You can delete record in unconfirm
                state only!'''))
        return super(SchoolStudentAssignment, self).unlink()


class FileFormat(models.Model):

        _name = "file.format"

        name = fields.Char("Name")
