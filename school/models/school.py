# -*- coding: utf-8 -*-
# Part of Odoo. See LICENSE file for full copyright and licensing details.

import time
from datetime import date, datetime
from dateutil import relativedelta as rdelta
from openerp import models, fields, api
from openerp.tools.translate import _
from openerp.exceptions import Warning as UserError


class AcademicYear(models.Model):
    ''' Defines an academic year '''
    _name = "academic.year"
    _description = "Academic Year"
    _order = "sequence"

    sequence = fields.Integer('Sequence', required=True,
                              help="Sequence order you want to see this year.")
    name = fields.Char('Name', required=True, select=1,
                       help='Name of academic year')
    code = fields.Char('Code', required=True, select=1,
                       help='Code of academic year')
    date_start = fields.Date('Start Date', required=True,
                             help='Starting date of academic year')
    date_stop = fields.Date('End Date', required=True,
                            help='Ending of academic year')
    month_ids = fields.One2many('academic.month', 'year_id', 'Months',
                                help="related Academic months")
    grade_id = fields.Many2one('grade.master', "Grade")
    description = fields.Text('Description')

    @api.model
    def next_year(self, sequence):
        year_ids = self.search([('sequence', '>', sequence)],
                               order='id ASC', limit=1)
        if year_ids:
            return year_ids.id
        return False

    @api.multi
    def name_get(self):
        res = []
        for acd_year_rec in self:
            name = "[" + acd_year_rec['code'] + "]" + acd_year_rec['name']
            res.append((acd_year_rec['id'], name))
        return res

    @api.constrains('date_start', 'date_stop')
    def _check_academic_year(self):
        obj_academic_ids = self.search([])
        academic_list = []
        for rec_academic in obj_academic_ids:
            academic_list.append(rec_academic.id)
        for current_academic_yr in self:
            academic_list.remove(current_academic_yr.id)
            data_academic_yr = self.browse(academic_list)
            for old_ac in data_academic_yr:
                if old_ac.date_start <= self.date_start <= old_ac.date_stop\
                   or old_ac.date_start <= self.date_stop <= old_ac.date_stop:
                        raise UserError(_('Error! You cannot define\
                                         overlapping academic years.'))

    @api.constrains('date_start', 'date_stop')
    def _check_duration(self):
        dt_start = self.date_start
        dt_stop = self.date_stop
        if (dt_start and dt_stop and dt_stop < dt_start):
            raise UserError(_('Error! The duration of the academic year\
                             is invalid.'))


class AcademicMonth(models.Model):
    ''' Defining a month of an academic year '''
    _name = "academic.month"
    _description = "Academic Month"
    _order = "date_start"

    name = fields.Char('Name', required=True, help='Name of Academic month')
    code = fields.Char('Code', required=True, help='Code of Academic month')
    date_start = fields.Date('Start of Period', required=True,
                             help='Starting of academic month')
    date_stop = fields.Date('End of Period', required=True,
                            help='Ending of academic month')
    year_id = fields.Many2one('academic.year', 'Academic Year', required=True,
                              help="Related academic year ")
    description = fields.Text('Description')

    @api.constrains('date_start', 'date_stop')
    def _check_duration(self):
        dt_start = self.date_start
        dt_stop = self.date_stop
        if (dt_start and dt_stop and dt_stop < dt_start):
            raise UserError(_('Error ! The duration of the Month(s)\
                             is/are invalid.'))

    @api.constrains('year_id', 'date_start', 'date_stop')
    def _check_year_limit(self):
        start = self.date_start
        stop = self.date_stop
        if self.year_id and start and stop:
            y_st = self.year_id.date_start
            y_sp = self.year_id.date_stop
            if (y_sp < stop or y_sp < start or y_st > start or y_st > stop):
                raise UserError(_('Invalid Months ! Some months overlap or\
                                   the date period is not in the scope of the\
                                   academic year.'))


class FacultyFaculty(models.Model):
    ''' Defining a Faculty'''
    _name = "faculty.faculty"
    _description = "Faculty Information"

    name = fields.Char('Name', required=True)
    code = fields.Char('Code', required=True)
    faculty_manager_id = fields.Many2one('faculty.manager',
                                         'Dean of the Faculty')
    dean_id = fields.Many2one('hr.employee', 'Dean of the Faculty',
                              related="faculty_manager_id.employee_id",
                              store=True)
    department_ids = fields.One2many('standard.standard', "faculty_id",
                                     "Department in Faculty")
    description = fields.Text('Description')
    campus_ids = fields.Many2many('school.school', "faculty_campus_relation",
                                  'faculty_id', 'campus_id', 'Campus')

    @api.model
    def create(self, vals):
        faculty_id = super(FacultyFaculty, self).create(vals)
        if faculty_id.faculty_manager_id:
            manager_id = self.search([('faculty_manager_id', '=',
                                       self.faculty_manager_id.id),
                                      ('id', '!=', faculty_id.id)])
            if manager_id:
                raise UserError(_(str(faculty_id.faculty_manager_id.name) +
                                  ' is already Dean of other Faculty.'))
            faculty_id.faculty_manager_id.write({'faculty_id': self.id})
        return faculty_id

    @api.multi
    def write(self, vals):
        if vals.get('faculty_manager_id'):
            if (not vals.get('faculty_manager_write')):
                raise UserError("You can't change the manager from here!\
                \nKindly change the Faculty from the Faculty manager Profile.")
            else:
                self.faculty_manager_id.write({'faculty_id': self.id,
                                               'faculty_write': True})
        return super(FacultyFaculty, self).write(vals)


class StandardMedium(models.Model):
    ''' Defining a medium(ENGLISH, HINDI, GUJARATI) related to standard'''
    _name = "standard.medium"
    _description = "Standard Medium"

    name = fields.Char('Name', required=True)
    code = fields.Char('Code', required=True)
    description = fields.Text('Description')


class CourseYears(models.Model):
    ''' Defining a Years to complete the Course'''
    _name = "course.years"
    _description = "Course Specification"
    _sql_constraints = [('name_unique', 'unique(name,course_id)',
                        ' You can not create same course level for this\
                        department!')]

    @api.one
    @api.depends('subject_id.weightage')
    def _get_unit(self):
        unit = 0
        for unit_subject in self.subject_id:
            unit += unit_subject.weightage
        self.unit = unit

    name = fields.Char('Name')
    code = fields.Char('Code')
    unit = fields.Integer("WeightAge/Unit", compute="_get_unit", store=True)
    subject_id = fields.Many2many('subject.subject', 'course_year_id',
                                  'subject_id', "course_year_subject_rel",
                                  'Subjects')
    course_id = fields.Many2one('standard.standard', 'Department')
#    course_year_id = fields.Many2one('course.years', 'Course Subjects')
    description = fields.Text('Description')
    course_year_duration_ids = fields.One2many('course.years.duration',
                                               'course_year_id',
                                               'Course Duration')

    @api.multi
    def name_get(self):
        res = []
        for semester in self:
            name = semester.name
            if semester.course_id:
                name += "[" + semester.course_id.name + "]"
            res.append((semester.id, name))
        return res

    @api.model
    def name_search(self, name='', args=None, operator='ilike',
                    limit=100):
        sem_id = self._context.get('sem_id')
        if sem_id:
            rec = self.search([('id', '=', sem_id)])
            return rec.name_get()
        else:
            return super(CourseYears, self).name_search(name, args,
                                                        operator=operator,
                                                        limit=limit)


class CourseYearDuration(models.Model):
    _name = "course.years.duration"

    course_year_id = fields.Many2one('course.years', 'Level')
    academic_year_id = fields.Many2one('academic.year', 'Academic year')
    month_duration_start = fields.Many2one('academic.month', 'Starting Month')
    month_duration_end = fields.Many2one('academic.month', 'Ending Month')


class StandardDivision(models.Model):
    ''' Defining a division(A, B, C) related to standard'''
    _name = "standard.division"
    _description = "Standard Division"
    _order = "sequence"

    sequence = fields.Integer('Sequence', required=False)
    name = fields.Char('Name', required=True)
    code = fields.Char('Code', required=True)
    description = fields.Text('Description')


class StandardStandard(models.Model):
    ''' Defining Standard Information '''
    _name = 'standard.standard'
    _description = 'Standard Information'

    @api.constrains('attendance_criteria')
    def check_Utme_subject(self):
        att_ctiteria = self.attendance_criteria
        if att_ctiteria >= 100 or att_ctiteria < 0:
            raise UserError(_("Invalid Attendance Criteria."))

    sequence = fields.Integer('Name', default=5)
    name = fields.Char('Name', required=True)
    code = fields.Char('Code', required=True)
    description = fields.Text('Description')
    d_manager_id = fields.Many2one('department.manager', 'Department Head')
    department_manager_id = fields.Many2one('hr.employee', 'Department Head',
                                            related="d_manager_id.employee_id",
                                            store=True)
    course_year_ids = fields.One2many('course.years', 'course_id',
                                      'Course Subjects')
    faculty_id = fields.Many2one("faculty.faculty", "Faculty")
    certi_needed_ids = fields.One2many('student.document.files', 'course_id',
                                       'Required Certificates to submit')
    minimum_score = fields.Integer('Minimum Score', default="220")
    maximum_score = fields.Integer('Maximum Score', default="400")
    electives_subject_ids = fields.Many2many('subject.subject',
                                             'electives_sub_id',
                                             'standard_id',
                                             'elective_subject_standard_rel',
                                             'Elective Subjects')
    attendance_criteria = fields.Integer('Attendance Criteria(%)', default=75)
    deferment_fees = fields.Float('Deferment Fees', default=25000)
    requirements = fields.One2many('department.need.requirement',
                                   'department_id', 'Requirement')

    @api.model
    def create(self, vals):
        department_id = super(StandardStandard, self).create(vals)
        if department_id.d_manager_id:
            manager_id = self.search([('campus_manager_id', '=',
                                       self.d_manager_id.id),
                                      ('id', '!=', department_id.id)])
            if manager_id:
                raise UserError(_(str(department_id.d_manager_id.name) +
                                  ' is already manager of other Department.'))
            department_id.d_manager_id.write({'d_id': self.id})
        return department_id

    @api.multi
    def write(self, vals):
        if vals.get('d_manager_id'):
            if (not vals.get('department_manager_write')):
                raise UserError("You can't change the manager from here!\
                \nKindly change the Department from the Department manager\
                Profile.")
            else:
                self.d_manager_id.write({'d_id': self.id,
                                         'department_write': True})
        return super(StandardStandard, self).write(vals)

    @api.model
    def next_standard(self, sequence):
        stand_ids = self.search([('sequence', '>', sequence)],
                                order='id ASC', limit=1)
        if stand_ids:
            return stand_ids.id
        return False

    @api.model
    def name_search(self, name='', args=None, operator='ilike',
                    limit=100):
        dept_id = self._context.get('dept_id')
        if dept_id:
            rec = self.search([('id', '=', dept_id)])
            return rec.name_get()
        else:
            return super(StandardStandard, self).name_search(name, args,
                                                             operator=operator,
                                                             limit=limit)


class SchoolStandard(models.Model):
    ''' Defining a standard related to school '''
    _name = 'school.standard'
    _description = 'School Standards'
    _rec_name = "school_id"

    @api.depends('standard_id')
    def _compute_student(self):
        domain = [('standard_id', '=', self._ids),
                  ('standard_id.division_id', '=', self.division_id.id),
                  ('state', '=', 'done')]
        if self.standard_id:
            self.student_ids = self.env['student.student'].search(domain)

    @api.depends('standard_id', 'division_id')
    def _standard_name(self):
        name = self.name_get()
        self.stan_name = name[0][1]

    school_id = fields.Many2one('school.school', 'Campus', required=True)
    stan_name = fields.Char("Standard Name", compute='_standard_name')
    standard_id = fields.Many2one('standard.standard', 'Department',
                                  required=True)
    division_id = fields.Many2one('standard.division', 'Division')
    medium_id = fields.Many2one('standard.medium', 'Medium', required=True)
    subject_ids = fields.Many2many('subject.subject', 'subject_standards_rel',
                                   'subject_id', 'standard_id', 'Subject')
    user_id = fields.Many2one('school.teacher', 'Responsible Lecturer')
    student_ids = fields.One2many('student.student', 'standard_id',
                                  'Student In Class',
                                  compute='_compute_student')
    color = fields.Integer('Color Index')
    passing = fields.Integer('No Of ATKT', help="Allowed No of ATKTs")
    cmp_id = fields.Many2one('res.company', 'Company Name',
                             related='school_id.company_id', store=True)
    faculty_id = fields.Many2one('faculty.faculty', 'Faculty',
                                 related='standard_id.faculty_id', store=True)
    lecturer_ids = fields.Many2many('school.teacher',
                                    'standard_teacher_relation',
                                    'lecturer_id', 'standard_id',
                                    'Related Lecturer in Class')

    @api.onchange('standard_id')
    def onchange_standard_id(self):
        if self.standard_id:
            subject_ids = []
            for subject in self.standard_id.course_year_ids:
                [subject_ids.append(sub.id) for sub in subject.subject_id]
            self.subject_ids = [(6, 0, subject_ids)]

    @api.multi
    def name_get(self):
        res = []
        for standard in self:
            name = standard.standard_id.code
            name += "-(" + standard.standard_id.name + ")"
            if standard.division_id:
                name += "-(" + standard.division_id.name + ")"
            res.append((standard.id, name))
        return res

    @api.model
    def name_search(self, name='', args=None, operator='ilike',
                    limit=100):
        dept_id = self._context.get('depart_id')
        if dept_id:
            res = self.env['school.standard'].search([('standard_id',
                                                     '=', dept_id)])
            return res.name_get()
        else:
            return super(SchoolStandard, self).name_search(name, args,
                                                           operator=operator,
                                                           limit=limit)


class SchoolSchool(models.Model):
    ''' Defining School Information '''
    _name = 'school.school'
    _description = 'School Information'

    company_id = fields.Many2one('res.company', 'University',
                                 ondelete="cascade", change_default=True,
                                 default=lambda obj_c: obj_c.env['res.users'].
                                 browse([obj_c._uid])[0].company_id,
                                 required=True)
    name = fields.Char('Campus', required=True)
    code = fields.Char('Code', required=True, select=1)
    standards = fields.One2many('school.standard', 'school_id',
                                'Academic Class')
    street = fields.Char("Street")
    street2 = fields.Char("Street2")
    zip = fields.Char("Zip")
    city = fields.Char("City")
    state_id = fields.Many2one('res.country.state', "State")
    country_id = fields.Many2one('res.country', "Country",)
    email = fields.Char("Email")
    phone = fields.Char("Phone")
    fax = fields.Char("Fax")
    website = fields.Char("Website")
    campus_manager_id = fields.Many2one('campus.manager', 'Campus Manager')
    campus_mng_id = fields.Many2one('hr.employee', 'Campus Manager',
                                    related="campus_manager_id.employee_id",
                                    store=True)
    faculty_ids = fields.Many2many('faculty.faculty',
                                   'faculty_campus_relation',
                                   'campus_id', 'faculty_id',
                                   'Faculty')
    school_feesmng_id = fields.Many2many('fees.manager',
                                         'school_fees_rel',
                                         'campus_id',
                                         'school_feesmng_id',
                                         'Fees Manager(s)',
                                         help="Campus for which the he/she\
                                           responsible for.")

    @api.model
    def create(self, vals):
        campus_id = super(SchoolSchool, self).create(vals)
        if campus_id.campus_manager_id:
            manager_id = self.search([('campus_manager_id', '=',
                                       self.campus_manager_id.id),
                                      ('id', '!=', campus_id.id)])
            if manager_id:
                raise UserError(_(str(campus_id.campus_manager_id.name) +
                                  ' is already Manager of other Faculty.'))
            campus_id.campus_manager_id.write({'campus_id': self.id})
        return campus_id

    @api.multi
    def write(self, vals):
        if vals.get('campus_manager_id'):
            if (not vals.get('campus_manager_write')):
                raise UserError("You can't change the manager from here!\
                \nKindly change the Campus from the Campus manager Profile.")
            else:
                self.campus_manager_id.write({'campus_id': self.id,
                                              'campus_write': True})
        return super(SchoolSchool, self).write(vals)


class SubjectSubject(models.Model):
    '''Defining a subject '''
    _name = "subject.subject"
    _description = "Subjects"

    _sql_constraints = [('code_unique', 'unique(code)',
                         'Subject code must be unique!')]

    @api.one
    @api.depends('student_bool')
    def _get_group_student(self):
        ir_obj = self.env['ir.model.data']
        stu_xml_id = ir_obj.get_object('school',
                                       'group_school_student')
        grps = [group.id
                for group in self.env['res.users'].browse(self._uid).groups_id]
        if stu_xml_id.id in grps:
            self.student_bool = True

    name = fields.Char('Name', required=True)
    code = fields.Char('Code', required=True)
    maximum_marks = fields.Integer("Maximum marks")
    minimum_marks = fields.Integer("Minimum marks")
    weightage = fields.Integer("WeightAge/Unit")
    teacher_ids = fields.Many2many('school.teacher', 'subject_teacher_rel',
                                   'subject_id', 'teacher_id', 'Lecturer')
    standard_ids = fields.Many2many('standard.standard',
                                    'subject_standards_rel',
                                    'standard_id', 'subject_id', 'Courses')
    is_practical = fields.Boolean('Is Practical',
                                  help='Check this if subject is practical.')
    no_exam = fields.Boolean("No Exam",
                             help='Check this if subject has no exam.')
    subject_type = fields.Selection([('compulsory', 'Compulsory'),
                                     ('elective', 'Elective')],
                                    help="Type of Subject",
                                    default="compulsory")
    department_id = fields.Many2one("standard.standard", "Department")
    student_ids = fields.Many2many('student.student',
                                   'elective_subject_student_rel',
                                   'subject_id', 'student_id', 'Students')
    level_id = fields.Many2one("course.years", "Level")
    student_bool = fields.Boolean('Student user', compute="_get_group_student")

    @api.model
    def name_search(self, name='', args=None, operator='ilike',
                    limit=100):
        args = []
        dept_id = self._context.get('depart_id')
        sems_id = self._context.get('sems_id')
        teacher_id = self._context.get('teacher_id')
        semester_id = self._context.get('semester_id')
        year_id = self._context.get('year_id')
        stand_id = self._context.get('standard_id')
        weekday = self._context.get('weekday')
        data = []
        if dept_id and sems_id:
            for sub in self.search([('department_id', '=', dept_id),
                                    ('level_id', '=', sems_id),
                                    ('subject_type', '=', 'compulsory')]):
                data.append(sub.id)
            for ele_sub in self.search([('department_id', '=', dept_id),
                                        ('subject_type', '=', 'elective')]):
                data.append(ele_sub.id)
            args.extend([('id', 'in', data)])
        if (teacher_id and semester_id and year_id and stand_id and weekday):
            tt_res = self.env['time.table'].search([('standard_id', '=',
                                                     stand_id),
                                                    ('semester_id', '=',
                                                     semester_id),
                                                    ('year_id', '=', year_id),
                                                    ('timetable_type', '=',
                                                     'regular')])
            data = []
            for tt_line in tt_res.timetable_ids.\
                    search([('teacher_id', '=', teacher_id),
                            ('table_id', 'in', tt_res.ids),
                            ('week_day', '=', weekday)]):
                data.append(tt_line.subject_id.id)
            args.extend([('id', 'in', data)])
        return super(SubjectSubject, self).name_search(name=name, args=args,
                                                       operator=operator,
                                                       limit=limit)


class SubjectSyllabus(models.Model):
    '''Defining a  syllabus'''
    _name = "subject.syllabus"
    _description = "Syllabus"
    _rec_name = "duration"

    subject_id = fields.Many2one('subject.subject', 'Subject')
    duration = fields.Char("Duration")
    topic = fields.Text("Topic")
    course_id = fields.Many2one("standard.standard", "Course")
    level_id = fields.Many2one("course.years", "Level")
    week = fields.Char("Week")
    readings = fields.Char("Readings")
    activities = fields.Text("Activities")
    due_date = fields.Date("Due Date")

    @api.onchange('subject_id')
    def change_subject_id(self):
        self.course_id = ''
        if self.subject_id:
            course_ids = [course.id for course
                          in self.subject_id.department_id]
            return {'domain': {'course_id': [('id', 'in', course_ids)]}}

    @api.onchange('course_id')
    def change_course_id(self):
        self.level_id = ''
        if self.course_id:
            level_ids = [level.id for level in self.course_id.course_year_ids]
            return {'domain': {'level_id': [('id', 'in', level_ids)]}}

    @api.constrains('due_date')
    def check_utme_ids(self):
        if self.due_date and self.due_date <= date.today():
            raise UserError(_("Due Date Should be grater \
                             than the Current Date!."))


class StudentGrn(models.Model):
    _name = "student.grn"
    _rec_name = "grn_no"

    @api.one
    def _grn_no(self):
        for stud_grn in self:
            grn_no1 = " "
            grn_no2 = " "
            grn_no1 = stud_grn['grn']
            if stud_grn['prefix'] == 'static':
                grn_no1 = stud_grn['static_prefix'] + stud_grn['grn']
            elif stud_grn['prefix'] == 'school':
                a = stud_grn.schoolprefix_id.code
                grn_no1 = a + stud_grn['grn']
            elif stud_grn['prefix'] == 'year':
                grn_no1 = time.strftime('%Y') + stud_grn['grn']
            elif stud_grn['prefix'] == 'month':
                grn_no1 = time.strftime('%m') + stud_grn['grn']
            grn_no2 = grn_no1
            if stud_grn['postfix'] == 'static':
                grn_no2 = grn_no1 + stud_grn['static_postfix']
            elif stud_grn['postfix'] == 'school':
                b = stud_grn.schoolpostfix_id.code
                grn_no2 = grn_no1 + b
            elif stud_grn['postfix'] == 'year':
                grn_no2 = grn_no1 + time.strftime('%Y')
            elif stud_grn['postfix'] == 'month':
                grn_no2 = grn_no1 + time.strftime('%m')
            self.grn_no = grn_no2

    grn = fields.Char('GR no', help='General Reg Number', readonly=True,
                      default=lambda obj:
                      obj.env['ir.sequence'].get('student.grn'))
    name = fields.Char('GRN Format Name', required=True)
    prefix = fields.Selection([('school', 'School Name'),
                               ('year', 'Year'), ('month', 'Month'),
                               ('static', 'Static String')], 'Prefix')
    schoolprefix_id = fields.Many2one('school.school',
                                      'School Name For Prefix')
    schoolpostfix_id = fields.Many2one('school.school',
                                       'School Name For Suffix')
    postfix = fields.Selection([('school', 'School Name'),
                                ('year', 'Year'), ('month', 'Month'),
                                ('static', 'Static String')], 'Suffix')
    static_prefix = fields.Char('Static String for Prefix')
    static_postfix = fields.Char('Static String for Suffix')
    grn_no = fields.Char('Generated GR No.', compute='_grn_no')


class MotherTongue(models.Model):
    _name = 'mother.toungue'

    name = fields.Char("Mother Tongue")


class StudentAward(models.Model):
    _name = 'student.award'

    award_list_id = fields.Many2one('student.student', 'Student')
    name = fields.Char('Award Name')
    description = fields.Char('Description')


class AttendanceType(models.Model):
    _name = "attendance.type"
    _description = "School Type"

    name = fields.Char('Name', required=True)
    code = fields.Char('Code', required=True)


class StudentDescription(models.Model):
    ''' Defining a Student Description'''
    _name = 'student.description'

    des_id = fields.Many2one('student.student', 'Description')
    name = fields.Char('Name')
    description = fields.Char('Description')


class StudentHistory(models.Model):
    _name = "student.history"

    student_id = fields.Many2one('student.student', 'Student')
    academice_year_id = fields.Many2one('academic.year', 'Academic Year',
                                        required=True)
#    exam_name = fields.Char("Exam")
    standard_id = fields.Many2one('school.standard', 'Academic Class',
                                  required=True)
    semester_id = fields.Many2one('course.years', 'Semester')


class StudentExamRepeat(models.Model):
    _name = 'student.exam.repeat'
    _description = 'Student Exam Repeat'

    student_id = fields.Many2one('student.student', 'Student')
    standard_id = fields.Many2one('school.standard', 'Academic Class')
    semester_id = fields.Many2one('course.years', 'Semester')
    subject_id = fields.Many2one('subject.subject', 'Subject Name')
    state = fields.Selection([('draft', 'Draft'),
                              ('done', 'Done')])


class StudentCertificate(models.Model):
    _name = "student.certificate"

    student_id = fields.Many2one('student.student', 'Student')
    description = fields.Char('Description')
    certi = fields.Binary('Certificate', required=True)


class StudentPreviousSchool(models.Model):
    ''' Defining a student previous school information '''
    _name = "student.previous.school"
    _description = "Student Previous School"

    previous_school_id = fields.Many2one('student.student', 'Student')
    name = fields.Char('School/University Name')
    qualification = fields.Many2one('requirement.qualification',
                                    'Qualification', required=True)
    score = fields.Char('Percentage(%)', required="1")
    city = fields.Char('City')
    country_id = fields.Many2one('res.country', 'Country')
    state_id = fields.Many2one('res.country.state', 'State')
    admission_date = fields.Date('Admission Date')
    exit_date = fields.Date('Exit Date')
    school_attended = fields.Binary('School  Attended')


class StudentFamilyContact(models.Model):
    ''' Defining a student emergency contact information '''
    _name = "student.family.contact"
    _description = "Student Family Contact"

    family_contact_id = fields.Many2one('student.student', 'Student')
    rel_name = fields.Selection([('exist', 'Link to Existing Student'),
                                 ('new', 'Create New Relative Name')],
                                'Related Student', help="Select Name",
                                required=True)
    user_id = fields.Many2one('res.users', 'User ID', ondelete="cascade",
                              select=True)
    stu_name = fields.Char('Name', related='user_id.name',
                           help="Select Student From Existing List")
    name = fields.Char('Name')
    relation = fields.Many2one('student.relation.master', 'Relation',
                               required=True)
    phone = fields.Char('Phone', required=True)
    email = fields.Char('E-Mail')
    next_of_kin = fields.Char('Next of kin')
    next_of_kin_contect = fields.Char('Next of kin Contect')
    relative_name = fields.Char(compute='_get_name', string='Name')

    @api.multi
    @api.depends('relation')
    def _get_name(self):
        for rec in self:
            if rec.stu_name:
                rec.relative_name = rec.stu_name
            else:
                rec.relative_name = rec.name


class StudentRelationMaster(models.Model):
    ''' Student Relation Information '''
    _name = "student.relation.master"
    _description = "Student Relation Master"

    name = fields.Char('Name', required=True, help="Enter Relation name")
    seq_no = fields.Integer('Sequence')


class GradeMaster(models.Model):
    _name = 'grade.master'

    name = fields.Char('Grade', select=1, required=True)
    type = fields.Selection((('exam', 'Exam'),
                             ('assignment', 'Assignment')),
                            'Grade Type')
    grade_ids = fields.One2many('grade.line', 'grade_id', 'Grade Name')


class GradeLine(models.Model):
    _name = 'grade.line'
    _rec_name = 'grade'

    from_mark = fields.Integer('From Percentage(Lower)', required=True,
                               help='The grade will starts from this marks.')
    to_mark = fields.Integer('To Percentage(Higher)', required=True,
                             help='The grade will ends to this marks.')
    grade = fields.Selection((('A', 'A'),
                              ('B', 'B'),
                              ('C', 'C'),
                              ('D', 'D'),
                              ('E', 'E'),
                              ('F', 'F')),
                             'Grade', required=True, help="Grade")
    remarks = fields.Selection((('Excellent', 'Excellent'),
                                ('Very Good', 'Very Good'),
                                ('Good', 'Good'),
                                ('Fair', 'Fair'),
                                ('Pass', 'Pass'),
                                ('Fail', 'Fail')),
                               'Remarks', help="Remarks")
    sequence = fields.Integer('Sequence', help="Sequence order of the grade.")
    fail = fields.Boolean('Fail', help='If fail field is set to True,\
                                  it will allow you to set the grade as fail.')
    grade_id = fields.Many2one("grade.master", 'Grade')
    name = fields.Char('Name')

    @api.constrains('to_mark', 'from_mark')
    def _check_duration(self):
        if self.to_mark and self.from_mark:
            if self.from_mark > self.to_mark:
                raise UserError(_("Error! The TO Percentage can't more then \
                             From Percentage."))
            elif self.to_mark <= -1:
                raise UserError(_("Error! Invalid the TO Percentage "))
            elif self.from_mark >= 101:
                raise UserError(_("Error! Invalid the From percentage."))


class StudentNews(models.Model):
    _name = 'student.news'
    _description = 'Student News'
    _rec_name = 'subject'

    subject = fields.Char('Subject', required=True,
                          help='Subject of the news.')
    description = fields.Text('Description', help="Description")
    date = fields.Date('Expiry Date', help='Expiry date of the news.')
    user_ids = fields.Many2many('res.users', 'user_news_rel', 'id', 'user_ids',
                                'User News',
                                help='Name to whom this news is related.')
    color = fields.Integer('Color Index', default=0)

    @api.multi
    def news_update(self):
        emp_obj = self.env['school.teacher']
        obj_mail_server = self.env['ir.mail_server']
        mail_server_ids = obj_mail_server.search([])
        if not mail_server_ids:
            raise UserError(_('No mail outgoing mail server specified!'))
        mail_server_record = mail_server_ids[0]
        email_list = []
        for news in self:
            if news.user_ids:
                for user in news.user_ids:
                    if user.email:
                        email_list.append(user.email)
                if not email_list:
                    raise UserError(_("Email not found in users !"))
            else:
                for employee in emp_obj.search([]):
                    if employee.work_email:
                        email_list.append(employee.work_email)
                    elif employee.user_id and employee.user_id.email:
                        email_list.append(employee.user_id.email)
                if not email_list:
                    raise UserError(_('Mail Error'), _("Email not defined!"))
            t = datetime.strptime(news.date, '%Y-%m-%d %H:%M:%S')
            body = 'Hi,<br/><br/> \
                    This is a news update from <b>%s</b>posted at %s<br/><br/>\
                    %s <br/><br/>\
                    Thank you.' % (self._cr.dbname,
                                   t.strftime('%d-%m-%Y %H:%M:%S'),
                                   news.description)
            smtp_user = mail_server_record.smtp_user
            notification = 'Notification for news update.'
            message = obj_mail_server.build_email(email_from=smtp_user,
                                                  email_to=email_list,
                                                  subject=notification,
                                                  body=body,
                                                  body_alternative=body,
                                                  email_cc=None,
                                                  email_bcc=None,
                                                  reply_to=smtp_user,
                                                  attachments=None,
                                                  references=None,
                                                  object_id=None,
                                                  subtype='html',
                                                  subtype_alternative=None,
                                                  headers=None)
            obj_mail_server.send_email(message=message,
                                       mail_server_id=mail_server_ids[0].id)
        return True


class StudentReminder(models.Model):
    _name = 'student.reminder'

    @api.model
    def _get_student(self):
        user_rec = self.env['res.users'].browse(self._uid)
        student_group = self.pool.get('ir.model.data').get_object(
                                                    self._cr,
                                                    self._uid,
                                                    'school',
                                                    'group_school_student')
        groups = [grp.id for grp in user_rec.groups_id]
        if student_group.id in groups:
            student = self.env['student.student'].search([('user_id', '=',
                                                           self._uid)])
            if student:
                return student.id

    stu_id = fields.Many2one('student.student', 'Student Name', required=True,
                             default=_get_student)
    name = fields.Char('Title')
    date = fields.Date('Date')
    description = fields.Text('Description')
    color = fields.Integer('Color Index', default=0)
    state = fields.Selection([('draft', 'Draft'),
                              ('gone', 'Gone'),
                              ('done', 'Done')],
                             default='draft')
    action_data = fields.Char('Action Data', invisible=True)
    action_payment = fields.Boolean('Action Payment', invisible=True)

    @api.constrains('date')
    def check_date(self):
        '''
        This method is used to validate the date.
        -------------------------------------------------------------------
        @param self: object pointer
        @return: raise warning depending on the validation
        '''
        curr_date = datetime.now().date()
        if self.date <= str(curr_date):
            raise UserError(_('Date Should be grater than the Current Date!'))

    @api.multi
    def action_done(self):
        self.state = 'done'

    @api.model
    def reminder_gone(self):
        """
        This method is for scheduler
        every day scheduler will call this method and
        not done reminder set in gone state.
        --------------------------------------------------------------
        @param self: The object pointer
        @return: update reminder list
        """

        curr_date = datetime.now().date()
        remind_id = self.search([('date', '<', curr_date),
                                 ('state', '=', 'draft')])
        remind_id.write({'state': 'gone'})
        return True

    @api.model
    def send_mail_common(self, template, rec_id):
        template_rec = self.env['mail.template'].browse(template.id)
        template_rec.sudo().send_mail(rec_id.id, force_send=True)
        return True

    @api.model
    def create(self, vals):
        result = super(StudentReminder, self).create(vals)
        template = self.env.ref(
                                'school.email_template_student_reminders',
                                False)
        self.send_mail_common(template, result)
        return result


class StudentCast(models.Model):
    _name = "student.cast"

    name = fields.Char("Name", required=True)


class HrEmployee(models.Model):

    _inherit = 'hr.employee'

    employee_type = fields.Selection([('academic', 'Academic'),
                                      ('nonacademic', 'Non-academic')],
                                     "Employee Type", default="academic")


class RoomRoom(models.Model):

    _name = 'room.room'

    name = fields.Char(string='Room', required=True, copy=False,
                       readonly=True, index=True, default='New')
    school_id = fields.Many2one('school.school', 'School', required=True)
    room_type_id = fields.Many2one('room.type', 'Room Type', required=True)
    floor_id = fields.Many2one('school.floor', 'School Floor', required=True)

    @api.model
    def create(self, vals):
        if vals.get('name', 'New') == 'New':
            vals['name'] = self.env['ir.sequence'
                                    ].next_by_code('room.room') or 'New'
        return super(RoomRoom, self).create(vals)

    @api.model
    def name_search(self, name='', args=None, operator='ilike',
                    limit=100):
        args = []
        teacher_id = self._context.get('teacher_id')
        semester_id = self._context.get('semester_id')
        year_id = self._context.get('year_id')
        standard_id = self._context.get('standard_id')
        weekday = self._context.get('weekday')
        if semester_id and teacher_id:
            tt_res = self.env['time.table'].search([('standard_id', '=',
                                                     standard_id),
                                                    ('semester_id', '=',
                                                     semester_id),
                                                    ('year_id', '=', year_id),
                                                    ('timetable_type', '=',
                                                     'regular')])
            data = []
            for tt_line in tt_res.timetable_ids.\
                    search([('teacher_id', '=', teacher_id),
                            ('table_id', 'in', tt_res.ids),
                            ('week_day', '=', weekday)]):
                data.append(tt_line.room_id.id)
            args.extend([('id', 'in', data)])
        return super(RoomRoom, self).name_search(name=name, args=args,
                                                 operator=operator,
                                                 limit=limit)


class RoomType(models.Model):

    _name = 'room.type'
    _description = 'Room Types'

    name = fields.Char('Room Type')


class SchoolFloor(models.Model):

    _name = "school.floor"
    _description = "Floor"

    name = fields.Char('Floor Name', size=64, required=True, select=True,
                       help="School floor name")
    sequence = fields.Integer('Sequence', size=64,
                              help='School floor sequence')
    school_id = fields.Many2one('school.school', 'School', required=True)


class StudentSubjects(models.Model):
    _name = 'student.subjects'
    _description = "Student Subjects"

    @api.one
    @api.depends('semester_id')
    def _get_group_student(self):
        ir_obj = self.env['ir.model.data']
        stu_xml_id = ir_obj.get_object('school',
                                       'group_school_student')
        grps = [group.id
                for group in self.env['res.users'].browse(self._uid).groups_id]
        if stu_xml_id.id in grps:
            self.student_bool = True

    @api.one
    @api.depends('semester_id')
    def _get_subjects_credits(self):
        self.total_credit_points = 0
        if self.subjects_ids:
            for com_sub in self.subjects_ids:
                self.total_credit_points += com_sub.weightage
        if self.repeat_sub_ids:
            for re_sub in self.repeat_sub_ids:
                self.total_credit_points += re_sub.subject_id.weightage
        if self.electives_ids:
            for ele_sub in self.electives_ids:
                self.total_credit_points += ele_sub.weightage
        if self.total_credit_points >= 22:
            raise Warning("Overloads are not allowed,\
                Please Drop The elective Subjects")

    student_id = fields.Many2one('student.student', 'Student')
    student_bool = fields.Boolean('Student user', compute="_get_group_student")
    semester_id = fields.Many2one('course.years', 'Semester')
    subjects_ids = fields.Many2many('subject.subject', 'subjects_id',
                                    'student_id',
                                    'student_subjest_rel', 'Subjects')
#    electives_ids = fields.Many2many('subject.subject', 'electives_ids',
#                                    'student_id', 'student_elective_sub_rel',
#                                    'Electives')
    repeat_sub_ids = fields.Many2many('student.exam.repeat', 'repeat_sub_id',
                                      'student_id',
                                      'student_subject_repeat_rel',
                                      'Repeat Subject')
    total_credit_points = fields.Integer(compute="_get_subjects_credits",
                                         string="Total Credit")

    @api.onchange('semester_id')
    def _onchange_semester(self):
        if self.semester_id:
            res = self.env['subject.subject'].search([('level_id', '=',
                                                       self.semester_id.id),
                                                      ('subject_type', '=',
                                                       'compulsory')])
            self.subjects_ids = [(6, 0, res.ids)]


class StudentDashboard(models.Model):
    _name = 'student.dashboard'
    _description = "Student Dashboard"

    name = fields.Char("Name")


class ResCountryState(models.Model):
    _inherit = 'res.country.state'

    state_lga_ids = fields.One2many('state.lga', 'state_id', 'State LGA')


class StateLga(models.Model):
    _name = 'state.lga'

    name = fields.Char("LGA Name")
    code = fields.Char("LGA Code")
    state_id = fields.Many2one('res.country.state', 'State')


class StudentDocumentFiles(models.Model):

    _name = 'student.document.files'

    name = fields.Many2one('department.need.document', 'Document Name',
                           required="1")
    file_datas = fields.Binary('Attachments')
    course_id = fields.Many2one('standard.standard', 'Course Ref.')
    file_name = fields.Char('File Name')


class StudentDocuments(models.Model):

    _name = 'student.documents'

    name = fields.Many2one('department.need.document', 'Document Name',
                           required="1")
    file_datas = fields.Binary('Attachments')
    student_id = fields.Many2one('student.student', 'Student Ref.')


class DepartmentNeedDocument(models.Model):

    _name = 'department.need.document'

    name = fields.Char('Document Name', required="1")


class DepartmentNeedRequirement(models.Model):

    _name = 'department.need.requirement'

    name = fields.Many2one('requirement.qualification',
                           'Requirement Qualification',
                           required="1")
    department_id = fields.Many2one('standard.standard',
                                    'Course Ref.')
    score = fields.Char('Requirement Percentage(%)', required="1")


class RequirementQualification(models.Model):

    _name = 'requirement.qualification'

    name = fields.Char('Requirement Qualification', required="1")


class PostLectureNotes(models.Model):

    _name = 'post.lecture.notes'

    name = fields.Char("Notes Name")
    lecturer_id = fields.Many2one('school.teacher', 'Lecturer')
    class_id = fields.Many2one('school.standard', 'Academic Class')
    subject_id = fields.Many2one('subject.subject', 'Subject')
    note = fields.Binary('Lecture Note')
    student_ids = fields.Many2many('student.student', 'student_id',
                                   'post_lect_note_id',
                                   'post_lect_notes_student_rel',
                                   'Students')
    state = fields.Selection([('draft', 'Draft'),
                              ('post', 'Post')],
                             'Status',
                             default='draft')

    @api.onchange('lecturer_id')
    def change_lecturer_id(self):
        self.class_id = ''
        if self.lecturer_id:
            course_ids = [course.id for course in self.lecturer_id.standard_id]
            return {'domain': {'class_id': [('id', 'in', course_ids)]}}

    @api.onchange('class_id')
    def change_class_id(self):
        self.student_ids = ''
        self.subject_id = ''
        student_list = []
        if self.class_id:
            for student in self.class_id.student_ids:
                student_list.append(student.id)
            self.student_ids = [(6, 0, student_list)]
            subject_ids = [subject.id for subject
                           in self.lecturer_id.subject_id]
            return {'domain': {'subject_id': [('id', 'in', subject_ids)]}}

    @api.multi
    def set_post(self):
        if self.student_ids:
            template = self.env.ref('school.email_temp_student_post_lec_notes',
                                    False)
            template_rec = self.env['mail.template'].browse(template.id)
            template_rec.send_mail(self.id, force_send=True)
            self.state = 'post'
        else:
            raise UserError(_('You must add Student'))


class AccountInvoice(models.Model):
    _inherit = "account.invoice"

    deferment_id = fields.Many2one('student.drop.request',
                                   'Deferment Request')


class AccountPayment(models.Model):
    _inherit = "account.payment"

    @api.multi
    def post(self):
        post_id = super(AccountPayment, self).post()
        if self._context.get('active_model') == 'account.invoice':
            if self._context.get('active_id'):
                active_inv = self._context.get('active_id')
                invoice_rec = self.env['account.invoice'].browse(active_inv)
                if invoice_rec.deferment_id:
                    if invoice_rec.state == 'paid':
                        invoice_rec.deferment_id.write({'state': 'pay_fees'})
        return post_id


class StudentDropRequest(models.Model):
    _name = 'student.drop.request'
    _descripation = 'Student Drop Request'
    _rec_name = 'request_code'

    @api.model
    def _get_student(self):
        user_rec = self.env['res.users'].browse(self._uid)
        student_group = self.env['ir.model.data'
                                 ].get_object('school',
                                              'group_school_student')
        groups = [grp.id for grp in user_rec.groups_id]
        if student_group.id in groups:
            student = self.env['student.student'
                               ].search([('user_id', '=', self._uid)])
            if student:
                self.write({'school_standard_id': student.standard_id.id,
                            'semester_id': student.course_year_id.id,
                            'deferment_fees': student.stand_id.deferment_fees})
                return student.id

    @api.one
    @api.depends('from_date', 'to_date')
    def _calc_duration(self):
        '''
        This method gives the duration between From and To.
        --------------------------------------------------------------------
        @param self: object pointer
        @return: Duration and checkout_date
        '''
        if self.to_date and self.from_date:
            date_I = datetime.strptime(self.to_date, '%Y-%m-%d')
            date_O = datetime.strptime(self.from_date, '%Y-%m-%d')
            rd = rdelta.relativedelta(date_O, date_I)
            self.duration = "{0.years} years and {0.months} \
                            months and {0.days} days".format(rd)

    @api.onchange('student_id')
    def onchange_student_id(self):
        if self.student_id:
            self.school_standard_id = self.student_id.standard_id.id
            self.semester_id = self.student_id.course_year_id.id
            self.deferment_fees = self.student_id.stand_id.deferment_fees

    @api.one
    @api.constrains('from_date', 'to_date')
    def check_date(self):
        if self.from_date <= self.date or self.to_date <= self.date:
            raise UserError(_('From date or To date should be more\
                            then current date'))
        date_format = "%Y-%m-%d"
        from_date = datetime.strptime(self.from_date, date_format)
        to_date = datetime.strptime(self.to_date, date_format)
        delta = to_date - from_date
        print delta.days
        if delta.days >= 365:
            raise UserError(_("You can't Deferment for 1 years"))
        if not self.Bank_teller_no and self.payment_mode == 'by_bank':
            raise UserError(_("Kindly, Enter the Bank Teller No"))

    @api.multi
    def _prepare_invoice(self):
        self.ensure_one()
        inv_obj = self.env['account.invoice']
        journal_id = inv_obj.default_get(['journal_id'])['journal_id']
        if not journal_id:
            raise UserError(_('Please define an accounting sale journal for\
            this company.'))
        account = self.student_id.partner_id.property_account_receivable_id.id
        invoice_vals = {
                        'name': ('Deferment Fees: ' +
                                 str(self.student_id.name)) or '',
                        'origin': ('Student Deferment Fees' +
                                   str(self.request_code)),
                        'account_id': account,
                        'partner_id': self.student_id.partner_id.id,
                        'journal_id': journal_id,
                        'deferment_id': self.id}
        return invoice_vals

    @api.multi
    def _prepare_invoice_line(self, invoice_id, rec):
        """
        Prepare the dict of values to create the new invoice line for a fees
        line.

        :param qty: float quantity to invoice
        """
        ir_obj = self.pool.get('ir.model.data')
        product_id = ir_obj.get_object(self._cr, self._uid, 'school',
                                       'data_fees_product')
        account = (product_id.property_account_income_id or
                   product_id.categ_id.property_account_income_categ_id)
        return {'product_id': product_id.id,
                'name': 'Deferment Fees:' + str(rec.request_code),
                'origin': rec.request_code,
                'price_unit': rec.deferment_fees,
                'quantity': 1,
                'invoice_id': invoice_id.id,
                'account_id': account.id}

    @api.multi
    def action_pay_fees(self):
        for rec in self:
            if rec.invoice_id:
                return {
                        'name': ("Deferment Fees"),
                        'view_mode': 'form',
                        'res_id': rec.invoice_id.id,
                        'view_type': 'form',
                        'res_model': 'account.invoice',
                        'type': 'ir.actions.act_window',
                        'nodestroy': True,
                        'target': 'current',
                      }
            invoice_vals = rec._prepare_invoice()
            invoice_id = self.env['account.invoice'].create(invoice_vals)
            rec.write({'invoice_id': invoice_id.id})
            invoice_line_vals = rec._prepare_invoice_line(invoice_id, rec)
            self.env['account.invoice.line'].create(invoice_line_vals)
        return {
                'name': ("Pay Fees"),
                'view_mode': 'form',
                'res_id': invoice_id.id,
                'view_type': 'form',
                'res_model': 'account.invoice',
                'type': 'ir.actions.act_window',
                'nodestroy': True,
                'target': 'current',
               }

    request_code = fields.Char('Request Code', default="New")
    student_id = fields.Many2one('student.student',
                                 'Student Name',
                                 default=_get_student)
    date = fields.Date("Date",
                       default=lambda * a: time.strftime('%Y-%m-%d'))
    school_standard_id = fields.Many2one('school.standard',
                                         "Academic Class")
    semester_id = fields.Many2one('course.years',
                                  'Level')
    from_date = fields.Date('From Date')
    to_date = fields.Date('To Date')
    reason_interruption = fields.Selection([
                            ('helth_issue', 'Health Issues'),
                            ('financial_issues', 'Financial Issues'),
                            ('security', 'Security'),
                            ('accommodation', 'Accommodation'),
                            ('domestic_problems', 'Domestic Problems')],
                             "Reason for the Interruption")
    reason = fields.Text('More Details')
    state = fields.Selection([('submit', 'Submit'),
                              ('approve', 'Approved'),
                              ('pay_fees', 'Pay Fees'),
                              ('payment_verify', 'Payment Verified'),
                              ('done', 'Done'),
                              ('cancel', 'Cancel')],
                             "State", default="submit")
    deferment_fees = fields.Float('Deferment Fees')
    payment_mode = fields.Selection([('by_physically', 'Pay By Cash'),
                                     ('by_bank', 'Pay By Bank')],
                                    "Payment Type")
    Bank_teller_no = fields.Char('Bank Teller No.')
    invoice_id = fields.Many2one('account.invoice', 'Invoice Reference')
    duration = fields.Char('Duration', size=64, compute='_calc_duration')

    @api.multi
    def action_approve(self):
        for rec in self:
            rec.write({'state': 'approve'})
        return True

    @api.multi
    def action_cancel(self):
        for rec in self:
            template_xml_id = 'school.email_temp_student_deferment_req_cancel'
            template = self.env.ref(template_xml_id, False)
            template_rec = self.env['mail.template'].browse(template.id)
            template_rec.sudo().send_mail(rec.id,
                                          force_send=True)
            rec.write({'state': 'cancel'})
        return True

    @api.model
    def create(self, vals):
        if vals.get('name', 'New') == 'New':
            seq_obj = self.env['ir.sequence']
            vals['request_code'] = seq_obj.next_by_code('student.drop.request')
        return super(StudentDropRequest, self).create(vals)

    @api.multi
    def action_done(self):
        for rec in self:
            ir_obj = self.env['ir.model.data']
            student_grp = ir_obj.get_object('school',
                                            'group_school_student')
            groups = freeze_grp = ir_obj.get_object('school',
                                                    'group_freeze_student')
            if rec.student_id.groups_id:
                groups = rec.student_id.groups_id
                groups += freeze_grp
                groups -= student_grp
            group_ids = [group.id for group in groups]
            rec.student_id.write({'groups_id': [(6, 0, group_ids)],
                                  'state': 'freeze',
                                  'action_id': ''})
            rec.write({'state': 'done'})
        return True


class StudentReadmission(models.Model):
    _name = 'student.readmission'
    _descripation = 'Student Readmission'
    _rec_name = 'student_id'

    @api.one
    @api.depends('from_date', 'to_date')
    def _calc_duration(self):
        '''
        This method gives the duration between From and To.
        --------------------------------------------------------------------
        @param self: object pointer
        @return: Duration and checkout_date
        '''
        if self.to_date and self.from_date:
            date_I = datetime.strptime(self.to_date, '%Y-%m-%d')
            date_O = datetime.strptime(self.from_date, '%Y-%m-%d')
            rd = rdelta.relativedelta(date_O, date_I)
            self.duration = "{0.years} years and {0.months} \
                            months and {0.days} days".format(rd)

    @api.model
    def _get_student(self):
        user_rec = self.env['res.users'].browse(self._uid)
        student_group = self.env['ir.model.data'
                                 ].get_object('school',
                                              'group_school_student')
        groups = [grp.id for grp in user_rec.groups_id]
        if student_group.id in groups:
            student = self.env['student.student'
                               ].search([('user_id', '=', self._uid)])
            self.write({'school_standard_id': student.standard_id.id,
                        'semester_id': student.course_year_id.id})
            if student:
                return student.id

    student_id = fields.Many2one('student.student',
                                 'Student Name',
                                 default=_get_student)
    date = fields.Date("Date",
                       default=lambda * a: time.strftime('%Y-%m-%d'))
    school_standard_id = fields.Many2one('school.standard',
                                         "Academic Class")
    semester_id = fields.Many2one('course.years',
                                  'Level')
    from_date = fields.Date('From Date')
    to_date = fields.Date('To Date')
    drop_id = fields.Many2one('student.drop.request',
                              'Drop Request Ref')
    duration = fields.Char('Duration', size=64, compute='_calc_duration')
    reason_interruption = fields.Selection([
                            ('helth_issue', 'Health Issues'),
                            ('financial_issues', 'Financial Issues'),
                            ('security', 'Security'),
                            ('accommodation', 'Accommodation'),
                            ('domestic_problems', 'Domestic Problems')],
                             "Reason for the Interruption")
    reason = fields.Text('More Details')
    additional_detail = fields.Text('Additional Details(If any)')
    state = fields.Selection([('submit', 'Submit'),
                              ('approve', 'Approved'),
                              ('done', 'Done'),
                              ('cancel', 'Cancel')],
                             "Status", default="submit")

    @api.model
    def create(self, vals):
        if vals.get('drop_id'):
            drop_id = self.env['student.drop.request'
                               ].search([('id', '=', vals.get('drop_id'))])
            vals.update({'student_id': drop_id.student_id.id,
                         'school_standard_id': drop_id.school_standard_id.id,
                         'reason_interruption': drop_id.reason_interruption,
                         'reason': drop_id.reason,
                         'to_date': drop_id.to_date,
                         'from_date': drop_id.from_date,
                         'semester_id': drop_id.semester_id.id,
                         'duration': drop_id.duration})
        return super(StudentReadmission, self).create(vals)

    @api.onchange('drop_id')
    def onchange_drop_id(self):
        if self.drop_id:
            self.reason_interruption = self.drop_id.reason_interruption
            self.reason = self.drop_id.reason
            self.to_date = self.drop_id.to_date
            self.from_date = self.drop_id.from_date
            self.student_id = self.drop_id.student_id.id
            self.school_standard_id = self.drop_id.school_standard_id.id
            self.semester_id = self.drop_id.semester_id.id
            self.duration = self.drop_id.duration

    @api.multi
    def action_approve(self):
        self.state = 'approve'

    @api.multi
    def action_cancel(self):
        self.state = 'cancel'

    @api.multi
    def action_done(self):
        for rec in self:
            ir_obj = self.env['ir.model.data']
            student_grp = ir_obj.get_object('school'
                                            'group_school_student')
            groups = freeze_grp = ir_obj.get_object('school',
                                                    'group_freeze_student')
            home_action_id = ir_obj.get_object('school',
                                               'school_dashboard_act')
            if rec.student_id.groups_id:
                groups = rec.student_id.groups_id
                groups -= freeze_grp
                groups += student_grp
            group_ids = [group.id for group in groups]
            rec.student_id.write({'groups_id': [(6, 0, group_ids)],
                                  'state': 'done',
                                  'action_id': home_action_id.id})
            rec.write({'state': 'done'})
