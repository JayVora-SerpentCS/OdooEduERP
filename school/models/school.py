# See LICENSE file for full copyright and licensing details.

# import time
import re
import calendar
from datetime import datetime
from odoo import models, fields, api
from odoo.tools.translate import _
from odoo.tools import DEFAULT_SERVER_DATE_FORMAT
from odoo.exceptions import except_orm
from odoo.exceptions import ValidationError
from dateutil.relativedelta import relativedelta


EM = (r"[_a-z0-9-]+(\.[_a-z0-9-]+)*@[a-z0-9-]+(\.[a-z0-9-]+)*(\.[a-z]{2,4})$")


def emailvalidation(email):
    """Check valid email."""
    if email:
        email_regex = re.compile(EM)
        if not email_regex.match(email):
            raise ValidationError(_('''This seems not to be valid email.
            Please enter email in correct format!'''))
        else:
            return True


class AcademicYear(models.Model):
    '''Defines an academic year.'''

    _name = "academic.year"
    _description = "Academic Year"
    _order = "sequence"

    sequence = fields.Integer('Sequence', required=True,
                              help="Sequence order you want to see this year.")
    name = fields.Char('Name', required=True, help='Name of academic year')
    code = fields.Char('Code', required=True, help='Code of academic year')
    date_start = fields.Date('Start Date', required=True,
                             help='Starting date of academic year')
    date_stop = fields.Date('End Date', required=True,
                            help='Ending of academic year')
    month_ids = fields.One2many('academic.month', 'year_id', 'Months',
                                help="related Academic months")
    grade_id = fields.Many2one('grade.master', "Grade")
    current = fields.Boolean('Current', help="Set Active Current Year")
    description = fields.Text('Description')

    @api.model
    def next_year(self, sequence):
        '''This method assign sequence to years'''
        year_id = self.search([('sequence', '>', sequence)], order='id',
                              limit=1)
        if year_id:
            return year_id.id
        return False

    def name_get(self):
        '''Method to display name and code'''
        return [(rec.id, ' [' + rec.code + ']' + rec.name) for rec in self]

    def generate_academicmonth(self):
        """Generate academic months."""
        interval = 1
        month_obj = self.env['academic.month']
        for data in self:
            ds = data.date_start
            while ds < data.date_stop:
                de = ds + relativedelta(months=interval, days=-1)
                if de > data.date_stop:
                    de = data.date_stop
                month_obj.create({
                    'name': ds.strftime('%B'),
                    'code': ds.strftime('%m/%Y'),
                    'date_start': ds.strftime('%Y-%m-%d'),
                    'date_stop': de.strftime('%Y-%m-%d'),
                    'year_id': data.id,
                })
                ds = ds + relativedelta(months=interval)
        return True

    @api.constrains('date_start', 'date_stop')
    def _check_academic_year(self):
        '''Method to check start date should be greater than end date
           also check that dates are not overlapped with existing academic
           year'''
        new_start_date = self.date_start
        new_stop_date = self.date_stop
        delta = new_stop_date - new_start_date
        if delta.days > 365 and not calendar.isleap(new_start_date.year):
            raise ValidationError(_('''Error! The duration of the academic year
                                      is invalid.'''))
        if (self.date_stop and self.date_start and
                self.date_stop < self.date_start):
            raise ValidationError(_('''The start date of the academic year'
                                      should be less than end date.'''))
        for old_ac in self.search([('id', 'not in', self.ids)]):
            # Check start date should be less than stop date
            if (old_ac.date_start <= self.date_start <= old_ac.date_stop or
                    old_ac.date_start <= self.date_stop <= old_ac.date_stop):
                raise ValidationError(_('''Error! You cannot define overlapping
                                          academic years.'''))

    @api.constrains('current')
    def check_current_year(self):
        check_year = self.search([('current', '=', True)])
        if len(check_year.ids) >= 2:
            raise ValidationError(_('''Error! You cannot set two current \
year active!'''))


class AcademicMonth(models.Model):
    '''Defining a month of an academic year.'''

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

    _sql_constraints = [
        ('month_unique', 'unique(date_start, date_stop, year_id)',
         'Academic Month should be unique!'),
    ]

    @api.constrains('date_start', 'date_stop')
    def _check_duration(self):
        '''Method to check duration of date'''
        if (self.date_stop and self.date_start and
                self.date_stop < self.date_start):
            raise ValidationError(_(''' End of Period date should be greater
                                    than Start of Peroid Date!'''))

    @api.constrains('year_id', 'date_start', 'date_stop')
    def _check_year_limit(self):
        '''Method to check year limit'''
        if self.year_id and self.date_start and self.date_stop:
            if (self.year_id.date_stop < self.date_stop or
                    self.year_id.date_stop < self.date_start or
                    self.year_id.date_start > self.date_start or
                    self.year_id.date_start > self.date_stop):
                raise ValidationError(_('''Invalid Months ! Some months overlap
                                    or the date period is not in the scope
                                    of the academic year!'''))

    @api.constrains('date_start', 'date_stop')
    def check_months(self):
        """Check start date should be less than stop date."""
        for old_month in self.search([('id', 'not in', self.ids)]):
            if old_month.date_start <= \
                    self.date_start <= old_month.date_stop \
                    or old_month.date_start <= \
                    self.date_stop <= old_month.date_stop:
                raise ValidationError(_('''Error! You cannot define
                    overlapping months!'''))


class StandardMedium(models.Model):
    ''' Defining a medium(ENGLISH, HINDI, GUJARATI) related to standard'''

    _name = "standard.medium"
    _description = "Standard Medium"
    _order = "sequence"

    sequence = fields.Integer('Sequence', required=True)
    name = fields.Char('Name', required=True)
    code = fields.Char('Code', required=True)
    description = fields.Text('Description')


class StandardDivision(models.Model):
    '''Defining a division(A, B, C) related to standard'''

    _name = "standard.division"
    _description = "Standard Division"
    _order = "sequence"

    sequence = fields.Integer('Sequence', required=True)
    name = fields.Char('Name', required=True)
    code = fields.Char('Code', required=True)
    description = fields.Text('Description')


class StandardStandard(models.Model):
    '''Defining Standard Information.'''

    _name = 'standard.standard'
    _description = 'Standard Information'
    _order = "sequence"

    sequence = fields.Integer('Sequence', required=True)
    name = fields.Char('Name', required=True)
    code = fields.Char('Code', required=True)
    description = fields.Text('Description')

    @api.model
    def next_standard(self, sequence):
        '''This method check sequence of standard'''
        stand_ids = self.search([('sequence', '>', sequence)], order='id',
                                limit=1)
        if stand_ids:
            return stand_ids.id
        return False


class SchoolStandard(models.Model):
    '''Defining a standard related to school.'''

    _name = 'school.standard'
    _description = 'School Standards'
    _rec_name = "standard_id"

    @api.depends('standard_id', 'school_id', 'division_id', 'medium_id',
                 'school_id')
    def _compute_student(self):
        '''Compute student of done state'''
        student_obj = self.env['student.student']
        for rec in self:
            rec.student_ids = student_obj.\
                search([('standard_id', '=', rec.id),
                        ('school_id', '=', rec.school_id.id),
                        ('division_id', '=', rec.division_id.id),
                        ('medium_id', '=', rec.medium_id.id),
                        ('state', '=', 'done')])

    @api.onchange('standard_id', 'division_id')
    def onchange_combine(self):
        self.name = str(self.standard_id.name
                        ) + '-' + str(self.division_id.name)

    @api.depends('subject_ids')
    def _compute_subject(self):
        '''Method to compute subjects.'''
        for rec in self:
            rec.total_no_subjects = len(rec.subject_ids)

    @api.depends('student_ids')
    def _compute_total_student(self):
        for rec in self:
            rec.total_students = len(rec.student_ids)

    @api.depends("capacity", "total_students")
    def _compute_remain_seats(self):
        for rec in self:
            rec.remaining_seats = rec.capacity - rec.total_students

    school_id = fields.Many2one('school.school', 'School', required=True)
    standard_id = fields.Many2one('standard.standard', 'Standard',
                                  required=True)
    division_id = fields.Many2one('standard.division', 'Division',
                                  required=True)
    medium_id = fields.Many2one('standard.medium', 'Medium', required=True)
    subject_ids = fields.Many2many('subject.subject', 'subject_standards_rel',
                                   'subject_id', 'standard_id', 'Subject')
    user_id = fields.Many2one('school.teacher', 'Class Teacher')
    student_ids = fields.One2many('student.student', 'standard_id',
                                  'Student In Class',
                                  compute='_compute_student', store=True
                                  )
    color = fields.Integer('Color Index')
    cmp_id = fields.Many2one('res.company', 'Company Name',
                             related='school_id.company_id', store=True)
    syllabus_ids = fields.One2many('subject.syllabus', 'standard_id',
                                   'Syllabus')
    total_no_subjects = fields.Integer('Total No of Subject',
                                       compute="_compute_subject")
    name = fields.Char('Name')
    capacity = fields.Integer("Total Seats")
    total_students = fields.Integer("Total Students",
                                    compute="_compute_total_student",
                                    store=True)
    remaining_seats = fields.Integer("Available Seats",
                                     compute="_compute_remain_seats",
                                     store=True)
    class_room_id = fields.Many2one('class.room', 'Room Number')

    @api.constrains('standard_id', 'division_id')
    def check_standard_unique(self):
        """Method to check unique standard."""
        standard_search = self.env['school.standard'
                                   ].search([('standard_id', '=',
                                              self.standard_id.id),
                                             ('division_id', '=',
                                              self.division_id.id),
                                             ('school_id', '=',
                                              self.school_id.id),
                                             ('id', 'not in', self.ids)])
        if standard_search:
            raise ValidationError(_('''Division and class should be unique!'''
                                    ))
  
    def unlink(self):
        for rec in self:
            if rec.student_ids or rec.subject_ids or rec.syllabus_ids:
                raise ValidationError(_('''You cannot delete this standard
                because it has reference with student or subject or
                syllabus!'''))
        return super(SchoolStandard, self).unlink()

    @api.constrains('capacity')
    def check_seats(self):
        """Method to check seats."""
        if self.capacity <= 0:
            raise ValidationError(_('''Total seats should be greater than
                0!'''))

    def name_get(self):
        '''Method to display standard and division'''
        return [(rec.id, rec.standard_id.name + '[' + rec.division_id.name +
                 ']') for rec in self]


class SchoolSchool(models.Model):
    ''' Defining School Information'''

    _name = 'school.school'
    _description = 'School Information'
    _rec_name = "com_name"

    @api.model
    def _lang_get(self):
        '''Method to get language'''
        languages = self.env['res.lang'].search([])
        return [(language.code, language.name) for language in languages]

    company_id = fields.Many2one('res.company', 'Company',
                                 ondelete="cascade",
                                 required=True,
                                 delegate=True)
    com_name = fields.Char('School Name', related='company_id.name',
                           store=True)
    code = fields.Char('Code', required=True)
    standards = fields.One2many('school.standard', 'school_id',
                                'Standards')
    lang = fields.Selection(_lang_get, 'Language',
                            help='''If the selected language is loaded in the
                                system, all documents related to this partner
                                will be printed in this language.
                                If not, it will be English.''')
    required_age = fields.Integer("Student Admission Age Required", default=5)

    @api.model
    def create(self, vals):
        res = super(SchoolSchool, self).create(vals)
        main_company = self.env.ref('base.main_company')
        res.company_id.parent_id = main_company.id
        return res


class SubjectSubject(models.Model):
    '''Defining a subject '''
    _name = "subject.subject"
    _description = "Subjects"

    name = fields.Char('Name', required=True)
    code = fields.Char('Code', required=True)
    maximum_marks = fields.Integer("Maximum marks")
    minimum_marks = fields.Integer("Minimum marks")
    weightage = fields.Integer("WeightAge")
    teacher_ids = fields.Many2many('school.teacher', 'subject_teacher_rel',
                                   'subject_id', 'teacher_id', 'Teachers')
    standard_ids = fields.Many2many('standard.standard',
                                    string='Standards')
    standard_id = fields.Many2one('standard.standard', 'Class')
    is_practical = fields.Boolean('Is Practical',
                                  help='Check this if subject is practical.')
    elective_id = fields.Many2one('subject.elective')
    student_ids = fields.Many2many('student.student',
                                   'elective_subject_student_rel',
                                   'subject_id', 'student_id', 'Students')


class SubjectSyllabus(models.Model):
    '''Defining a  syllabus'''
    _name = "subject.syllabus"
    _description = "Syllabus"
    _rec_name = "subject_id"

    standard_id = fields.Many2one('school.standard', 'Standard')
    subject_id = fields.Many2one('subject.subject', 'Subject')
    syllabus_doc = fields.Binary("Syllabus Doc",
                                 help="Attach syllabus related to Subject")


class SubjectElective(models.Model):
    ''' Defining Subject Elective '''
    _name = 'subject.elective'
    _description = "Elective Subject"

    name = fields.Char("Name")
    subject_ids = fields.One2many('subject.subject', 'elective_id',
                                  'Elective Subjects')


class MotherTongue(models.Model):
    """Defining mother tongue."""

    _name = 'mother.toungue'
    _description = "Mother Toungue"

    name = fields.Char("Mother Tongue")


class StudentAward(models.Model):
    """Defining student award."""

    _name = 'student.award'
    _description = "Student Awards"

    award_list_id = fields.Many2one('student.student', 'Student')
    name = fields.Char('Award Name')
    description = fields.Char('Description')


class AttendanceType(models.Model):
    """Defining attendance type."""

    _name = "attendance.type"
    _description = "School Type"

    name = fields.Char('Name', required=True)
    code = fields.Char('Code', required=True)


class StudentDocument(models.Model):
    """Defining Student document."""
    _name = 'student.document'
    _description = "Student Document"
    _rec_name = "doc_type"

    doc_id = fields.Many2one('student.student', 'Student')
    file_no = fields.Char('File No', readonly="1", default=lambda obj:
                          obj.env['ir.sequence'].
                          next_by_code('student.document'))
    submited_date = fields.Date('Submitted Date')
    doc_type = fields.Many2one('document.type', 'Document Type', required=True)
    file_name = fields.Char('File Name',)
    return_date = fields.Date('Return Date')
    new_datas = fields.Binary('Attachments')


class DocumentType(models.Model):
    ''' Defining a Document Type(SSC,Leaving)'''
    _name = "document.type"
    _description = "Document Type"
    _rec_name = "doc_type"
    _order = "seq_no"

    seq_no = fields.Char('Sequence', readonly=True,
                         default=lambda self: _('New'))
    doc_type = fields.Char('Document Type', required=True)

    @api.model
    def create(self, vals):
        if vals.get('seq_no', _('New')) == _('New'):
            vals['seq_no'] = self.env['ir.sequence'
                                      ].next_by_code('document.type'
                                                     ) or _('New')
        return super(DocumentType, self).create(vals)


class StudentDescription(models.Model):
    ''' Defining a Student Description'''
    _name = 'student.description'
    _description = "Student Description"

    des_id = fields.Many2one('student.student', 'Student Ref.')
    name = fields.Char('Name')
    description = fields.Char('Description')


class StudentDescipline(models.Model):
    """Definign student dscipline."""

    _name = 'student.descipline'
    _description = "Student Discipline"

    student_id = fields.Many2one('student.student', 'Student')
    teacher_id = fields.Many2one('school.teacher', 'Teacher')
    date = fields.Date('Date')
    class_id = fields.Many2one('standard.standard', 'Class')
    note = fields.Text('Note')
    action_taken = fields.Text('Action Taken')


class StudentHistory(models.Model):
    """Defining Student History."""

    _name = "student.history"
    _description = "Student History"

    student_id = fields.Many2one('student.student', 'Student')
    academice_year_id = fields.Many2one('academic.year', 'Academic Year',
                                        )
    standard_id = fields.Many2one('school.standard', 'Standard')
    percentage = fields.Float("Percentage", readonly=True)
    result = fields.Char('Result', readonly=True)


class StudentCertificate(models.Model):
    """Defining student certificate."""

    _name = "student.certificate"
    _description = "Student Certificate"

    student_id = fields.Many2one('student.student', 'Student')
    description = fields.Char('Description')
    certi = fields.Binary('Certificate', required=True)


class StudentReference(models.Model):
    ''' Defining a student reference information '''

    _name = "student.reference"
    _description = "Student Reference"

    reference_id = fields.Many2one('student.student', 'Student')
    name = fields.Char('First Name', required=True)
    middle = fields.Char('Middle Name', required=True)
    last = fields.Char('Surname', required=True)
    designation = fields.Char('Designation', required=True)
    phone = fields.Char('Phone', required=True)
    gender = fields.Selection([('male', 'Male'), ('female', 'Female')],
                              'Gender')


class StudentPreviousSchool(models.Model):
    ''' Defining a student previous school information '''
    _name = "student.previous.school"
    _description = "Student Previous School"

    previous_school_id = fields.Many2one('student.student', 'Student')
    name = fields.Char('Name', required=True)
    registration_no = fields.Char('Registration No.', required=True)
    admission_date = fields.Date('Admission Date')
    exit_date = fields.Date('Exit Date')
    course_id = fields.Many2one('standard.standard', 'Course', required=True)
    add_sub = fields.One2many('academic.subject', 'add_sub_id', 'Add Subjects')

    @api.constrains('admission_date', 'exit_date')
    def check_date(self):
        curr_dt = datetime.now()
        new_dt = datetime.strftime(curr_dt,
                                   DEFAULT_SERVER_DATE_FORMAT)
        if self.admission_date >= new_dt or self.exit_date >= new_dt:
            raise ValidationError(_('''Your admission date and exit date
            should be less than current date in previous school details!'''))
        if self.admission_date > self.exit_date:
            raise ValidationError(_(''' Admission date should be less than
            exit date in previous school!'''))


class AcademicSubject(models.Model):
    ''' Defining a student previous school information '''
    _name = "academic.subject"
    _description = "Student Previous School"

    add_sub_id = fields.Many2one('student.previous.school', 'Add Subjects',
                                 invisible=True)
    name = fields.Char('Name', required=True)
    maximum_marks = fields.Integer("Maximum marks")
    minimum_marks = fields.Integer("Minimum marks")


class StudentFamilyContact(models.Model):
    ''' Defining a student emergency contact information '''
    _name = "student.family.contact"
    _description = "Student Family Contact"

    @api.depends('relation', 'stu_name')
    def _compute_get_name(self):
        for rec in self:
            if rec.stu_name:
                rec.relative_name = rec.stu_name.name
            else:
                rec.relative_name = rec.name

    family_contact_id = fields.Many2one('student.student', 'Student Ref.')
    rel_name = fields.Selection([('exist', 'Link to Existing Student'),
                                 ('new', 'Create New Relative Name')],
                                'Related Student', help="Select Name",
                                required=True)
    user_id = fields.Many2one('res.users', 'User ID', ondelete="cascade")
    stu_name = fields.Many2one('student.student', 'Existing Student',
                               help="Select Student From Existing List")
    name = fields.Char('Relative Name')
    relation = fields.Many2one('student.relation.master', 'Relation',
                               required=True)
    phone = fields.Char('Phone', required=True)
    email = fields.Char('E-Mail')
    relative_name = fields.Char(compute='_compute_get_name', string='Name')


class StudentRelationMaster(models.Model):
    ''' Student Relation Information '''
    _name = "student.relation.master"
    _description = "Student Relation Master"

    name = fields.Char('Name', required=True, help="Enter Relation name")
    seq_no = fields.Integer('Sequence')


class GradeMaster(models.Model):
    """Defining grade master."""

    _name = 'grade.master'
    _description = "Grade Master"

    name = fields.Char('Grade', required=True)
    grade_ids = fields.One2many('grade.line', 'grade_id', 'Grade Lines')


class GradeLine(models.Model):
    """Defining grade line."""

    _name = 'grade.line'
    _description = "Grades"
    _rec_name = 'grade'

    from_mark = fields.Integer('From Marks', required=True,
                               help='The grade will starts from this marks.')
    to_mark = fields.Integer('To Marks', required=True,
                             help='The grade will ends to this marks.')
    grade = fields.Char('Grade', required=True, help="Grade")
    sequence = fields.Integer('Sequence', help="Sequence order of the grade.")
    fail = fields.Boolean('Fail', help='If fail field is set to True,\
                                  it will allow you to set the grade as fail.')
    grade_id = fields.Many2one("grade.master", 'Grade Ref.')
    name = fields.Char('Name')


class StudentNews(models.Model):
    """Defining studen news."""

    _name = 'student.news'
    _description = 'Student News'
    _rec_name = 'subject'
    _order = 'date asc'

    subject = fields.Char('Subject', required=True,
                          help='Subject of the news.')
    description = fields.Text('Description', help="Description")
    date = fields.Datetime('Expiry Date', help='Expiry date of the news.')
    user_ids = fields.Many2many('res.users', 'user_news_rel', 'id', 'user_ids',
                                'User News',
                                help='Name to whom this news is related.')
    color = fields.Integer('Color Index', default=0)

    @api.constrains("date")
    def checknews_dates(self):
        """Check news date."""
        new_date = datetime.now()
        if self.date < new_date:
            raise ValidationError(_('''Configure expiry date greater than \
current date!'''))

    def news_update(self):
        '''Method to send email to student for news update'''
        emp_obj = self.env['hr.employee']
        obj_mail_server = self.env['ir.mail_server']
        user = self.env['res.users'].browse(self._context.get('uid'))
        # Check if out going mail configured
        mail_server_ids = obj_mail_server.search([])
        if not mail_server_ids:
            raise except_orm(_('Mail Error'),
                             _('''No mail outgoing mail server \
specified!'''))
        mail_server_record = mail_server_ids[0]
        email_list = []
        # Check email is defined in student
        for news in self:
            if news.user_ids and news.date:
                email_list = [news_user.email for news_user in news.user_ids
                              if news_user.email]
                if not email_list:
                    raise except_orm(_('User Email Configuration!'),
                                     _("Email not found in users !"))
            # Check email is defined in user created from employee
            else:
                for employee in emp_obj.search([]):
                    if employee.work_email:
                        email_list.append(employee.work_email)
                    elif employee.user_id and employee.user_id.email:
                        email_list.append(employee.user_id.email)
                if not email_list:
                    raise except_orm(_('Email Configuration!'),
                                     _("Email not defined!"))
            news_date = news.date
            # Add company name while sending email
            company = user.company_id.name or ''
            body = """Hi,<br/><br/>
                    This is a news update from <b>%s</b> posted at %s<br/>
                    <br/> %s <br/><br/>
                    Thank you.""" % (company,
                                     news_date.strftime('%d-%m-%Y %H:%M:%S'),
                                     news.description or '')
            smtp_user = mail_server_record.smtp_user or False
            # Check if mail of outgoing server configured
            if not smtp_user:
                raise except_orm(_('Email Configuration '),
                                 _("Kindly,Configure Outgoing Mail Server!"))
            notification = 'Notification for news update.'
            # Configure email
            message = obj_mail_server.build_email(email_from=smtp_user,
                                                  email_to=email_list,
                                                  subject=notification,
                                                  body=body,
                                                  body_alternative=body,
                                                  reply_to=smtp_user,
                                                  subtype='html')
            # Send Email configured above with help of send mail method
            obj_mail_server.send_email(message=message,
                                       mail_server_id=mail_server_ids[0].id)
        return True


class StudentReminder(models.Model):
    """Defining student reminder."""

    _name = 'student.reminder'
    _description = "Student Reminder"

    @api.model
    def check_user(self):
        '''Method to get default value of logged in Student'''
        return self.env['student.student'].search([('user_id', '=',
                                                    self._uid)]).id

    stu_id = fields.Many2one('student.student', 'Student Name', required=True,
                             default=check_user)
    name = fields.Char('Title')
    date = fields.Date('Date')
    description = fields.Text('Description')
    color = fields.Integer('Color Index', default=0)


class StudentCast(models.Model):
    """Defining student cast."""

    _name = "student.cast"
    _description = "Student Cast"

    name = fields.Char("Name", required=True)


class ClassRoom(models.Model):
    """Defining class room."""

    _name = "class.room"
    _description = "Class Room"

    name = fields.Char("Name")
    number = fields.Char("Room Number")


class Report(models.Model):
    _inherit = "ir.actions.report"

    def render_template(self, template, values=None):
        student_id = self.env['student.student'].\
            browse(self._context.get('student_id', False))
        if student_id and student_id.state == 'draft':
            raise ValidationError(_('''You cannot print report for
                student in unconfirm state!'''))
        return super(Report, self).render_template(template, values)
