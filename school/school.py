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
from openerp.osv import fields, osv
import time
import openerp
from datetime import datetime
from openerp.tools.translate import _
from openerp.tools import DEFAULT_SERVER_DATE_FORMAT, DEFAULT_SERVER_DATETIME_FORMAT, image_colorize, image_resize_image_big

class academic_year(osv.Model):
    ''' Defining an academic year '''
    _name = "academic.year"
    _description = "Academic Year"
    _order = "sequence"
    _columns = {
        'sequence': fields.integer('Sequence', required=True, help="In which sequence order you want to see this year."),
        'name': fields.char('Name', size=64, required=True, select=1,help='Name of  academic year'),
        'code': fields.char('Code', size=6, required=True, select=1,help='Code of academic year'),
        'date_start': fields.date('Start Date', required=True,help='Starting date of academic year'),
        'date_stop': fields.date('End Date', required=True,help='Ending of academic year'),
        'month_ids': fields.one2many('academic.month', 'year_id', 'Months',help="related Academic months"),
        'grade_id' : fields.many2one('grade.master',"Grade"),
        'description': fields.text('Description')
    }

    def next_year(self, cr, uid, sequence, context=None):
        year_ids = self.search(cr, uid, [('sequence', '>', sequence)])
        if year_ids:
            return year_ids[0]
        return False

    def name_get(self, cr, uid, ids, context=None):
        res = []
        for acd_year_rec in self.browse(cr, uid, ids, context=context):
            nam = "[" + acd_year_rec['code'] + "]" + acd_year_rec['name']
            res.append((acd_year_rec['id'], nam))
        return res

    def _check_academic_year(self, cr, uid, ids, context=None):
        obj_academic_ids = self.search(cr, uid, [], context=context)
        for current_academic_yr in self.browse(cr, uid, ids, context=context):
            obj_academic_ids.remove(current_academic_yr.id)
            data_academic_yr = self.browse(cr, uid, obj_academic_ids, context=context)
            for old_ac in data_academic_yr:
                if old_ac.date_start <= current_academic_yr.date_start <= old_ac.date_stop or \
                    old_ac.date_start <= current_academic_yr.date_stop <= old_ac.date_stop:
                    return False
        return True

    def _check_duration(self, cr, uid, ids, context=None):
        for obj_ac in self.browse(cr, uid, ids, context=context):
            if obj_ac.date_stop < obj_ac.date_start:
                return False
        return True

    _constraints = [
        (_check_duration, _('Error! The duration of the academic year is invalid.'), ['date_stop']),
        (_check_academic_year, _('Error! You cannot define overlapping academic years'), ['date_start', 'date_stop'])
    ]

class academic_month(osv.Model):
    ''' Defining a month of an academic year '''
    _name = "academic.month"
    _description = "Academic Month"
    _order = "date_start"
    _columns = {
        'name': fields.char('Name', size=64, required=True, help='Name of Academic month'),
        'code': fields.char('Code', size=12, required=True, help='Code of Academic month'),
        'date_start': fields.date('Start of Period', required=True, help='Starting of Academic month'),
        'date_stop': fields.date('End of Period', required=True,help='Ending of Academic month'),
        'year_id': fields.many2one('academic.year', 'Academic Year', required=True, help="Related Academic year "),
        'description': fields.text('Description')
    }

    def _check_duration(self, cr, uid, ids, context=None):
        for obj_month in self.browse(cr, uid, ids, context=context):
            if obj_month.date_stop < obj_month.date_start:
                return False
        return True

    def _check_year_limit(self,cr,uid,ids,context=None):
        for obj_month in self.browse(cr, uid, ids, context=context):
            if obj_month.year_id.date_stop < obj_month.date_stop or \
               obj_month.year_id.date_stop < obj_month.date_start or \
               obj_month.year_id.date_start > obj_month.date_start or \
               obj_month.year_id.date_start > obj_month.date_stop:
                return False
        return True

    _constraints = [
        (_check_duration, _('Error ! The duration of the Month(s) is/are invalid.'), ['date_stop']),
        (_check_year_limit, _('Invalid Months ! Some months overlap or the date period is not in the scope of the academic year.'), ['date_stop'])
    ]

class standard_medium(osv.Model):
    ''' Defining a medium(English, Hindi, Gujarati) related to standard'''
    _name = "standard.medium"
    _description = "Standard Medium"
    _order = "sequence"
    _columns = {
        'sequence': fields.integer('Sequence', required=True),
        'name': fields.char('Name', size=64, required=True),
        'code': fields.char('Code', size=12, required=True),
        'description': fields.text('Description'),
    }

class standard_division(osv.Model):
    ''' Defining a division(A, B, C) related to standard'''
    _name = "standard.division"
    _description = "Standard Division"
    _order = "sequence"
    _columns = {
        'sequence': fields.integer('Sequence', required=True),
        'name': fields.char('Name', size=64, required=True),
        'code': fields.char('Code', size=12, required=True),
        'description': fields.text('Description')
    }

class standard_standard(osv.Model):
    ''' Defining Standard Information '''
    _description ='Standard Information'
    _name = 'standard.standard'
    _order = "sequence"
    _columns = {
        'sequence': fields.integer('Sequence', required=True),
        'name': fields.char('Name', size=64, required=True),
        'code': fields.char('Code', size=20, required=True),
        'description': fields.text('Description'),
    }

    def next_standard(self, cr, uid, sequence, context=None):
        stand_ids = self.search(cr, uid, [('sequence', '>', sequence)])
        if stand_ids:
            return stand_ids[0]
        return False

class school_standard(osv.Model):
    ''' Defining a standard related to school '''
    _description ='School Standards'
    _name = 'school.standard'
    _rec_name ="school_id"

    def _compute_student(self, cr, uid, ids, name, args, context=None):
        ''' This function will automatically computes the students related to particular standard.'''
        result = {}
        student_obj = self.pool.get('student.student')
        for standard_data in self.browse(cr, uid, ids, context=context):
            student_ids = student_obj.search(cr, uid,[('standard_id', '=', standard_data.standard_id.id)], context=context)
            result[standard_data.id] = student_ids
        return result

    def import_subject(self, cr, uid, ids,context=None):
        ''' This function will automatically placed previous standard subject'''
        import_rec = self.browse(cr, uid, ids, context=context)
        for im_ob in import_rec:
            import_sub_id = self.search(cr, uid,[('standard_id', '=', int(im_ob.standard_id)-1)])
            val = []
            for import_sub_obj in self.browse(cr, uid, import_sub_id, context=context):
                for last in import_sub_obj.subject_ids: 
                    val.append(last.id)
                    self.write(cr, uid, ids, {'subject_ids': [(6, 0, val)]}, context=context)
        return True

    _columns = {
        'school_id': fields.many2one('school.school', 'School', required=True),
        'standard_id':fields.many2one('standard.standard', 'Class', required=True),
        'division_id':fields.many2one('standard.division', 'Division', required=True),
        'medium_id':fields.many2one('standard.medium', 'Medium', required=True),
        'subject_ids': fields.many2many('subject.subject', 'subject_standards_rel', 'subject_id', 'standard_id', 'Subject'),
        'user_id':fields.many2one('hr.employee', 'Class Teacher'),
        'student_ids': fields.function(_compute_student, method=True, relation='student.student', type="one2many", string='Student In Class'),
        'color': fields.integer('Color Index'),
        'passing':fields.integer('No Of ATKT', help="Allowed No of ATKTs"),
        'cmp_id':fields.related('school_id','company_id',relation="res.company", string="Company Name", type="many2one", store=True),
    }

    def name_get(self, cr, uid, ids, context=None):
        res = []
        for standard in self.browse(cr, uid, ids, context=context):
            nam = standard.standard_id.name+"[" + standard.division_id.name + "]" 
            res.append((standard.id,nam))
        return res

class school_school(osv.Model):
    
    ''' Defining School Information '''
    _description ='School Information'
    _name = 'school.school'
    _inherits = {'res.company': 'company_id'}
    _rec_name="com_name"
    
    def _lang_get(self, cr, uid, context=None):
        lang_pool = self.pool.get('res.lang')
        ids = lang_pool.search(cr, uid, [], context=context)
        res = lang_pool.read(cr, uid, ids, ['code', 'name'], context)
        return [(r['code'], r['name']) for r in res] + [('','')]
    _columns = {
        'company_id': fields.many2one('res.company', 'Company',ondelete="cascade", required=True),
#        Made field for Company Name 
        'com_name':fields.related('company_id','name',string="School Name",size=128,store=True,type="char"),
        'code': fields.char('Code', size=20, required=True, select=1),
        'standards':fields.one2many('school.standard', 'school_id','Standards'),
        'lang': fields.selection(_lang_get, 'Language',help="If the selected language is loaded in the system, all documents related to this partner will be printed in this language. If not, it will be english."),

    }

class subject_subject(osv.Model):
    
    '''Defining a subject '''
    _name = "subject.subject"
    _description = "Subjects"
    _columns = {
        'name': fields.char('Name', size=64, required=True),
        'code': fields.char('Code', size=12, required=True),
        'maximum_marks': fields.integer("Maximum marks", size=5),
        'minimum_marks': fields.integer("Minimum marks", size=5),
        'weightage': fields.integer("Weightage", size=10),
        'teacher_ids':fields.many2many('hr.employee','subject_teacher_rel','subject_id','teacher_id','Teachers'),
        'standard_ids':fields.many2many('school.standard','subject_standards_rel','standard_id','subject_id','Standards'),
        'standard_id':fields.many2one('standard.standard', 'Class'),
        'is_practical':fields.boolean('Is Practical',help='Check this if subject is practical.'),
        'no_exam' : fields.boolean("No Exam",help='Check this if subject has no exam.'),
        'elective_id' : fields.many2one('subject.elective'),
        'student_ids' : fields.many2many('student.student','elective_subject_student_rel','subject_id','student_id','Students'),
        'syllabus_ids':fields.one2many('subject.syllabus','subject_id','Syllabus')
    }

class subject_syllabus(osv.Model):
    
    '''Defining a  syllabus'''
    _name= "subject.syllabus"
    _description = "Syllabus"
    _rec_name = "duration"
    _columns = {
        'subject_id':fields.many2one('subject.subject', 'Subject'),
        'duration':fields.char("Duration"),
        'topic': fields.text("Topic")
    }

class subject_elective(osv.Model):
    
    _name = 'subject.elective'
    
    _columns = {
        'name' : fields.char("Name",size=32),
        'subject_ids' : fields.one2many('subject.subject','elective_id','Elective Subjects'),
    }

class student_student(osv.Model):
    ''' Defining a student information '''

    def _calc_age(self, cr, uid, ids, name, arg, context=None):
        ''' This function will automatically calculates the age of particular student.'''
        res= {}
        for student in self.browse(cr, uid, ids, context=context):
            start = datetime.strptime(student.date_of_birth, DEFAULT_SERVER_DATE_FORMAT)
            end = datetime.strptime(time.strftime(DEFAULT_SERVER_DATE_FORMAT),DEFAULT_SERVER_DATE_FORMAT)
            delta = end - start
            years =  (delta.days / 365)
            res[student.id] = years
        return res
    
    def create(self, cr, uid, data, context={}):
        if data.get('pid',False):
            data['login']= data['pid']
            data['password']= data['pid']
        else:
            raise osv.except_osv(_('Error!'), _('PID not valid, so record will not save.'))
        result = super(student_student, self).create(cr, uid, data, context=context)
        return result
    
    _name = 'student.student'
    _table = "student_student"
    _description = 'Student Information'
    _inherits = {'res.users': 'user_id'}
    _columns = {
        'user_id': fields.many2one('res.users', 'User ID', ondelete="cascade", select=True, required=True),
        'student_name' : fields.related('user_id', 'name',type='char', size=64, store=True, readonly=True),
        'pid':fields.char('Student ID', size=64, required=True, help='Personal IDentification Number'),
        'reg_code':fields.char('Registration Code', size=64, required=True, help='Student Registration Code'),
        'student_code':fields.char('Student Code', size=64, required=True),
        'contact_phone1': fields.char('Phone no.',size=20),
        'contact_mobile1': fields.char('Mobile no',size=20),
        'roll_no':fields.integer('Roll No.',readonly=True),
        'photo': fields.binary('Photo'),
        'year':fields.many2one('academic.year', 'Academic Year', required=True, states={'done':[('readonly',True)]}),
        'cast_id':fields.many2one('student.cast','Religion'),
        'admission_date':fields.date('Admission Date'),
        'middle': fields.char('Middle Name', size=64, required=True, states={'done':[('readonly',True)]}),
        'last': fields.char('Surname', size=64, required=True, states={'done':[('readonly',True)]}),
        'gender':fields.selection([('male','Male'), ('female','Female')], 'Gender', states={'done':[('readonly',True)]}),
        'date_of_birth':fields.date('Birthdate', required=True, states={'done':[('readonly',True)]}),
        'mother_tongue':fields.many2one('mother.toungue',"Mother Tongue"),
        'age':fields.function(_calc_age, method=True, string='Age', readonly=True, type="integer"),
        'maritual_status':fields.selection([('unmarried','Unmarried'), ('married','Married')], 'Maritual Status', states={'done':[('readonly',True)]}),
        'reference_ids':fields.one2many('student.reference', 'reference_id', 'References', states={'done':[('readonly',True)]}),
        'previous_school_ids':fields.one2many('student.previous.school', 'previous_school_id', 'Previous School Detail', states={'done':[('readonly',True)]}),
        'family_con_ids':fields.one2many('student.family.contact', 'family_contact_id', 'Family Contact Detail', states={'done':[('readonly',True)]}),
        'doctor': fields.char('Doctor Name', size=64, states={'done':[('readonly',True)]} ),
        'designation': fields.char('Designation', size=64),
        'doctor_phone': fields.char('Phone', size=12),
        'blood_group': fields.char('Blood Group', size=12),
        'height': fields.float('Height'),
        'weight': fields.float('Weight'),
        'eye':fields.boolean('Eyes'),
        'ear':fields.boolean('Ears'),
        'nose_throat':fields.boolean('Nose & Throat'),
        'respiratory':fields.boolean('Respiratory'),
        'cardiovascular':fields.boolean('Cardiovascular'),
        'neurological':fields.boolean('Neurological'),
        'muskoskeletal':fields.boolean('Musculoskeletal'),
        'dermatological':fields.boolean('Dermatological'),
        'blood_pressure':fields.boolean('Blood Pressure'),
        'remark':fields.text('Remark', states={'done':[('readonly',True)]}),
        'school_id': fields.many2one('school.school', 'School', states={'done':[('readonly',True)]}),
        'state':fields.selection([('draft','Draft'),('done','Done'),('terminate','Terminate'),('alumni','Alumni')],'State',readonly=True),
        'history_ids': fields.one2many('student.history', 'student_id', 'History'),
        'certificate_ids' : fields.one2many('student.certificate','student_id','Certificate'),
     #   'attendance_ids' : fields.one2many('attendance.sheet.line','name','Attendance History',readonly=True),
     #   'exam_results_ids' : fields.one2many('exam.result','student_id','Exam History',readonly=True),
    #    'student_attachment_line' : fields.one2many('student.attachment','student_id','Attachment'),
        'student_discipline_line' : fields.one2many('student.descipline','student_id','Descipline'),
        'address_ids' : fields.one2many('res.partner','student_id','Contacts'),
        'document':fields.one2many('student.document','doc_id','Documents'),
        'description':fields.one2many('student.description','des_id','Description'),
        'student_id': fields.many2one('student.student','name'),
        'contact_phone':fields.related('student_id','phone',type='char',relation='student.student',string='Phone No'),
        'contact_mobile':fields.related('student_id','mobile',type='char',relation='student.student',string='Mobile No'),
        'student_id': fields.many2one('student.student','Name'),
        'contact_phone':fields.related('student_id','phone',type='char',relation='student.student',string='Phone No',readonly=True),
        'contact_mobile':fields.related('student_id','mobile',type='char',relation='student.student',string='Mobile No',readonly=True),
        'contact_email':fields.related('student_id','email',type='char',relation='student.student',string='Email',readonly=True),
        'contact_website':fields.related('student_id','website',type='char',relation='student.student',string='Website',readonly=True),
        'award_list':fields.one2many('student.award','award_list_id','Award List'),
        'student_status':fields.related('state',type='char',relation='student.student',string='Status',help="Show the Status Of Student",readonly=True),
        'stu_name':fields.related('user_id','name',type='char',relation='student.student',string='First Name',readonly=True),
        'Acadamic_year':fields.related('year','name',type='char',relation='student.student',string='Academic Year',help="Academic Year",readonly=True),
        'grn_number': fields.many2one('student.grn','GR No.',help="General reg number"),
        'standard_id':fields.many2one('standard.standard', 'Class'),
        'division_id':fields.many2one('standard.division', 'Division'),
        'medium_id':fields.many2one('standard.medium', 'Medium'),
        'cmp_id':fields.related('school_id','company_id',relation="res.company", string="Company Name", type="many2one", store=True),
        }
    
    _sql_constraints = [('grn_unique', 'unique(grn_number)', 'GRN Number must be unique!')]

    _defaults = {
        'pid': lambda obj, cr, uid, context:obj.pool.get('ir.sequence').get(cr, uid, 'student.student'),
        'reg_code': ' ',
        'student_code':' ',
        'state':'draft',
        'admission_date':fields.date.context_today,
        'photo': lambda self, cr, uid, ctx: self._get_default_image(cr, uid, ctx.get('default_is_company', False), ctx),
    }
    
    def set_to_draft(self, cr, uid, ids, context=None):
        self.write(cr, uid, ids, {'state' : 'draft'}, context=context)
        return True
        
    def set_alumni(self, cr, uid, ids, context=None):
        self.write(cr, uid, ids, {'state' : 'alumni'}, context=context)
        return True
    
    def set_terminate(self, cr, uid, ids, context=None):
        self.write(cr, uid, ids, {'state' : 'terminate'}, context=context)
        return True
    
    def set_done(self, cr, uid, ids, context=None):
        self.write(cr, uid, ids, {'state' : 'done'}, context=context)
        return True
        
    def _get_default_image(self, cr, uid, is_company, context=None, colorize=False):
        image = image_colorize(open(openerp.modules.get_module_resource('base', 'static/src/img', 'avatar.png')).read())
        return image_resize_image_big(image.encode('base64'))
    
    def admission_draft(self, cr, uid, ids, context=None):
        self.write(cr, uid, ids, {'state' : 'draft'}, context=context)
        return True

    def admission_done(self, cr, uid, ids, context=None):
        school_standard_obj = self.pool.get('school.standard')
        for student_data in self.browse(cr, uid, ids, context=context):
            if student_data.age <=5:
                raise osv.except_osv(_('Warning'), _('The student is not eligible. Age is not valid.'))
            domain = [('standard_id', '=', student_data.standard_id.id)]
            school_standard_search_ids = school_standard_obj.search(cr, uid, domain, context=context)
            if not school_standard_search_ids:
                raise osv.except_osv(_('Warning'), _('The standard is not defined in a school'))
            domain = [('standard_id', '=', student_data.standard_id.id)]
            student_search_ids = self.search(cr, uid, domain, context=context)
            number = 1
            for student in self.browse(cr, uid, student_search_ids, context=context):
                self.write(cr, uid, [student.id], {'roll_no':number}, context=context)
                number += 1
            reg_code = self.pool.get('ir.sequence').get(cr, uid, 'student.registration')
            registation_code = str(student_data.school_id.state_id.name) + str('/') + str(student_data.school_id.city) + str('/') + str(student_data.school_id.name) + str('/') + str(reg_code)
            stu_code = self.pool.get('ir.sequence').get(cr, uid, 'student.code')
            student_code = str(student_data.school_id.code) + str('/') + str(student_data.year.code) + str('/') + str(stu_code)
        self.write(cr, uid, ids, {'state': 'done', 'admission_date': time.strftime('%Y-%m-%d'), 'student_code' : student_code, 'reg_code':registation_code}, context=context)
        return True

class student_grn(osv.Model):

    def _grn_no(self, cr, uid, ids, name, args, context=None):
        res = {}
        for stud_grn in self.browse(cr, uid, ids, context=context):
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
            res[stud_grn.id]=grn_no2
        return res
    
    _name = "student.grn"
    _rec_name ="grn_no"
    _columns = {
        'grn': fields.char('GR no',size=64, help='General Reg Number',readonly=True),
        'name': fields.char('GRN Format Name',size=30,required=True),
        'prefix': fields.selection([('school','School Name'),('year','Year'),('month','Month'),('static','Static String')],'Prefix'),
        'schoolprefix_id': fields.many2one('school.school', 'School Name for Prefix'),
        'schoolpostfix_id': fields.many2one('school.school', 'School Name for Suffix'),
        'postfix': fields.selection([('school','School Name'),('year','Year'),('month','Month'),('static','Static String')],'Suffix'),
        'static_prefix': fields.char('Static String for Prefix',size=5),
        'static_postfix': fields.char('Static String for Suffix',size=5),
        'grn_no': fields.function(_grn_no, type="char",method=True, string='Generated GR No'),
    }
    _defaults = {
       'grn': lambda obj, cr, uid, context:obj.pool.get('ir.sequence').get(cr, uid, 'student.grn'),
        }

class mother_tongue(osv.Model):
    _name = 'mother.toungue'
    _columns = {
        'name': fields.char("Mother Tongue" ,size=64)
    }

class student_award(osv.Model):
    _name = 'student.award'
    _columns = {
        'award_list_id' : fields.many2one('student.student', 'Student'),
        'name':fields.char('Award Name',size=30),
        'description':fields.char('Description',size=50),
    }

class attendance_type(osv.Model):
    '''Defining a subject '''
    _name = "attendance.type"
    _description = "School Type"
    _columns = {
        'name': fields.char('Name', size=64, required=True),
        'code': fields.char('Code', size=12, required=True),
    }

class student_document(osv.Model):
    _name = 'student.document'
    _rec_name="doc_type"
    _defaults = {
        'file_no':lambda obj, cr, uid, context:obj.pool.get('ir.sequence').get(cr, uid,'student.document'),
    }
    _columns = {
        'doc_id' : fields.many2one('student.student', 'Student'),
        'file_no':fields.char('File No', size=12,readonly="1"),
        'submited_date':fields.date('Submitted Date'),
        'doc_type' : fields.many2one('document.type', 'Document Type', required=True),
        'file_name':fields.char('File Name',size=30),
        'return_date':fields.date('Return Date'),
        'new_datas' : fields.binary('Attachments'),
    }

class document_type(osv.Model):
    ''' Defining a Document Type(SSC,Leaving)'''
    _name = "document.type"
    _description = "Document Type"
    _rec_name="doc_type"
    _order = "seq_no"
    _defaults={
        'seq_no': lambda obj, cr, uid, context:obj.pool.get('ir.sequence').get(cr, uid, 'document.type'),
    }
    _columns = {
        'seq_no': fields.char('Sequence', readonly=True),
        'doc_type': fields.char('Document Type', size=64, required=True),
    }

document_type()

class student_description(osv.Model):
    _name = 'student.description'
    _columns = {
        'des_id':fields.many2one('student.student', 'Description'),
        'name':fields.char('Name', size=20),
        'description':fields.char('Description',size=50),
    }

class student_descipline(osv.Model):
    _name = 'student.descipline'
    _columns = {
        'student_id' : fields.many2one('student.student', 'Student'),
        'teacher_id':fields.many2one('hr.employee', 'Teacher'),
        'date':fields.date('Date'),
        'class_id': fields.many2one('standard.standard', 'Class'),
        'note':fields.text('Note'),
        'action_taken':fields.text('Action Taken'),
    }

class student_history(osv.Model):
    _name = "student.history"
    _columns = {
        'student_id': fields.many2one('student.student', 'Student'),
        'academice_year_id':fields.many2one('academic.year', 'Academic Year', required=True),
        'standard_id': fields.many2one('school.standard', 'Standard', required=True),
        'percentage': fields.float("Percentage", readonly=True ),
        'result': fields.char(string ='Result', readonly=True, method=True,type = 'char', store=True, size =30),
    }

class student_certificate(osv.Model):
    _name = "student.certificate"
    _columns = {
        'student_id' : fields.many2one('student.student', 'Student'),
        'description' : fields.char('Description',size=50),
        'certi' : fields.binary('Certificate',required =True)
    }

class hr_employee(osv.Model):
    ''' Defining a teacher information '''

    def _compute_subject(self, cr, uid, ids, name, args, context=None):
        ''' This function will automatically computes the subjects related to particular teacher.'''
        result = {}
        subject_obj = self.pool.get('subject.subject')
        for id in ids:
            subject_ids = subject_obj.search(cr, uid,[('teacher_ids.id','=',id)])
            result[id] = subject_ids
        return result

    _name = 'hr.employee'
    _inherit = 'hr.employee'
    _description = 'Teacher Information'
    _columns = {
        'subject_ids': fields.function(_compute_subject, method=True, relation='subject.subject', type="many2many", string='Subjects'),
    }

class res_partner(osv.Model):
    '''Defining a address information '''
    _inherit = 'res.partner'
    _description = 'Address Information'
    _columns = {
        'student_id': fields.many2one('student.student','Student')
    }

class student_reference(osv.Model):
    ''' Defining a student reference information '''
    _name = "student.reference"
    _description = "Student Reference"
    _columns = {
        'reference_id': fields.many2one('student.student', 'Student'),
        'name': fields.char('First Name', size=64, required=True),
        'middle': fields.char('Middle Name', size=64, required=True),
        'last': fields.char('Surname', size=64, required=True),
        'designation': fields.char('Designation', size=12, required=True),
        'phone': fields.char('Phone', size=12, required=True),
        'gender':fields.selection([('male','Male'), ('female','Female')], 'Gender'),
    }

class student_previous_school(osv.Model):
    ''' Defining a student previous school information '''
    _name = "student.previous.school"
    _description = "Student Previous School"
    _columns = {
        'previous_school_id': fields.many2one('student.student', 'Student'),
        'name': fields.char('Name', size=64, required=True),
        'registration_no': fields.char('Registration No.', size=12, required=True),
        'admission_date': fields.date('Admission Date'),
        'exit_date': fields.date('Exit Date'),
        'course_id':fields.many2one('standard.standard', 'Course', required=True),
        'add_sub':fields.one2many('academic.subject', 'add_sub_id', 'Add Subjects'),
    }

class academic_subject(osv.Model):
    ''' Defining a student previous school information '''
    _name = "academic.subject"
    _description = "Student Previous School"
    _columns = {
        'add_sub_id': fields.many2one('student.previous.school', 'Add Subjects',invisible=True),
        'name': fields.char('Name', size=64, required=True),
        'maximum_marks': fields.integer("Maximum marks"),
        'minimum_marks': fields.integer("Minimum marks"),
    }

class student_family_contact(osv.Model):
    ''' Defining a student emergency contact information '''
    _name = "student.family.contact"
    _description = "Student Family Contact"
    _columns = {
        'family_contact_id': fields.many2one('student.student', 'Student'),
        'rel_name': fields.selection([('exist','Link to Existing Student'), ('new','Create New Relative Name')], 'Related Student', help="Select Name", required=True),
        'stu_name':fields.related('user_id','name',type='many2one',relation='student.student',string='Name',help="Select Student From Existing List"),
        'name':fields.char('Name',size=20 ),
        'relation': fields.many2one('student.relation.master','Relation', required=True),
        'phone': fields.char('Phone', size=20, required=True),
        'email': fields.char('E-Mail', size=100),
    }

class student_relation_master(osv.Model):
    ''' Student Relation Information '''
    _name = "student.relation.master"
    _description = "Student Relation Master"
    _columns = {
                'name':fields.char('Name',size=20,required=True,help="Enter Relation name"),
                'seq_no':fields.integer('Sequence',size=5),
                }

class grade_master(osv.Model):
    _name = 'grade.master'
    _columns = {
        'name': fields.char('Grade', size = 256, select=1, required=True),
        'grade_ids':fields.one2many('grade.line','grade_id', 'Grade Name'),
    }

class grade_line(osv.Model):
    _name = 'grade.line'
    _columns = {
        'from_mark': fields.integer("From Marks",required=True, help="The grade will starts from this marks."),
        'to_mark': fields.integer('To Marks',required=True, help="The grade will ends to this marks."),
        'grade': fields.char('Grade', size = 8, required=True, help="Grade"),
        'sequence' : fields.integer('Sequence',help="Sequence order of the grade."),
        'fail': fields.boolean("Fail",help="If fail field is set to True, it will allow you to set the grade as fail."),
        'grade_id' : fields.many2one("grade.master",'Grade'),
        'name':fields.char('Name',size=15)
    }

class student_news(osv.Model):
    _name='student.news'
    _description = 'Student News'
    _rec_name = 'subject'
    _columns={
        'subject' : fields.char('Subject', size=255, required=True, help="Subject of the news."), 
        'description' : fields.text('Description',help="Description"), 
        'date' :fields.datetime('Expiry Date',help="Expiry date of the news."),
        'user_ids' : fields.many2many('res.users','user_news_rel','id','user_ids','User News',help="Name to whom this news is related."),
        'color': fields.integer('Color Index'),
    }

    def news_update(self, cr, uid, ids, context = None):
        emp_obj = self.pool.get("hr.employee")
        obj_mail_server = self.pool.get('ir.mail_server')
        mail_server_ids = obj_mail_server.search(cr, uid, [], context=context)
        if not mail_server_ids:
            raise osv.except_osv(_('Mail Error'), _('No mail outgoing mail server specified!'))
        mail_server_record = obj_mail_server.browse(cr, uid, mail_server_ids[0])
        email_list = []
        for news in self.browse(cr, uid, ids, context):
            if news.user_ids:
                for user in news.user_ids:
                    if user.email:
                        email_list.append(user.email)
                if not email_list:
                    raise osv.except_osv(_('User Email Configuration '), _("Email not found in users !"))
            else:
                emp_ids = emp_obj.search(cr, uid, [], context = context)
                for employee in emp_obj.browse(cr, uid,emp_ids, context=context ):
                    if employee.work_email:
                        email_list.append(employee.work_email)
                    elif employee.user_id and employee.user_id.email:
                        email_list.append(employee.user_id.email)
                if not email_list:
                    raise osv.except_osv(_('Mail Error' ), _("Email not defined!")) 
            rec_date = fields.datetime.context_timestamp(cr, uid, datetime.strptime(news.date, DEFAULT_SERVER_DATETIME_FORMAT), context)
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
            obj_mail_server.send_email(cr, uid, message=message, mail_server_id=mail_server_ids[0], context=context)
        return True

    _defaults = {
        'color': 0,
    }

class student_reminder(osv.Model):
    _name = 'student.reminder'
    _columns = {
        'stu_id': fields.many2one('student.student',' Student Name',required = True),
        'name':fields.char('Title',size=30),
        'date' : fields.date('Date'),
        'description':fields.text('Description',size=130),
        'color': fields.integer('Color Index'),
    }
    _defaults = {
        'color': 0,
        }

class student_cast(osv.Model):
    _name = "student.cast"
    _columns = {
        'name':fields.char("Name",size=30,required=True),
    }
 
class res_users(osv.Model):
     
    _inherit = 'res.users'
     
    def create(self, cr, uid, vals, context=None):
        vals.update({'employee_ids':False})
        res = super(res_users, self).create(cr, uid, vals, context=context)
        return res

# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4: