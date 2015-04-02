# -*- encoding: utf-8 -*-
##############################################################################
#
#    OpenERP, Open Source Management Solution
#    Copyright (C) 2004-2009 Tiny SPRL (<http://tiny.be>).
#    Copyright (C) 2011-2012 Serpent Consulting Services (<http://www.serpentcs.com>)
#    Copyright (C) 2013-2014 Serpent Consulting Services (<http://www.serpentcs.com>)
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
from openerp import models, fields, api, _
import time
import openerp
from datetime import datetime
from openerp.tools.translate import _
from openerp.tools import DEFAULT_SERVER_DATE_FORMAT, DEFAULT_SERVER_DATETIME_FORMAT, image_colorize, image_resize_image_big
from openerp.exceptions import except_orm, Warning, RedirectWarning

class academic_year(models.Model):
    ''' Defining an academic year '''
    
    _name = "academic.year"
    _description = "Academic Year"
    _order = "sequence"
    
    sequence = fields.Integer('Sequence', required=True, help="In which sequence order you want to see this year.")
    name = fields.Char('Name', size=64, required=True, select=1,help='Name of  academic year')
    code = fields.Char('Code', size=6, required=True, select=1,help='Code of academic year')
    date_start = fields.Date('Start Date', required=True,help='Starting date of academic year')
    date_stop = fields.Date('End Date', required=True,help='Ending of academic year')
    month_ids = fields.One2many('academic.month', 'year_id', string='Months',help="related Academic months")
    grade_id = fields.Many2one('grade.master',"Grade")
    description = fields.Text('Description')

    @api.model
    def next_year(self, sequence):
        year_ids = self.search([('sequence', '>', sequence)])
        if year_ids.id:
            return year_ids[0].id
        return False
    
#    def name_get(self, cr, uid, ids, context=None):
#        res = []
#        for acd_year_rec in self.browse(cr, uid, ids, context=context):
#            nam = "[" + acd_year_rec['code'] + "]" + acd_year_rec['name']
#            res.append((acd_year_rec['id'], nam))
#        return res
    
    @api.multi
    def name_get(self):
        res = []
        for acd_year_rec in self:
#            print '===acd_year_rec', acd_year_rec, acd_year_rec['name'], acd_year_rec['code']
            name = "[" + acd_year_rec['code'] + "]" + acd_year_rec['name']
            res.append((acd_year_rec['id'], name))
        return res

#    def _check_academic_year(self, cr, uid, ids, context=None):
#        obj_academic_ids = self.search(cr, uid, [], context=context)
#        for current_academic_yr in self.browse(cr, uid, ids, context=context):
#            obj_academic_ids.remove(current_academic_yr.id)
#            data_academic_yr = self.browse(cr, uid, obj_academic_ids, context=context)
#            for old_ac in data_academic_yr:
#                if old_ac.date_start <= current_academic_yr.date_start <= old_ac.date_stop or \
#                    old_ac.date_start <= current_academic_yr.date_stop <= old_ac.date_stop:
#                    return False
#        return True
    
    @api.constrains('date_start','date_stop')
    def _check_academic_year(self):
        obj_academic_ids = self.search([])
        print '=======[] search', obj_academic_ids
        academic_list = []
        for rec_academic_id in obj_academic_ids:
            print '====rec_academic_id', rec_academic_id
            academic_list.append(rec_academic_id.id)
        academic_list.remove()
        data_academic_yr = obj_academic_ids
        for old_ac in data_academic_yr:
            if old_ac.date_start <= self.date_start <= old_ac.date_stop or \
                old_ac.date_start <= self.date_stop <= old_ac.date_stop:
                raise Warning(_('Error! You cannot define overlapping academic years.'))

#    @api.constrains('date_start','date_stop')
#    def _check_duration(self):
#        if self.date_stop and self.date_start and self.date_stop < self.date_start:
#            raise Warning(_('Error! The duration of the academic year is invalid.'))

#    _constraints = [
#        (_check_academic_year, _('Error! You cannot define overlapping academic years'), ['date_start', 'date_stop'])
#    ]


class academic_month(models.Model):
    ''' Defining a month of an academic year '''
    _name = "academic.month"
    _description = "Academic Month"
    _order = "date_start"
    
    name =          fields.Char('Name', size=64, required=True, help='Name of Academic month')
    code =          fields.Char('Code', size=12, required=True, help='Code of Academic month')
    date_start =    fields.Date('Start of Period', required=True, help='Starting of Academic month')
    date_stop =     fields.Date('End of Period', required=True,help='Ending of Academic month')
    year_id =       fields.Many2one('academic.year', 'Academic Year', required=True, help="Related Academic year ")
    description=    fields.Text('Description')

#    def _check_duration(self, cr, uid, ids, context=None):
#        for obj_month in self.browse(cr, uid, ids, context=context):
#            if obj_month.date_stop < obj_month.date_start:
#                return False
#        return True

    @api.constrains('date_start','date_stop')
    def _check_duration(self):
        if self.date_stop and self.date_start and self.date_stop < self.date_start:
            raise Warning(_('Error ! The duration of the Month(s) is/are invalid.'))

#    def _check_year_limit(self,cr,uid,ids,context=None):
#        for obj_month in self.browse(cr, uid, ids, context=context):
#            if obj_month.year_id.date_stop < obj_month.date_stop or \
#               obj_month.year_id.date_stop < obj_month.date_start or \
#               obj_month.year_id.date_start > obj_month.date_start or \
#               obj_month.year_id.date_start > obj_month.date_stop:
#                return False
#        return True
    
    @api.constrains('year_id','date_start','date_stop')
    def _check_year_limit(self):
        if self.year_id and self.date_start and self.date_stop:
            if self.year_id.date_stop < self.date_stop or \
                self.year_id.date_stop < self.date_start or \
                self.year_id.date_start > self.date_start or \
                self.year_id.date_start > self.date_stop:
                raise Warning(_('Invalid Months ! Some months overlap or the date period is not in the scope of the academic year.'))

#    _constraints = [
#        (_check_duration, _('Error ! The duration of the Month(s) is/are invalid.'), ['date_stop']),
#        (_check_year_limit, _('Invalid Months ! Some months overlap or the date period is not in the scope of the academic year.'), ['date_stop'])
#    ]

class standard_medium(models.Model):
    ''' Defining a medium(English, Hindi, Gujarati) related to standard'''
    _name = "standard.medium"
    _description = "Standard Medium"
    _order = "sequence"
    
    sequence =      fields.Integer('Sequence', required=True)
    name =          fields.Char('Name', size=64, required=True)
    code =          fields.Char('Code', size=12, required=True)
    description =   fields.Text('Description')


class standard_division(models.Model):
    ''' Defining a division(A, B, C) related to standard'''
    _name = "standard.division"
    _description = "Standard Division"
    _order = "sequence"
    
    sequence =      fields.Integer('Sequence', required=True)
    name =          fields.Char('Name', size=64, required=True)
    code =          fields.Char('Code', size=12, required=True)
    description =   fields.Text('Description')


class standard_standard(models.Model):
    ''' Defining Standard Information '''
    _name = 'standard.standard'
    _description ='Standard Information'
    _order = "sequence"
    
    sequence =      fields.Integer('Sequence', required=True)
    name =          fields.Char('Name', size=64, required=True)
    code =          fields.Char('Code', size=20, required=True)
    description =   fields.Text('Description')

#    def next_standard(self, cr, uid, sequence, context=None):
#        stand_ids = self.search(cr, uid, [('sequence', '>', sequence)])
#        if stand_ids:
#            return stand_ids[0]
#        return False

    @api.model
    def next_standard(self, sequence):
        stand_ids = self.search([('sequence', '>', sequence)])
        if stand_ids.id:
            return stand_ids[0].id
        return False


class school_standard(models.Model):
    ''' Defining a standard related to school '''
    _name = 'school.standard'
    _description ='School Standards'
    _rec_name ="school_id"

#    def _compute_student(self, cr, uid, ids, name, args, context=None):
#        ''' This function will automatically computes the students related to particular standard.'''
#        result = {}
#        student_obj = self.pool.get('student.student')
#        for standard_data in self.browse(cr, uid, ids, context=context):
#            student_ids = student_obj.search(cr, uid,[('standard_id', '=', standard_data.standard_id.id)], context=context)
#            result[standard_data.id] = student_ids
#        return result

    @api.one
    def _compute_student(self):
        result = {}
        student_obj = self.env['student.student']
        for standard_data in self:
            student_ids = student_obj.search([('standard_id', '=', standard_data.standard_id.id)])
            result[standard_data.id] = student_ids
        return result
    
#    def import_subject(self, cr, uid, ids,context=None):
#        ''' This function will automatically placed previous standard subject'''
#        import_rec = self.browse(cr, uid, ids, context=context)
#        for im_ob in import_rec:
#            import_sub_id = self.search(cr, uid,[('standard_id', '=', int(im_ob.standard_id)-1)])
#            val = []
#            for import_sub_obj in self.browse(cr, uid, import_sub_id, context=context):
#                for last in import_sub_obj.subject_ids: 
#                    val.append(last.id)
#                    self.write(cr, uid, ids, {'subject_ids': [(6, 0, val)]}, context=context)
#        return True

    @api.multi
    def import_subject(self):
        import_rec = self.browse(self.ids)
        for im_ob in import_rec:
            import_sub_id = self.search([('standard_id', '=', int(im_ob.standard_id)-1)])
            val = []
            for import_sub_obj in self.browse(import_sub_id):
                for last in import_sub_obj.subject_ids: 
                    val.append(last.id)
                    self.write({'subject_ids': [(6, 0, val)]})
        return True

    school_id =     fields.Many2one('school.school', 'School', required=True)
    standard_id =   fields.Many2one('standard.standard', 'Class', required=True)
    division_id =   fields.Many2one('standard.division', 'Division', required=True)
    medium_id =     fields.Many2one('standard.medium', 'Medium', required=True)
    subject_ids =   fields.Many2many('subject.subject', 'subject_standards_rel', 'subject_id', 'standard_id', 'Subject')
    user_id =       fields.Many2one('hr.employee', string='Class Teacher')
#    student_ids =   fields.function(_compute_student, method=True, relation='student.student', type="one2many", string='Student In Class')
    student_ids =   fields.One2many('student.student',compute='_compute_student',string='Student In Class')
    color =         fields.Integer('Color Index')
    passing =       fields.Integer('No Of ATKT', help="Allowed No of ATKTs")
#    cmp_id =        fields.related('school_id','company_id',relation="res.company", string="Company Name", type="many2one", store=True)
    cmp_id =        fields.Many2one('res.company',related='school_id.company_id',string="Company Name", store=True)

#    def name_get(self, cr, uid, ids, context=None):
#        res = []
#        for standard in self.browse(cr, uid, ids, context=context):
#            nam = standard.standard_id.name+"[" + standard.division_id.name + "]" 
#            res.append((standard.id,nam))
#        return res

    @api.multi
    def name_get(self):
        res = []
        for standard in self:
            name = standard.standard_id.name+"[" + standard.division_id.name + "]" 
            res.append((standard.id,name))
        return res

class school_school(models.Model):
    ''' Defining School Information '''
    _name = 'school.school'
    _inherits = {'res.company': 'company_id'}
    _description ='School Information'
    _rec_name="com_name"
    
#    def _lang_get(self, cr, uid, context=None):
#        lang_pool = self.pool.get('res.lang')
#        ids = lang_pool.search(cr, uid, [], context=context)
#        res = lang_pool.read(cr, uid, ids, ['code', 'name'], context)
#        return [(r['code'], r['name']) for r in res] + [('','')]
    
    @api.model
    def _lang_get(self):
        res_lan_obj = self.env['res.lang']
        ids = res_lan_obj.search([])
        res = res_lan_obj.read(['code', 'name'])
        return [(r['code'], r['name']) for r in res] + [('','')]
    
    company_id = fields.Many2one('res.company', 'Company',ondelete="cascade", required=True)
#    com_name =   fields.related('company_id','name',string="School Name",size=128,store=True,type="char")
    com_name =   fields.Char(related='company_id.name',string="School Name",size=128,store=True)
    code =       fields.Char('Code', size=20, required=True, select=1)
    standards =  fields.One2many('school.standard', 'school_id',string='Standards')
    lang =       fields.Selection('_lang_get', string='Language',help="If the selected language is loaded in the system, all documents related to this partner will be printed in this language. If not, it will be english.")


class subject_subject(models.Model):
    '''Defining a subject '''
    _name = "subject.subject"
    _description = "Subjects"
    
    name =          fields.Char('Name', size=64, required=True)
    code =          fields.Char('Code', size=12, required=True)
    maximum_marks = fields.Integer("Maximum marks", size=5)
    minimum_marks = fields.Integer("Minimum marks", size=5)
    weightage =     fields.Integer("Weightage", size=10)
    teacher_ids =   fields.Many2many('hr.employee','subject_teacher_rel','subject_id','teacher_id','Teachers')
    standard_ids =  fields.Many2many('school.standard','subject_standards_rel','standard_id','subject_id','Standards')
    standard_id =   fields.Many2one('standard.standard', 'Class')
    is_practical =  fields.Boolean('Is Practical',help='Check this if subject is practical.')
    no_exam =       fields.Boolean("No Exam",help='Check this if subject has no exam.')
    elective_id =   fields.Many2one('subject.elective')
    student_ids =   fields.Many2many('student.student','elective_subject_student_rel','subject_id','student_id','Students')
    syllabus_ids =  fields.One2many('subject.syllabus','subject_id',string='Syllabus')


class subject_syllabus(models.Model):
    '''Defining a  syllabus'''
    _name= "subject.syllabus"
    _description = "Syllabus"
    _rec_name = "duration"
    
    subject_id = fields.Many2one('subject.subject', 'Subject')
    duration =   fields.Char("Duration")
    topic =      fields.Text("Topic")


class subject_elective(models.Model):
    ''' Defining Subject Elective '''
    _name = 'subject.elective'
    
    name =          fields.Char("Name",size=32)
    subject_ids =   fields.One2many('subject.subject','elective_id',string='Elective Subjects')


class student_student(models.Model):
    ''' Defining a student information '''
    _name = 'student.student'
    _table = "student_student"
    _description = 'Student Information'
    _inherits = {'res.users': 'user_id'}

#    def _calc_age(self, cr, uid, ids, name, arg, context=None):
#        ''' This function will automatically calculates the age of particular student.'''
#        res= {}
#        for student in self.browse(cr, uid, ids, context=context):
#            start = datetime.strptime(student.date_of_birth, DEFAULT_SERVER_DATE_FORMAT)
#            end = datetime.strptime(time.strftime(DEFAULT_SERVER_DATE_FORMAT),DEFAULT_SERVER_DATE_FORMAT)
#            delta = end - start
#            years =  (delta.days / 365)
#            res[student.id] = years
#        return res
    
    @api.one
    @api.depends('date_of_birth')
    def _calc_age(self):
        if self.date_of_birth:
            start = datetime.strptime(self.date_of_birth, DEFAULT_SERVER_DATE_FORMAT)
            end = datetime.strptime(time.strftime(DEFAULT_SERVER_DATE_FORMAT),DEFAULT_SERVER_DATE_FORMAT)
            delta = end - start
            years =  (delta.days / 365)
            self.age = years
        else:
            self.age = 0
    
#    def create(self, cr, uid, data, context={}):
#        if data.get('pid',False):
#            data['login']= data['pid']
#            data['password']= data['pid']
#        else:
#            raise osv.except_osv(_('Error!'), _('PID not valid, so record will not save.'))
#        result = super(student_student, self).create(cr, uid, data, context=context)
#        return result

    @api.model
    def create(self, vals):
        print '=================vals', vals
        if vals.get('pid',False):
            vals['login']= vals['pid']
            vals['password']= vals['pid']
        else:
            raise except_orm(_('Error!'), _('PID not valid, so record will not save.'))
        result = super(student_student, self).create(vals)
        return result
    
    user_id =           fields.Many2one('res.users', string='User ID', ondelete="cascade", select=True, required=True)
#    student_name =      fields.related('user_id', 'name',type='char', size=64, store=True, readonly=True)
    student_name =      fields.Char(related='user_id.name',string='Name', size=64, store=True, readonly=True)
    pid =               fields.Char('Student ID', size=64, required=True, default=lambda obj:obj.env['ir.sequence'].get('student.student'), help='Personal IDentification Number')
    reg_code =          fields.Char('Registration Code', size=64, required=True,help='Student Registration Code')
    student_code =      fields.Char('Student Code', size=64, required=True)
    contact_phone1 =    fields.Char('Phone no.',size=20)
    contact_mobile1 =   fields.Char('Mobile no',size=20)
    roll_no =           fields.Integer('Roll No.',readonly=True)
    photo =             fields.Binary('Photo',)
#    default=lambda self: self._get_default_image(self._context.get('default_is_company', False))
    year =              fields.Many2one('academic.year', 'Academic Year', required=True, states={'done':[('readonly',True)]})
    cast_id =           fields.Many2one('student.cast','Religion')
    admission_date =    fields.Date('Admission Date', default=fields.datetime.now)
    middle =            fields.Char('Middle Name', size=64, required=True, states={'done':[('readonly',True)]})
    last =              fields.Char('Surname', size=64, required=True, states={'done':[('readonly',True)]})
    gender =            fields.Selection([('male','Male'), 
                                          ('female','Female')], 
                                         'Gender', states={'done':[('readonly',True)]})
    date_of_birth =     fields.Date('Birthdate', required=True, states={'done':[('readonly',True)]})
    mother_tongue =     fields.Many2one('mother.toungue',"Mother Tongue")
    age =               fields.Integer(compute='_calc_age', string='Age', readonly=True)
    maritual_status =   fields.Selection([('unmarried','Unmarried'), 
                                          ('married','Married')], 
                                         'Maritual Status', states={'done':[('readonly',True)]})
    reference_ids =     fields.One2many('student.reference', 'reference_id', string='References', states={'done':[('readonly',True)]})
    previous_school_ids=fields.One2many('student.previous.school', 'previous_school_id', string='Previous School Detail', states={'done':[('readonly',True)]})
    family_con_ids =    fields.One2many('student.family.contact', 'family_contact_id', string='Family Contact Detail', states={'done':[('readonly',True)]})
    doctor =            fields.Char('Doctor Name', size=64, states={'done':[('readonly',True)]} )
    designation =       fields.Char('Designation', size=64)
    doctor_phone =      fields.Char('Phone', size=12)
    blood_group =       fields.Char('Blood Group', size=12)
    height =            fields.Float('Height')
    weight =            fields.Float('Weight')
    eye =               fields.Boolean('Eyes')
    ear =               fields.Boolean('Ears')
    nose_throat =       fields.Boolean('Nose & Throat')
    respiratory =       fields.Boolean('Respiratory')
    cardiovascular =    fields.Boolean('Cardiovascular')
    neurological =      fields.Boolean('Neurological')
    muskoskeletal =     fields.Boolean('Musculoskeletal')
    dermatological =    fields.Boolean('Dermatological')
    blood_pressure =    fields.Boolean('Blood Pressure')
    remark =            fields.Text('Remark', states={'done':[('readonly',True)]})
    school_id =         fields.Many2one('school.school', 'School', states={'done':[('readonly',True)]})
    state =             fields.Selection([('draft','Draft'),
                                          ('done','Done'),
                                          ('terminate','Terminate'),
                                          ('alumni','Alumni')],'State',readonly=True, default='draft')
    history_ids =       fields.One2many('student.history', 'student_id', string='History')
    certificate_ids =   fields.One2many('student.certificate','student_id',string='Certificate')
 #   'attendance_ids' : fields.one2many('attendance.sheet.line','name','Attendance History',readonly=True)
 #   'exam_results_ids' : fields.one2many('exam.result','student_id','Exam History',readonly=True)
#    'student_attachment_line' : fields.one2many('student.attachment','student_id','Attachment')
    student_discipline_line=fields.One2many('student.descipline','student_id',string='Descipline')
    address_ids =           fields.One2many('res.partner','student_id',string='Contacts')
    document =              fields.One2many('student.document','doc_id',string='Documents')
    description =           fields.One2many('student.description','des_id',string='Description')
    student_id =            fields.Many2one('student.student','name')
#    contact_phone =         fields.related('student_id','phone',type='char',relation='student.student',string='Phone No')
    contact_phone =         fields.Char(related='student_id.phone',string='Phone No')
#    contact_mobile =        fields.related('student_id','mobile',type='char',relation='student.student',string='Mobile No')
    contact_mobile =        fields.Char(related='student_id.mobile',string='Mobile No')
    student_id =            fields.Many2one('student.student','Name')
#    contact_phone =         fields.related('student_id','phone',type='char',relation='student.student',string='Phone No',readonly=True)
#    contact_mobile =        fields.related('student_id','mobile',type='char',relation='student.student',string='Mobile No',readonly=True)
#    contact_email =         fields.related('student_id','email',type='char',relation='student.student',string='Email',readonly=True)
#    contact_website =       fields.related('student_id','website',type='char',relation='student.student',string='Website',readonly=True)
    contact_phone =         fields.Char(related='student_id.phone',string='Phone No',readonly=True)
    contact_mobile =        fields.Char(related='student_id.mobile',string='Mobile No',readonly=True)
    contact_email =         fields.Char(related='student_id.email',string='Email',readonly=True)
    contact_website =       fields.Char(related='student_id.website',string='Website',readonly=True)
    award_list =            fields.One2many('student.award','award_list_id',string='Award List')
#    student_status =        fields.related('state',type='char',relation='student.student',string='Status',help="Show the Status Of Student",readonly=True)
#    stu_name =              fields.related('user_id','name',type='char',relation='student.student',string='First Name',readonly=True)
#    Acadamic_year =         fields.related('year','name',type='char',relation='student.student',string='Academic Year',help="Academic Year",readonly=True)
    student_status =        fields.Selection(related='student_id.state',string='Status',help="Show the Status Of Student",readonly=True)
    stu_name =              fields.Char(related='user_id.name',string='First Name',readonly=True)
    Acadamic_year =         fields.Char(related='year.name',string='Academic Year',help="Academic Year",readonly=True)
    grn_number =            fields.Many2one('student.grn','GR No.',help="General reg number")
    standard_id =           fields.Many2one('standard.standard', 'Class')
    division_id =           fields.Many2one('standard.division', 'Division')
    medium_id =             fields.Many2one('standard.medium', 'Medium')
#    cmp_id =                fields.related('school_id','company_id',relation="res.company", string="Company Name", type="many2one", store=True)
    cmp_id =                fields.Many2one('res.company',string="Company Name",related='school_id.company_id',store=True)
    
    _sql_constraints = [('grn_unique', 'unique(grn_number)', 'GRN Number must be unique!')]

#    _defaults = {
#        'admission_date':fields.date.context_today,
#        'photo': lambda self: self._get_default_image(cr, uid, ctx.get('default_is_company', False), ctx),
#    }

    @api.multi
    def set_to_draft(self):
        self.write({'state' : 'draft'})
        return True
    
    @api.multi
    def set_alumni(self):
        self.write({'state' : 'alumni'})
        return True
    
    @api.multi
    def set_terminate(self):
        self.write({'state' : 'terminate'})
        return True
    
    @api.multi
    def set_done(self):
        self.write({'state' : 'done'})
        return True
    
#    def _get_default_image(self, cr, uid, is_company, context=None, colorize=False):
#        image = image_colorize(open(openerp.modules.get_module_resource('base', 'static/src/img', 'avatar.png')).read())
#        return image_resize_image_big(image.encode('base64'))
    
    @api.multi
    def _get_default_image(self, is_company, colorize=False):
        image = image_colorize(open(openerp.modules.get_module_resource('base', 'static/src/img', 'avatar.png')).read())
        return image_resize_image_big(image.encode('base64'))
    
    @api.multi
    def admission_draft(self):
        self.write({'state' : 'draft'})
        return True

#    def admission_done(self, cr, uid, ids, context=None):
#        school_standard_obj = self.pool.get('school.standard')
#        for student_data in self.browse(cr, uid, ids, context=context):
#            if student_data.age <=5:
#                raise osv.except_osv(_('Warning'), _('The student is not eligible. Age is not valid.'))
#            domain = [('standard_id', '=', student_data.standard_id.id)]
#            school_standard_search_ids = school_standard_obj.search(cr, uid, domain, context=context)
#            if not school_standard_search_ids:
#                raise osv.except_osv(_('Warning'), _('The standard is not defined in a school'))
#            domain = [('standard_id', '=', student_data.standard_id.id)]
#            student_search_ids = self.search(cr, uid, domain, context=context)
#            number = 1
#            for student in self.browse(cr, uid, student_search_ids, context=context):
#                self.write(cr, uid, [student.id], {'roll_no':number}, context=context)
#                number += 1
#            reg_code = self.pool.get('ir.sequence').get(cr, uid, 'student.registration')
#            registation_code = str(student_data.school_id.state_id.name) + str('/') + str(student_data.school_id.city) + str('/') + str(student_data.school_id.name) + str('/') + str(reg_code)
#            stu_code = self.pool.get('ir.sequence').get(cr, uid, 'student.code')
#            student_code = str(student_data.school_id.code) + str('/') + str(student_data.year.code) + str('/') + str(stu_code)
#        self.write(cr, uid, ids, {'state': 'done', 'admission_date': time.strftime('%Y-%m-%d'), 'student_code' : student_code, 'reg_code':registation_code}, context=context)
#        return True

    @api.multi
    def admission_done(self):
        school_standard_obj = self.env['school.standard']
        for student_data in self:
            if student_data.age <=5:
                raise except_orm(_('Warning'), _('The student is not eligible. Age is not valid.'))
            school_standard_search_ids = school_standard_obj.search([('standard_id', '=', student_data.standard_id.id)])
            if not school_standard_search_ids:
                raise except_orm(_('Warning'), _('The standard is not defined in a school'))
            student_search_ids = self.search([('standard_id', '=', student_data.standard_id.id)])
            number = 1
            for student in self.browse(student_search_ids):
                self.write({'roll_no':number})
                number += 1
            reg_code = self.env['ir.sequence'].get('student.registration')
            registation_code = str(student_data.school_id.state_id.name) + str('/') + str(student_data.school_id.city) + str('/') + str(student_data.school_id.name) + str('/') + str(reg_code)
            stu_code = self.env['ir.sequence'].get('student.code')
            student_code = str(student_data.school_id.code) + str('/') + str(student_data.year.code) + str('/') + str(stu_code)
        self.write({'state': 'done', 'admission_date': time.strftime('%Y-%m-%d'), 'student_code' : student_code, 'reg_code':registation_code})
        return True

class student_grn(models.Model):
    _name = "student.grn"
    _rec_name ="grn_no"

#    def _grn_no(self, cr, uid, ids, name, args, context=None):
#        res = {}
#        for stud_grn in self.browse(cr, uid, ids, context=context):
#            grn_no1=" "
#            grn_no2=" "
#            grn_no1= stud_grn['grn']
#            if stud_grn['prefix']=='static':
#                grn_no1=stud_grn['static_prefix'] + stud_grn['grn']
#            elif stud_grn['prefix']=='school':
#                a=stud_grn.schoolprefix_id.code
#                grn_no1 = a + stud_grn['grn']
#            elif stud_grn['prefix']=='year':
#                grn_no1 =  time.strftime('%Y')+ stud_grn['grn']
#            elif stud_grn['prefix']=='month':
#                grn_no1 =  time.strftime('%m')+ stud_grn['grn']
#            grn_no2=grn_no1
#            if stud_grn['postfix']=='static':
#                grn_no2=grn_no1+stud_grn['static_postfix']
#            elif stud_grn['postfix']=='school':
#                b=stud_grn.schoolpostfix_id.code
#                grn_no2 =grn_no1+b
#            elif stud_grn['postfix']=='year':
#                grn_no2 = grn_no1+ time.strftime('%Y')
#            elif stud_grn['postfix']=='month':
#                grn_no2 =grn_no1+ time.strftime('%m')
#            res[stud_grn.id]=grn_no2
#        return res

    @api.one
    def _grn_no(self):
        for stud_grn in self:
            grn_no1=" "
            grn_no2=" "
            grn_no1= stud_grn['grn']
            if stud_grn['prefix']=='static':
                grn_no1=stud_grn['static_prefix'] + stud_grn['grn']
            elif stud_grn['prefix']=='school':
                a=stud_grn.schoolprefix_id.code
                grn_no1 = a + stud_grn['grn']
            elif stud_grn['prefix']=='year':
                grn_no1 =  time.strftime('%Y')+ stud_grn['grn']
            elif stud_grn['prefix']=='month':
                grn_no1 =  time.strftime('%m')+ stud_grn['grn']
            grn_no2=grn_no1
            if stud_grn['postfix']=='static':
                grn_no2=grn_no1+stud_grn['static_postfix']
            elif stud_grn['postfix']=='school':
                b=stud_grn.schoolpostfix_id.code
                grn_no2 =grn_no1+b
            elif stud_grn['postfix']=='year':
                grn_no2 = grn_no1+ time.strftime('%Y')
            elif stud_grn['postfix']=='month':
                grn_no2 =grn_no1+ time.strftime('%m')
            self.grn_no = grn_no2
    
    grn =               fields.Char('GR no',size=64, help='General Reg Number',readonly=True,default=lambda obj:obj.env['ir.sequence'].get('student.grn'))
    name =              fields.Char('GRN Format Name',size=30,required=True)
    prefix =            fields.Selection([('school','School Name'),
                                          ('year','Year'),('month','Month'),
                                          ('static','Static String')],'Prefix')
    schoolprefix_id =   fields.Many2one('school.school', 'School Name for Prefix')
    schoolpostfix_id =  fields.Many2one('school.school', 'School Name for Suffix')
    postfix =           fields.Selection([('school','School Name'),
                                          ('year','Year'),('month','Month'),
                                          ('static','Static String')],'Suffix')
    static_prefix =     fields.Char('Static String for Prefix',size=5)
    static_postfix =    fields.Char('Static String for Suffix',size=5)
    grn_no =            fields.Char(compute='_grn_no',string='Generated GR No')

class mother_tongue(models.Model):
    _name = 'mother.toungue'
    
    name = fields.Char("Mother Tongue" ,size=64)

class student_award(models.Model):
    _name = 'student.award'
    
    award_list_id = fields.Many2one('student.student', 'Student')
    name =          fields.Char('Award Name',size=30)
    description =   fields.Char('Description',size=50)


class attendance_type(models.Model):
    _name = "attendance.type"
    _description = "School Type"
    
    name = fields.Char('Name', size=64, required=True)
    code = fields.Char('Code', size=12, required=True)

class student_document(models.Model):
    _name = 'student.document'
    _rec_name="doc_type"
    
    doc_id =        fields.Many2one('student.student', 'Student')
    file_no =       fields.Char('File No', size=12,readonly="1",default=lambda obj:obj.env['ir.sequence'].get('student.document'))
    submited_date = fields.Date('Submitted Date')
    doc_type =      fields.Many2one('document.type', 'Document Type', required=True)
    file_name =     fields.Char('File Name',size=30)
    return_date =   fields.Date('Return Date')
    new_datas =     fields.Binary('Attachments')

class document_type(models.Model):
    ''' Defining a Document Type(SSC,Leaving)'''
    _name = "document.type"
    _description = "Document Type"
    _rec_name="doc_type"
    _order = "seq_no"
    
    seq_no =    fields.Char('Sequence', readonly=True, default=lambda obj:obj.env['ir.sequence'].get('document.type'))
    doc_type =  fields.Char('Document Type', size=64, required=True)

class student_description(models.Model):
    ''' Defining a Student Description'''
    _name = 'student.description'
    
    des_id =        fields.Many2one('student.student', 'Description')
    name =          fields.Char('Name', size=20)
    description =   fields.Char('Description',size=50)

class student_descipline(models.Model):
    _name = 'student.descipline'
                
    student_id =    fields.Many2one('student.student', 'Student')
    teacher_id =    fields.Many2one('hr.employee', 'Teacher')
    date =          fields.Date('Date')
    class_id =      fields.Many2one('standard.standard', 'Class')
    note =          fields.Text('Note')
    action_taken =  fields.Text('Action Taken')

class student_history(models.Model):
    _name = "student.history"
    
    student_id =        fields.Many2one('student.student', 'Student')
    academice_year_id = fields.Many2one('academic.year', 'Academic Year', required=True)
    standard_id =       fields.Many2one('school.standard', 'Standard', required=True)
    percentage =        fields.Float("Percentage", readonly=True )
    result =            fields.Char(string ='Result', readonly=True, store=True, size =30)

class student_certificate(models.Model):
    _name = "student.certificate"
                
    student_id =    fields.Many2one('student.student', 'Student')
    description =   fields.Char('Description',size=50)
    certi =         fields.Binary('Certificate',required =True)

class hr_employee(models.Model):
    ''' Defining a teacher information '''
    _name = 'hr.employee'
    _inherit = 'hr.employee'
    _description = 'Teacher Information'
    
#    def _compute_subject(self, cr, uid, ids, name, args, context=None):
#        ''' This function will automatically computes the subjects related to particular teacher.'''
#        result = {}
#        subject_obj = self.pool.get('subject.subject')
#        for id in ids:
#            subject_ids = subject_obj.search(cr, uid,[('teacher_ids.id','=',id)])
#            result[id] = subject_ids
#        return result

    @api.one
    def _compute_subject(self):
        ''' This function will automatically computes the subjects related to particular teacher.'''
        subject_obj = self.env['subject.subject']
        for id in self:
            subject_ids = subject_obj.search([('teacher_ids.id','=',id)])
            self.subject_ids = subject_ids

#    subject_ids = fields.function(_compute_subject, method=True, relation='subject.subject', type="many2many", string='Subjects')
    subject_ids = fields.Many2many(compute='_compute_subject', string='Subjects')

class res_partner(models.Model):
    '''Defining a address information '''
    _inherit = 'res.partner'
    _description = 'Address Information'
    
    student_id = fields.Many2one('student.student','Student')

class student_reference(models.Model):
    ''' Defining a student reference information '''
    _name = "student.reference"
    _description = "Student Reference"
    
    reference_id =  fields.Many2one('student.student', 'Student')
    name =          fields.Char('First Name', size=64, required=True)
    middle =        fields.Char('Middle Name', size=64, required=True)
    last =          fields.Char('Surname', size=64, required=True)
    designation =   fields.Char('Designation', size=12, required=True)
    phone =         fields.Char('Phone', size=12, required=True)
    gender =        fields.Selection([('male','Male'), ('female','Female')], 'Gender')

class student_previous_school(models.Model):
    ''' Defining a student previous school information '''
    _name = "student.previous.school"
    _description = "Student Previous School"
    
    previous_school_id = fields.Many2one('student.student', 'Student')
    name =               fields.Char('Name', size=64, required=True)
    registration_no =    fields.Char('Registration No.', size=12, required=True)
    admission_date =     fields.Date('Admission Date')
    exit_date =          fields.Date('Exit Date')
    course_id =          fields.Many2one('standard.standard', 'Course', required=True)
    add_sub =            fields.One2many('academic.subject', 'add_sub_id', string='Add Subjects')

class academic_subject(models.Model):
    ''' Defining a student previous school information '''
    _name = "academic.subject"
    _description = "Student Previous School"
    
    add_sub_id =    fields.Many2one('student.previous.school', 'Add Subjects',invisible=True)
    name =          fields.Char('Name', size=64, required=True)
    maximum_marks = fields.Integer("Maximum marks")
    minimum_marks = fields.Integer("Minimum marks")

class student_family_contact(models.Model):
    ''' Defining a student emergency contact information '''
    _name = "student.family.contact"
    _description = "Student Family Contact"
    
    family_contact_id = fields.Many2one('student.student', string='Student')
    rel_name =          fields.Selection([('exist','Link to Existing Student'), ('new','Create New Relative Name')], 'Related Student', help="Select Name", required=True)
#    stu_name =          fields.related('user_id','name',type='many2one',relation='student.student',string='Name',help="Select Student From Existing List")
    user_id =           fields.Many2one('res.users', string='User ID', ondelete="cascade", select=True, required=True)
    stu_name =          fields.Char(related='user_id.name',string='Name',help="Select Student From Existing List")
    name =              fields.Char('Name',size=20 )
    relation =          fields.Many2one('student.relation.master',string='Relation', required=True)
    phone =             fields.Char('Phone', size=20, required=True)
    email =             fields.Char('E-Mail', size=100)

class student_relation_master(models.Model):
    ''' Student Relation Information '''
    _name = "student.relation.master"
    _description = "Student Relation Master"
    
    name =   fields.Char('Name',size=20,required=True,help="Enter Relation name")
    seq_no = fields.Integer('Sequence',size=5)

class grade_master(models.Model):
    _name = 'grade.master'
    
    name =      fields.Char('Grade', size = 256, select=1, required=True)
    grade_ids = fields.One2many('grade.line','grade_id', string='Grade Name')

class grade_line(models.Model):
    _name = 'grade.line'
    
    from_mark = fields.Integer("From Marks",required=True, help="The grade will starts from this marks.")
    to_mark =   fields.Integer('To Marks',required=True, help="The grade will ends to this marks.")
    grade =     fields.Char('Grade', size = 8, required=True, help="Grade")
    sequence =  fields.Integer('Sequence',help="Sequence order of the grade.")
    fail =      fields.Boolean("Fail",help="If fail field is set to True, it will allow you to set the grade as fail.")
    grade_id =  fields.Many2one("grade.master",'Grade')
    name =      fields.Char('Name',size=15)

class student_news(models.Model):
    _name='student.news'
    _description = 'Student News'
    _rec_name = 'subject'
    
    subject =       fields.Char('Subject', size=255, required=True, help="Subject of the news.") 
    description =   fields.Text('Description',help="Description")
    date =          fields.Datetime('Expiry Date',help="Expiry date of the news.")
    user_ids =      fields.Many2many('res.users','user_news_rel','id','user_ids','User News',help="Name to whom this news is related.")
    color =         fields.Integer('Color Index', default=0)

#    def news_update(self, cr, uid, ids, context = None):
#        emp_obj = self.pool.get("hr.employee")
#        obj_mail_server = self.pool.get('ir.mail_server')
#        mail_server_ids = obj_mail_server.search(cr, uid, [], context=context)
#        if not mail_server_ids:
#            raise osv.except_osv(_('Mail Error'), _('No mail outgoing mail server specified!'))
#        mail_server_record = obj_mail_server.browse(cr, uid, mail_server_ids[0])
#        email_list = []
#        for news in self.browse(cr, uid, ids, context):
#            if news.user_ids:
#                for user in news.user_ids:
#                    if user.email:
#                        email_list.append(user.email)
#                if not email_list:
#                    raise osv.except_osv(_('User Email Configuration '), _("Email not found in users !"))
#            else:
#                emp_ids = emp_obj.search(cr, uid, [], context = context)
#                for employee in emp_obj.browse(cr, uid,emp_ids, context=context ):
#                    if employee.work_email:
#                        email_list.append(employee.work_email)
#                    elif employee.user_id and employee.user_id.email:
#                        email_list.append(employee.user_id.email)
#                if not email_list:
#                    raise osv.except_osv(_('Mail Error' ), _("Email not defined!")) 
#            rec_date = fields.datetime.context_timestamp(cr, uid, datetime.strptime(news.date, DEFAULT_SERVER_DATETIME_FORMAT), context)
#            body =  'Hi,<br/><br/> \
#                This is a news update from <b>%s</b> posted at %s<br/><br/>\
#                %s <br/><br/>\
#                Thank you.' % (cr.dbname, rec_date.strftime('%d-%m-%Y %H:%M:%S'), news.description )
#            message  = obj_mail_server.build_email(
#                            email_from=mail_server_record.smtp_user, 
#                            email_to=email_list, 
#                            subject='Notification for news update.', 
#                            body=body, 
#                            body_alternative=body, 
#                            email_cc=None, 
#                            email_bcc=None, 
#                            reply_to=mail_server_record.smtp_user, 
#                            attachments=None, 
#                            references = None, 
#                            object_id=None, 
#                            subtype='html', #It can be plain or html
#                            subtype_alternative=None, 
#                            headers=None)
#            obj_mail_server.send_email(cr, uid, message=message, mail_server_id=mail_server_ids[0], context=context)
#        return True
    
    @api.multi
    def news_update(self):
        emp_obj = self.env['hr.employee']
        obj_mail_server = self.env['ir.mail_server']
        mail_server_ids = obj_mail_server.search([])
        if not mail_server_ids:
            raise except_orm(_('Mail Error'), _('No mail outgoing mail server specified!'))
        mail_server_record = obj_mail_server.browse(mail_server_ids[0])
        email_list = []
        for news in self:
            if news.user_ids:
                for user in news.user_ids:
                    if user.email:
                        email_list.append(user.email)
                if not email_list:
                    raise except_orm(_('User Email Configuration '), _("Email not found in users !"))
            else:
                emp_ids = emp_obj.search([])
                for employee in emp_obj.browse(emp_ids):
                    if employee.work_email:
                        email_list.append(employee.work_email)
                    elif employee.user_id and employee.user_id.email:
                        email_list.append(employee.user_id.email)
                if not email_list:
                    raise except_orm(_('Mail Error' ), _("Email not defined!")) 
            rec_date = fields.datetime.context_timestamp(cr, uid, datetime.strptime(news.date, DEFAULT_SERVER_DATETIME_FORMAT))
            body =  'Hi,<br/><br/> \
                This is a news update from <b>%s</b> posted at %s<br/><br/>\
                %s <br/><br/>\
                Thank you.' % (cr.dbname, rec_date.strftime('%d-%m-%Y %H:%M:%S'), news.description )
            message  = obj_mail_server.build_email(
                            email_from=mail_server_record.smtp_user, 
                            email_to=email_list, 
                            subject='Notification for news update.', 
                            body=body, 
                            body_alternative=body, 
                            email_cc=None, 
                            email_bcc=None, 
                            reply_to=mail_server_record.smtp_user, 
                            attachments=None, 
                            references = None, 
                            object_id=None, 
                            subtype='html', #It can be plain or html
                            subtype_alternative=None, 
                            headers=None)
            obj_mail_server.send_email(message=message, mail_server_id=mail_server_ids[0])
        return True


class student_reminder(models.Model):
    _name = 'student.reminder'
    
    stu_id =        fields.Many2one('student.student',' Student Name',required = True)
    name =          fields.Char('Title',size=30)
    date =          fields.Date('Date')
    description =   fields.Text('Description',size=130)
    color =         fields.Integer('Color Index', default=0)

class student_cast(models.Model):
    _name = "student.cast"
    
    name = fields.Char("Name",size=30,required=True)

class res_users(models.Model):
    _inherit = 'res.users'
    
#    def create(self, cr, uid, vals, context=None):
#        vals.update({'employee_ids':False})
#        res = super(res_users, self).create(cr, uid, vals, context=context)
#        return res

    @api.model
    def create(self,vals):
        vals.update({'employee_ids':False})
        res = super(res_users, self).create(vals)
        return res
        
        
# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4: