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
from openerp import models, fields, api


class school_teacher_assignment(models.Model):

    _name = 'school.teacher.assignment'
    _description = 'Teacher Assignment Information'

    name = fields.Char('Assignment Name')
    subject_id = fields.Many2one('subject.subject', 'Subject', required=True)
    standard_id = fields.Many2one('school.standard', 'Standard')
    teacher_id = fields.Many2one('hr.employee', 'Teacher', required=True)
    assign_date = fields.Date("Assign Date", required=True)
    due_date = fields.Date("Due Date", required=True)
    attached_homework = fields.Binary("Attached Home work")
    state = fields.Selection([('draft', 'Draft'), ('active', 'Active')],
                             "Status", readonly=True, default='draft')
    school_id = fields.Many2one(related='standard_id.school_id',
                                string="School Name")
    cmp_id = fields.Many2one(related='school_id.company_id',
                             string="Company Name")

    @api.model
    def default_get(self, fields_list):
        res = super(school_teacher_assignment, self).default_get(fields_list)
        res.update({'state': 'draft'})
        return res

    @api.multi
    def active_assignment(self):
        '''  This method change state as active state and
        create assignment line
        @return : True
        '''
        assignment_obj = self.env['school.student.assignment']
        std_ids = []
        self._cr.execute("""select id from student_student where
                        standard_id=%s""", (self.standard_id.id,))
        student = self._cr.fetchall()
        if student:
            for stu in student:
                std_ids.append(stu[0])
        if std_ids:
            for std in std_ids:
                assignment_id = assignment_obj. \
                    create({'name': self.name,
                            'subject_id': self.subject_id.id,
                            'standard_id': self.standard_id.id,
                            'assign_date': self.assign_date,
                            'due_date': self.due_date, 'state': 'active',
                            'attached_homework': self.attached_homework,
                            'teacher_id': self.teacher_id.id, 'student_id': std
                            })
                if self.attached_homework:
                    data_attach = {'name': 'test',
                                   'datas': str(self.attached_homework),
                                   'description': 'Assignment attachment',
                                   'res_model': 'school.student.assignment',
                                   'res_id': assignment_id.id,
                                   }
                    self.env['ir.attachment'].create(data_attach)
                    self.write({'state': 'active'})
                    return True


class school_student_assignment(models.Model):

    _name = 'school.student.assignment'
    _description = 'Student Assignment Information'

    name = fields.Char("Assignment Name")
    subject_id = fields.Many2one("subject.subject", "Subject", required=True)
    standard_id = fields.Many2one("school.standard", "Standard", required=True)
    teacher_id = fields.Many2one("hr.employee", "Teacher", required=True)
    assign_date = fields.Date("Assign Date", required=True)
    due_date = fields.Date("Due Date", required=True)
    state = fields.Selection([('draft', 'Draft'), ('active', 'Active'),
                              ('done', 'done')], "Status", readonly=True)
    student_id = fields.Many2one('student.student', 'Student', required=True)
    attached_homework = fields.Binary("Attached Home work")

    @api.multi
    def done_assignment(self):
        self.write({'state': 'done'})
        return True

    # vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4:
