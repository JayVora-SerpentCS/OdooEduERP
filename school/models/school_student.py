# -*- coding: utf-8 -*-
# Part of Odoo. See LICENSE file for full copyright and licensing details.

from urlparse import urljoin
import werkzeug
import time

from datetime import date, datetime
from openerp import models, fields, api, modules
from openerp.tools.translate import _
from openerp.tools import DEFAULT_SERVER_DATE_FORMAT as SERVER_DATE_FORMAT
from openerp.tools import image_resize_image_big, image_colorize as IC
from openerp.exceptions import Warning as UserError


class StudentSubmitDocumentFiles(models.Model):
    ''' Defining a student submitted documents information '''
    _name = 'student.submit.document.files'

    name = fields.Many2one('department.need.document', 'Document Name',
                           required="1")
    file_datas = fields.Binary('Attachments')
    student_id = fields.Many2one('student.student', 'Student Ref.')
    file_name = fields.Char('File Name')
    submit = fields.Boolean('Submit')


class StudentStudent(models.Model):
    ''' Defining a student information '''
    _name = 'student.student'
    _inherit = ['mail.thread', 'ir.needaction_mixin']
    _table = "student_student"
    _description = 'Student Information'

    @api.depends('standard_id')
    def _get_group_student(self):
        ir_obj = self.env['ir.model.data']
        stu_xml_id = ir_obj.get_object('school',
                                       'group_school_student')
        grps = [group.id
                for group in self.env['res.users'].browse(self._uid).groups_id]
        if stu_xml_id.id in grps:
            self.student_bool = True

    @api.depends('standard_id')
    def _get_grp_stu_admission(self):
        ir_obj = self.env['ir.model.data']
        stu_xml_id = ir_obj.get_object('school',
                                       'group_school_student_inadmission')
        grps = [group.id
                for group in self.env['res.users'].browse(self._uid).groups_id]
        if stu_xml_id.id in grps:
            self.student_admission_bool = True

    @api.depends('date_of_birth')
    def _calc_age(self):
        self.age = 0
        if self.date_of_birth:
            start = datetime.strptime(self.date_of_birth, SERVER_DATE_FORMAT)
            end = datetime.strptime(time.strftime(SERVER_DATE_FORMAT),
                                    SERVER_DATE_FORMAT)
            self.age = ((end - start).days / 365)

    @api.multi
    def action_mail_send(self):
        '''
        This function opens a window to compose an email
        '''
        self.ensure_one()
        ir_model_data = self.env['ir.model.data']
        try:
            wiz_xml_id = 'email_compose_message_wizard_form'
            compose_form_id = ir_model_data.get_object_reference('mail',
                                                                 wiz_xml_id)[1]
        except ValueError:
            compose_form_id = False
        ctx = dict()
        ctx.update({
            'default_model': 'student.student',
            'default_res_id': self.ids[0],
            'default_composition_mode': 'comment',
            'default_partner_ids': [self.user_id.partner_id.id],
            'mark_so_as_sent': True
        })
        return {
            'type': 'ir.actions.act_window',
            'view_type': 'form',
            'view_mode': 'form',
            'res_model': 'mail.compose.message',
            'views': [(compose_form_id, 'form')],
            'view_id': compose_form_id,
            'target': 'new',
            'context': ctx,
        }

    @api.model
    def create(self, vals):
        if vals.get('pid', 'New') == 'New':
            seq_obj = self.env['ir.sequence']
            vals['pid'] = seq_obj.next_by_code('student.student') or 'New'
        if vals.get('school_id'):
            school = self.env['school.school'
                              ].search([('id', '=', vals.get('school_id'))])
            vals['cmp_id'] = school.company_id.id
            vals['company_id'] = school.company_id.id
            vals['company_ids'] = [(6, 0, [school.company_id.id])]
        if vals.get('pid', False) and vals.get('photo'):
            vals['login'] = vals['pid']
            if vals.get('email'):
                vals['login'] = vals['email']
            vals['password'] = vals['pid']
            result = super(StudentStudent,
                           self.with_context(mail_create_nolog=True
                                             )).create(vals)
        elif vals.get('pid', False) and not vals.get('origin_country'):
            vals['login'] = vals['pid']
            if vals.get('email'):
                vals['login'] = vals['email']
            vals['password'] = vals['pid']
            result = super(StudentStudent,
                           self.with_context(mail_create_nolog=True
                                             )).create(vals)
            ir_obj = self.env['ir.model.data']
            student_grp_id = ir_obj.get_object('school',
                                               'group_school_student')
            groups = student_grp_id
            if result.groups_id:
                groups = result.groups_id
                groups += student_grp_id
            group_ids = [group.id for group in groups]
            result.write({'groups_id': [(6, 0, group_ids)]})
        else:
            result = super(StudentStudent,
                           self.with_context(mail_create_nolog=True
                                             )).create(vals)
        url = self._get_accept_url(result)
        result.write({'accept_url': url})
        return result

    @api.model
    def _year(self):
        year = time.strftime('%Y')
        academic_year = self.env['academic.year'].search([])
        for a_date in academic_year:
            if a_date.date_start:
                dt = datetime.strptime(a_date.date_start, '%Y-%m-%d').year
                if dt == int(year):
                    return a_date

    @api.onchange('school_id')
    def school_change(self):
        self.write({'cmp_id': self.school_id.company_id.id})

    @api.onchange('stand_id')
    def get_stand_id(self):
        if self.stand_id:
            if self.certi_needed_ids:
                self.certi_needed_ids.unlink()
            new_lines = self.env['student.submit.document.files']
            for stand_certi in self.stand_id.certi_needed_ids:
                    data = {'name': stand_certi.name.id}
                    new_line = new_lines.new(data)
                    new_lines += new_line
            self.certi_needed_ids = new_lines

    @api.onchange('course_year_id')
    def get_semester(self):
        if self.course_year_id:
            rec_std = []
#            raise UserError(_('Kindly, Select Semester'))
#            res = self.course_year_id.subject_id.search([('department_id',
#                                                   '=', self.stand_id.id),
#                                                     ('subject_type', '=',
#                                                      'compulsory')])
            res = self.env['subject.subject'].search([('level_id', '=',
                                                       self.course_year_id.id),
                                                      ('subject_type', '=',
                                                       'compulsory')])
            std_id = self._context.get('params').get('id')
            if std_id and self.subject_ids:
                    repeat_subjects = self.env['student.exam.repeat'].\
                        search([('student_id', '=', std_id),
                                ('state', '=', 'draft')])
                    rec_std = [{'student_id': self.id,
                                'semester_id': self.course_year_id,
                                'subjects_ids': [(6, 0, res.ids)],
                                'repeat_sub_ids': [(6, 0, repeat_subjects.ids)]
                                }]
            else:
                rec_std = [{'student_id': self.id,
                            'semester_id': self.course_year_id,
                            'subjects_ids': [(6, 0, res.ids)]}]
            if self.subject_ids:
                for rec in self.subject_ids:
                    if rec.semester_id != self.course_year_id:
                        sub_obj = self.env['subject.subject']
                        if self._context.get('move_standard'):
                            year_id = self.course_year_id
                            rec_sem_id = rec_std[0].get('semester_id')
                            sem_id = rec.semester_id
                            if (sem_id != year_id and rec_sem_id != year_id):
                                res = sub_obj.search([('level_id', '=',
                                                       rec.semester_id.id),
                                                      ('subject_type', '=',
                                                       'compulsory')])
                                rec_std.append({'student_id': self.id,
                                                'semester_id': sem_id.id,
                                                'subjects_ids': [(6, 0,
                                                                  res.ids)],
                                                })
                        else:
                            res = sub_obj.search([('level_id', '=',
                                                   rec.semester_id.id),
                                                  ('subject_type', '=',
                                                   'compulsory')])
                            rec_std.append({'student_id': self.id,
                                            'semester_id': rec.semester_id.id,
                                            'subjects_ids': [(6, 0, res.ids)]})
            self.subject_ids = rec_std

    @api.model
    def _get_default_image(self, is_company, colorize=False):
        try:
            image = IC(open(modules.get_module_resource('base',
                                                        'static/src/img',
                                                        'avatar.png')).read())
            return image_resize_image_big(image.encode('base64'))
        except:
            return True

    @api.model
    def _get_photo(self):
        return self._get_default_image(self._context.get('default_is_company',
                                                         False))

    @api.model
    def _get_accept_url(self, student_id):
        """ proxy for function field towards actual implementation """

        base_url = self.env['ir.config_parameter'].get_param('web.base.url')

        # the parameters to encode for the query
        query = dict(db=self._cr.dbname)
        query['login'] = student_id.user_id.login
        query['student_id'] = student_id

        fragment = dict()

        if fragment:
            query['redirect'] = '/page#' + werkzeug.url_encode(fragment)

        return urljoin(base_url,
                       "/page/%s?%s" % ('applicationAccept',
                                        werkzeug.url_encode(query)))

    accept_url = fields.Char('URL', readonly=False)
    user_id = fields.Many2one('res.users', 'User ID',
                              delegate=True, select=True, required=True)
    student_name = fields.Char('Student Name', related='user_id.name',
                               store=True, readonly=True)
    rid = fields.Char('Student ID', required=True, default='New',
                      help='Registration IDentification Number')
    pid = fields.Char('Student ID', required=True, default='New',
                      help='Personal IDentification Number')
    student_code = fields.Char('Student Code')
    contact_phone1 = fields.Char('Phone no.')
    contact_mobile1 = fields.Char('Mobile no')
    roll_no = fields.Integer('Roll No.', readonly=True)
    fluent_language = fields.Many2one("mother.toungue", "Fluent Language")
    other_language = fields.Many2one("mother.toungue", "Other Language")
    photo = fields.Binary('Photo', default='_get_photo')
    origin_country = fields.Many2one('res.country', "Country of Origin")
    origin_state = fields.Many2one('res.country.state', 'State Of Origin')
    lga = fields.Many2one('state.lga', 'LGA')
    other_citizonship = fields.Many2one('res.country',
                                        "Other Country of Citizenship if any")
    hometown = fields.Char('Hometown')
    passport_no = fields.Char("International Passport Number")
    year = fields.Many2one('academic.year', 'Academic Year', required=True,
                           states={'done': [('readonly', True)]},
                           default=_year)
    cast_id = fields.Many2one('student.cast', 'Religion')
    admission_date = fields.Date('Admission Date', default=date.today())
    application_submit_date = fields.Date('Application Submit Date')
    middle = fields.Char('Middle Name', required=True,
                         states={'done': [('readonly', True)]})
    last = fields.Char('Surname', required=True,
                       states={'done': [('readonly', True)]})
    gender = fields.Selection([('male', 'Male'), ('female', 'Female')],
                              'Gender')
    date_of_birth = fields.Date('BirthDate', required=True,
                                states={'done': [('readonly', True)]})
    age = fields.Integer('Age', compute='_calc_age', readonly=True)
    maritual_status = fields.Selection([('single', 'Single'),
                                        ('married', 'Married'),
                                        ('widowed', 'Widowed'),
                                        ('divorced', 'Divorced'),
                                        ('seperated', 'Seperated')],
                                       'Marital Status')
    previous_school_ids = fields.One2many('student.previous.school',
                                          'previous_school_id',
                                          'Previous School Detail',
                                          states={'done': [('readonly',
                                                            True)]})
    family_con_ids = fields.One2many('student.family.contact',
                                     'family_contact_id',
                                     'Family Contact Detail')
    electives_sub_ids = fields.Many2many('subject.subject', 'electives_id',
                                         'student_id',
                                         'student_electivesub_student_rel',
                                         'Electives')
    certi_needed_ids = fields.One2many('student.submit.document.files',
                                       'student_id', 'Required Documents')
    doctor = fields.Char('Doctor Name', states={'done': [('readonly', True)]})
    designation = fields.Char('Designation')
    doctor_phone = fields.Char('Phone')
    blood_group = fields.Char('Blood Group')
    height = fields.Float('Height')
    weight = fields.Float('Weight')
    eye = fields.Boolean('Eyes')
    ear = fields.Boolean('Ears')
    nose_throat = fields.Boolean('Nose & Throat')
    respiratory = fields.Boolean('Respiratory')
    cardiovascular = fields.Boolean('Cardiovascular')
    neurological = fields.Boolean('Neurological')
    muskoskeletal = fields.Boolean('Musculoskeletal')
    dermatological = fields.Boolean('Dermatological')
    blood_pressure = fields.Boolean('Blood Pressure')
    remark = fields.Text('Rejection Remark',
                         states={'reject': [('readonly', True)]})
    school_id = fields.Many2one('school.school', 'Campus',
                                related="standard_id.school_id",
                                store=True,
                                states={'done': [('readonly', True)]})
    state = fields.Selection([('draft', 'Draft'),
                              ('submit', 'Submit'),
                              ('reject', 'Reject'),
                              ('verify', 'System Verification Done'),
                              ('registrar_verify',
                               'Verified by Admission Registrar'),
                              ('department_verify',
                               'Verified by Department Head'),
                              ('In_postutme_process',
                               'In Entrance Exam Process'),
                              ('postutme_qualified',
                               'Entrance Exam Qualified'),
                              ('verified', 'Verified'),
                              ('accepted', 'Accepted'),
                              ('slot_given', 'Slot Given'),
                              ('register_done', 'Registration Done'),
                              ('payment_done', 'Payment Details Submitted'),
                              ('payment_verify', 'Payment Verified'),
                              ('done', 'Done'),
                              ('deactivate', 'Deactivate'),
                              ('freeze', 'Freeze'),
                              ('withdraw', "Withdrawn"),
                              ('terminate', 'Terminate'),
                              ('alumni', 'Alumni')],
                             'State', readonly=True, default='draft')
    admission_fees_id = fields.Many2one("account.invoice", "Admission Fees")
    payment_mode = fields.Selection([('pay_physically', 'Pay Cash'),
                                     ('by_bank', 'Pay By Bank'),
                                     ],
                                    "Payment Mode")
    bank_teller_number = fields.Char('Bank Teller No.')
    amount = fields.Float('Amount')
    history_ids = fields.One2many('student.history', 'student_id', 'History')
    certificate_ids = fields.One2many('student.certificate', 'student_id',
                                      'Certificate')
    # document uploads
    document_ids = fields.One2many('student.documents', 'student_id',
                                   'Documents')
    description = fields.One2many('student.description', 'des_id',
                                  'Description')
    student_id = fields.Many2one('student.student', 'name')
    contact_phone = fields.Char('Phone No', related='student_id.phone')
    contact_mobile = fields.Char('Mobile No', related='student_id.mobile')
    contact_phone = fields.Char('Phone No', related='student_id.phone',
                                readonly=True)
    contact_mobile = fields.Char('Mobile No', related='student_id.mobile',
                                 readonly=True)
    contact_website = fields.Char('WebSite', related='student_id.website',
                                  readonly=True)
    award_list = fields.One2many('student.award', 'award_list_id',
                                 'Award List')
    student_status = fields.Selection('Status', related='student_id.state',
                                      help="Shows Status Of Student",
                                      readonly=True)
    stu_name = fields.Char('First Name', related='user_id.name',
                           readonly=True)
    Acadamic_year = fields.Char('Academic Year', related='year.name',
                                help='Academic Year', readonly=True)
    grn_number = fields.Many2one('student.grn', 'GR No.',
                                 help="General Register No.")
    division_id = fields.Many2one('standard.division', 'Division')
    medium_id = fields.Many2one('standard.medium', 'Medium')
    cmp_id = fields.Many2one('res.company', 'Company Name',
                             related='school_id.company_id', store=True)
    standard_id = fields.Many2one('school.standard', 'Academic Class')
    stand_id = fields.Many2one('standard.standard', 'Department')
    faculty_id = fields.Many2one('faculty.faculty', 'Faculty')
    course_year_id = fields.Many2one('course.years', 'Semester')
    teacher_id = fields.Many2one('school.teacher', 'Faculty',
                                 related="standard_id.user_id", store=True)
    student_parent_id = fields.Many2many('school.parent',
                                         'students_parents_rel',
                                         'student_id',
                                         'students_parent_id',
                                         'Parent(s)')
    alleges = fields.Boolean('Allergies')
    allergies = fields.Text("Allergy Details")
    periodic_medication = fields.Boolean('Periodic Medication')
    family_disease = fields.Boolean('Family Disease')
    family_disease_desc = fields.Text("Family Disease Details")
    student_bool = fields.Boolean('Student user', compute="_get_group_student")
    student_admission_bool = fields.Boolean('Student user',
                                            compute="_get_grp_stu_admission")
    is_criminal = fields.Boolean("Is there any criminal Record?",
                                 help="Checked if any criminal record.")
    criminal_detials = fields.Text("Details of Criminal Record")
    surgery = fields.Boolean('Surgery')
    genotype = fields.Boolean('Genotype')
    subject_ids = fields.One2many('student.subjects', 'student_id',
                                  'Student Subjects')
    # Permanent Home Address
    same_as_currnt = fields.Boolean("Is your permanent address the same as\
                                     your current address")
    street_p = fields.Char('Street')
    street2_p = fields.Char('Street details')
    zip_p = fields.Char('Zip', size=24, change_default=True)
    city_p = fields.Char('City')
    state_id_p = fields.Many2one("res.country.state", 'State',
                                 ondelete='restrict')
    country_id_p = fields.Many2one('res.country', 'Country',
                                   ondelete='restrict')
    email_p = fields.Char('Email')
    phone_p = fields.Char('Phone')

    # Programme Selection
    first_choice_id = fields.Many2one('standard.standard', 'First Choice')
    second_choice_id = fields.Many2one('standard.standard', 'Second Choice')
    third_choice_id = fields.Many2one('standard.standard', 'Third Choice')
    fourth_choice_id = fields.Many2one('standard.standard', 'Fourth Choice')
    # Referee1 Information
    referee = fields.Text('Reference Information')
    # education history
    dis_history = fields.Text('Disciplinary History')
    award_list = fields.Text('Awards List')
    progress = fields.Float(string='Admission Progress')
    final_verify_date = fields.Date("Final Verification Date")
    pass_out_score = fields.Float("Last Pass out Score")

    _sql_constraints = [('grn_unique', 'unique(grn_number)',
                         'GRN Number must be unique!')]

    @api.model
    def send_mail_common(self, template, rec_id):
        template_rec = self.env['mail.template'].browse(template.id)
        template_rec.sudo().send_mail(rec_id.student_id.id, force_send=True)
        return True

    @api.multi
    def write(self, vals):
        res_id = super(StudentStudent, self).write(vals)
        if vals.get('state') == 'reject':
            template = self.env.ref('school.email_template_student_reject',
                                    False)
            self.send_mail_common(template, self)
        if vals.get('state') in ('withdraw', 'reject'):
            reje_vals = {'name': self.name,
                         'country_id': self.origin_country.id,
                         'state_id': self.origin_state.id,
                         'lga': self.lga.id,
                         'email': self.email,
                         'middle': self.middle,
                         'last': self.last,
                         'gender': self.gender,
                         'date_of_birth': self.date_of_birth,
                         'reject_date': time.strftime('%Y-%m-%d'),
                         'withdraw_date': time.strftime('%Y-%m-%d'),
                         'reject_remark': self.remark,
                         'pid': self.pid,
                         'state': vals.get('state')}
            self.env['rejected.application'].create(reje_vals)
            user_id = self.user_id
            alias_id = user_id.alias_id
            part_id = user_id.partner_id
            user_id.unlink()
            alias_id.unlink()
            part_id.unlink()
        if vals.get('state') == 'postutme_qualified':
            template = self.env.ref('school.email_temp_stu_postutme_qualified',
                                    False)
            self.send_mail_common(template, self)
        return res_id

    @api.multi
    def unlink(self):
        """
        Overrides orm unlink method.
        @param self: The object pointer
        @return: True/False.
        """
        for records in self:
            if records.state not in ['draft', 'submit']:
                raise Warning("You can delete only Draft And Submit Student")
            if records.user_id:
                records.user_id.unlink()
        return super(StudentStudent, self).unlink()

    @api.model
    def scheduler_admission_withdrawn(self):
        student_ids = self.search([('state', '=', 'verified')])
        if student_ids:
            for student in student_ids:
                student.action_withdrawn()
        return True

    @api.model
    def scheduler_admission_registration(self):
        student_ids = self.search([('state', '=', 'accepted')])
        if student_ids:
            for student in student_ids:
                if student.document_ids:
                    if student.certi_needed_ids:
                        for doc in student.document_ids:
                            for certi in student.certi_needed_ids:
                                if doc.name.id == certi.name.id:
                                    certi.write({'file_datas': doc.file_datas})
                student.write({'state': 'slot_given'})
                email_template = 'school.email_template_student_registration'
                template = self.env.ref(email_template, False)
                self.send_mail_common(template, student)
        return True

    @api.multi
    def _department_sub_grade(self, student, choice_id):
        rem = ''
        state_chk = ''
        o_pre_obj = self.env['student.previous.school']
        deprt_sub_ids = choice_id.requirements
        if deprt_sub_ids:
            rem = 'Rejection Remark:'
            quali_name = []
            score = []
            edu_history = []
            gr = True
            score_dic = {'score': '',
                         'qualification': '',
                         'get_score': ''}
            if student.previous_school_ids:
                previous = student.previous_school_ids
                edu_history = [pre.qualification.id
                               for pre in previous]
            for o_sub in deprt_sub_ids:
                if o_sub.name.id in edu_history:
                    sub_ids = o_pre_obj.search([('qualification', '=',
                                                 o_sub.name.id),
                                                ('previous_school_id', '=',
                                                student.id)])
                    for sub in sub_ids:
                        if sub.score < o_sub.score:
                            q = sub.qualification
                            gr = False
                            score_dic.update({'qualification': q.name,
                                              'score': o_sub.score,
                                              'get_score': sub.score})
                            score.append(score_dic)
                else:
                    quali_name.append(o_sub.name.name)
                    gr = False
            if not gr:
                state_chk = 'reject'
                if quali_name:
                    rem += (str([str(q_nm) for q_nm in quali_name]) +
                            ' are a Required Qualification for ' +
                            str(choice_id.name) + ' to' +
                            ' be eligible to get an ' +
                            'Admission, but It is not in ' +
                            'your selected Qualification. '
                            )
                if score:
                    rem += (str([str(sub_nm.get("qualification"))
                                for sub_nm in score]) +
                            ' needs minimum percentage of ' +
                            str([int(sub_nm["score"])
                                 for sub_nm in score]) +
                            ' but you have ' +
                            str([int(sub_nm["get_score"])
                                 for sub_nm in score]))
                rem += ' So you does not qualifies for Admission.'
                return state_chk, rem
        documnets = choice_id.certi_needed_ids
        if documnets:
            gr = True
            document_list = []
            docu_nm = []
            do_nm = []
            if student.document_ids:
                docs = student.document_ids
                document_list = [doc.name.id
                                 for doc in docs]
            for o_doc in documnets:
                if o_doc.name.id in document_list:
                    docu_nm.append(o_doc.name.name)
                else:
                    do_nm.append(o_doc.name.name)
                    gr = False
            if not gr:
                student.write({"remark": [str(d_nm) for d_nm in do_nm]})
                template = self.env.ref('school.email_temp_student_document',
                                        False)
                template_rec = self.env['mail.template'].browse(template.id)
                template_rec.sudo().send_mail(student.student_id.id,
                                              force_send=True)
                return state_chk, rem
        return state_chk, rem

    @api.model
    def scheduler_submit_student(self):
        student_ids = self.search([('state', '=', 'submit')])
        if student_ids:
            for stu in student_ids:
                if stu.first_choice_id:
                    first_choice = stu.first_choice_id
                    fac_id1 = first_choice.faculty_id.id
                    object_re1 = self._department_sub_grade(stu,
                                                            first_choice)
                    if object_re1[0] == 'reject':
                        if stu.second_choice_id:
                            sec_choice = stu.second_choice_id
                            fac_id2 = stu.second_choice_id.faculty_id.id
                            object_re2 = self._department_sub_grade(stu,
                                                                    sec_choice)
                            if object_re2[0] == 'reject':
                                if stu.third_choice_id:
                                    fac_id3 = stu.third_choice_id.faculty_id.id
                                    chic3 = stu.third_choice_id
                                    obj_re3 = self._department_sub_grade(stu,
                                                                         chic3)
                                    if obj_re3[0] == 'reject':
                                        if stu.fourth_choice_id:
                                            sid = stu.fourth_choice_id
                                            fac_id4 = sid.faculty_id.id
                                            t = self._department_sub_grade(stu,
                                                                           sid)
                                            if t[0] == 'reject':
                                                stu.write({'state': 'reject',
                                                           'remark': t[1]})
                                                return True
                                            return stu.write(
                                                     {'state': 'verify',
                                                      'stand_id': sid.id,
                                                      'faculty_id': fac_id4,
                                                      'remark': ''})
                                        return stu.write({'state': 'reject',
                                                          'remark': obj_re3[1]
                                                          })
                                    choice3 = stu.third_choice_id.id
                                    return stu.write({'state': 'verify',
                                                      'stand_id': choice3,
                                                      'faculty_id': fac_id3,
                                                      'remark': ''})
                                return stu.write({'state': 'reject',
                                                  'remark': object_re2[1]})
                            return stu.write({'state': 'verify',
                                              'stand_id': sec_choice.id,
                                              'faculty_id': fac_id2,
                                              'remark': ''})
                        return stu.write({'state': 'reject',
                                          'remark': object_re1[1]})
                    return stu.write({'state': 'verify',
                                      'stand_id': first_choice.id,
                                      'faculty_id': fac_id1,
                                      'remark': ''})
                return stu.write({'state': 'verify',
                                  'remark': ''})

    @api.multi
    def verify_student_manually(self):
        for stu in self:
            if stu.first_choice_id:
                fac_id1 = stu.first_choice_id.faculty_id.id
                object_re1 = self._department_sub_grade(stu,
                                                        stu.first_choice_id)
                if object_re1[0] == 'reject':
                    if stu.second_choice_id:
                        fac_id2 = stu.second_choice_id.faculty_id.id
                        sec_choice = stu.second_choice_id
                        object_re2 = self._department_sub_grade(stu,
                                                                sec_choice)
                        if object_re2[0] == 'reject':
                            if stu.third_choice_id:
                                fac_id3 = stu.third_choice_id.faculty_id.id
                                ch3 = stu.third_choice_id
                                object_re3 = self._department_sub_grade(stu,
                                                                        ch3)
                                if object_re3[0] == 'reject':
                                    if stu.fourth_choice_id:
                                        sid = stu.fourth_choice_id
                                        fac_id4 = sid.faculty_id.id
                                        obre4 = self._department_sub_grade(stu,
                                                                           sid)
                                        if obre4[0] == 'reject':
                                            return stu.write(
                                                 {'state': 'reject',
                                                  'remark': obre4[1]})
                                        return stu.write(
                                                 {'state': 'verify',
                                                  'stand_id': sid.id,
                                                  'faculty_id': fac_id4,
                                                  'remark': ''})
                                    return stu.write({'state': 'reject',
                                                      'remark': object_re3[1]})
                                choi3 = stu.third_choice_id.id
                                return stu.write({'state': 'verify',
                                                  'stand_id': choi3,
                                                  'faculty_id': fac_id3,
                                                  'remark': ''})
                            return stu.write({'state': 'reject',
                                              'remark': object_re2[1]})
                        return stu.write({'state': 'verify',
                                          'stand_id': stu.second_choice_id.id,
                                          'faculty_id': fac_id2, 'remark': ''})
                    return stu.write({'state': 'reject',
                                      'remark': object_re1[1]})
                return stu.write({'state': 'verify',
                                  'stand_id': stu.first_choice_id.id,
                                  'faculty_id': fac_id1, 'remark': ''})
            return stu.write({'state': 'verify', 'remark': ''})

    @api.multi
    def set_to_draft(self):
        self.write({'state': 'draft'})
        return True

    @api.multi
    def set_alumni(self):
        self.write({'state': 'alumni'})
        return True

    @api.multi
    def set_terminate(self):
        self.write({'state': 'terminate'})
        return True

    @api.multi
    def action_reject(self):
        self.write({'state': 'reject'})
        return True

    @api.multi
    def admission_register(self):
        for certi in self.certi_needed_ids:
            if not certi.file_datas:
                raise UserError(_(str(certi.name.name) + ' is Required \
                                 certificate Submission is not\
                                 done yet! \nYou can not mark the application\
                                 as Registered before that!'))
            if not certi.submit:
                raise UserError(_(str(certi.name.name) + ' is Required \
                                 certificate Submission is not\
                                 done yet! \nYou can not mark the application\
                                 as Registered before that!'))
        self.write({'state': 'register_done'})
        email_tmplate = 'school.email_template_student_registration_done'
        template = self.env.ref(email_tmplate, False)
        self.send_mail_common(template, self)
        ir_obj = self.env['ir.model.data']
        admission_grp = ir_obj.get_object('school',
                                          'group_school_student_inadmission')
        employee_grp = ir_obj.get_object('base',
                                         'group_user')
        home_action_id = ir_obj.get_object('school',
                                           'school_dashboard_act')
        grps = [admission_grp.id, employee_grp.id]
        self.user_id.write({'groups_id': [(6, 0, grps)],
                            'action_id': home_action_id.id})
        return True

    @api.multi
    def admission_register_withdrawn(self):
        self.write({'state': 'withdraw'})
        email_template = 'school.email_template_student_registration_withdrawn'
        template = self.env.ref(email_template, False)
        self.send_mail_common(template, self)
        return True

    @api.multi
    def action_withdrawn(self):
        verify_date = datetime.strptime(self.final_verify_date,
                                        SERVER_DATE_FORMAT)
        date_today = datetime.strptime(time.strftime(SERVER_DATE_FORMAT),
                                       SERVER_DATE_FORMAT)
        if abs((verify_date - date_today).days) >= 28:
            self.write({'state': 'withdraw'})
            template = self.env.ref('school.email_template_student_withdrawn',
                                    False)
            self.send_mail_common(template, self)
        return True

    @api.multi
    def admission_registrar(self):
        progress = 25
        template = self.env.ref('school.email_temp_registrar_verify',
                                False)
        self.send_mail_common(template, self)
        return self.write({'state': 'registrar_verify', 'progress': progress})

    @api.multi
    def department_head(self):
        progress = 50
        template = self.env.ref('school.email_temp_department_verify',
                                False)
        self.send_mail_common(template, self)
        return self.write({'state': 'department_verify', 'progress': progress})

    @api.multi
    def action_varified(self):
        progress = 100
        template = self.env.ref('school.email_temp_final_registrar_verify',
                                False)
        self.send_mail_common(template, self)
        verify_dt = datetime.strptime(time.strftime(SERVER_DATE_FORMAT),
                                      SERVER_DATE_FORMAT)
        return self.write({'state': 'verified', 'progress': progress,
                           'final_verify_date': verify_dt})

    @api.multi
    def admission_draft(self):
        self.write({'state': 'draft'})
        return True

    @api.onchange('same_as_currnt')
    def change_same_as_currnt(self):
        if self.same_as_currnt:
            if self.street:
                self.street_p = self.street
            if self.street2:
                self.street2_p = self.street2
            if self.zip:
                self.zip_p = self.zip_p
            if self.city:
                self.city_p = self.city_p
            if self.state_id:
                self.state_id_p = self.state_id.id
            if self.country_id:
                self.country_id_p = self.country_id.id
            if self.email:
                self.email_p = self.email
            if self.phone:
                self.phone_p = self.phone
            if self.mobile:
                self.mobile_p = self.mobile

    @api.onchange('standard_id')
    def change_standard_id(self):
        if self.standard_id:
            self.division_id = self.standard_id.division_id.id
            self.medium_id = self.standard_id.medium_id.id

    @api.multi
    def action_payment_verify(self):
        '''
        This function returns an action that display existing invoices of
        given sales order ids. It can either be a in a list or in a form view,
        if there is only one invoice to show.
        '''
        for student in self:
            if student.admission_fees_id:
                mod_obj = self.pool.get('ir.model.data')
                act_obj = self.pool.get('ir.actions.act_window')

                result = mod_obj.get_object_reference(self._cr, self._uid,
                                                      'account',
                                                      'action_invoice_tree1')
                result_id = result and result[1] or False
                result = act_obj.read(self._cr, self._uid, [result_id])[0]

                if not student.admission_fees_id:
                    raise UserError(_('There is no payments Done/In Process\
                    till Date!'))
                # choose the view_mode accordingly
                res = mod_obj.get_object_reference(self._cr, self._uid,
                                                   'account',
                                                   'invoice_form')
                result['views'] = [(res and res[1] or False, 'form')]
                result['res_id'] = student.admission_fees_id.id or False
                return result

    @api.multi
    def admission_done(self):
        ir_obj = self.env['ir.model.data']
        for student_data in self:
            if student_data.age <= 5:
                raise UserError(_('The student is not eligible. Age is not\
                                valid.'))
            student_search_ids = self.search([('standard_id', '=',
                                               student_data.standard_id.id)])
            number = 1
            if student_search_ids:
                self.write({'roll_no': number})
                number += 1
            stu_code = self.env['ir.sequence'].get('student.code')
            student_code = (str(student_data.stand_id.code) + str('/') +
                            str(student_data.year.code) + str('/') +
                            str(stu_code))
        self.write({'state': 'done',
                    'admission_date': time.strftime('%Y-%m-%d'),
                    'student_code': student_code})
        if self.student_code:
            self.user_id.write({'login': self.student_code,
                                'password': self.student_code})
            template = self.env.ref('school.email_temp_student_admission_done',
                                    False)
            self.send_mail_common(template, self)
        admission_grp = ir_obj.get_object('school',
                                          'group_school_student_inadmission')
        home_action_id = ir_obj.get_object('school',
                                           'school_dashboard_act')
        student_grp = ir_obj.get_object('school',
                                        'group_school_student')
        user_obj = self.env['res.users']
        grps = [group.id
                for group in user_obj.browse(self.user_id.id).groups_id]
        if admission_grp.id in grps:
            grps.append(student_grp.id)
            grps.remove(admission_grp.id)
            self.user_id.write({'groups_id': [(6, 0, grps)],
                                'action_id': home_action_id.id})
        return True

    @api.multi
    def name_get(self):
        res = []
        for student_rec in self:
            name = " " + student_rec['name'] + " " + student_rec['middle'] +\
                   " " + student_rec['last']
            res.append((student_rec['id'], name))
        return res


class RejectedApplication(models.Model):
    ''' Rejected Application Information'''
    _name = 'rejected.application'

    name = fields.Char('Student Name')
    country_id = fields.Many2one('res.country', "Country of Origin")
    state_id = fields.Many2one('res.country.state', 'State Of Origin')
    lga = fields.Many2one('state.lga', 'LGA')
    email = fields.Char('Email')
    middle = fields.Char('Middle Name')
    last = fields.Char('Surname')
    gender = fields.Selection([('male', 'Male'), ('female', 'Female')],
                              'Gender')
    date_of_birth = fields.Date('BirthDate')
    reject_date = fields.Date('Rejected Date')
    reject_remark = fields.Text('Reject Remarks')
    pid = fields.Char('Student ID',
                      help='Personal IDentification Number')
    withdraw_date = fields.Date('Withdraw Date')
    state = fields.Char('state')
