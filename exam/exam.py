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
from openerp.osv import fields,osv
from datetime import date, datetime
from openerp.tools.translate import _

class extended_time_table(osv.Model):
    
    _inherit = 'time.table'
    
    _columns = {
        'timetable_type' : fields.selection([('exam', 'Exam'), ('regular', 'Regular')], "Time Table Type", required=True),
        'exam_id' : fields.many2one('exam.exam', 'Exam'),
    }

class extended_time_table_line(osv.Model):
    
    _inherit = 'time.table.line'
    
    _columns = {
        'exm_date' : fields.date('Exam Date'),
        'day_of_week': fields.char('Week Day',size=56),
    }
    
    def on_change_date_day(self, cr, uid, ids, exm_date, context=None):
        val = {}
        if exm_date:
            val['week_day'] = datetime.strptime(exm_date, "%Y-%m-%d").strftime("%A").lower()
        return {'value' : val}
        
    def _check_date(self, cr, uid, ids, context=None):
        line_ids = self.browse(cr, uid, ids, context=context)
        for line in line_ids:
            if line.exm_date:
                dt = datetime.strptime(line.exm_date, "%Y-%m-%d")
                if line.week_day != datetime.strptime(line.exm_date, "%Y-%m-%d").strftime("%A").lower():
                    return False
                elif dt.__str__() < datetime.strptime(date.today().__str__(), "%Y-%m-%d").__str__():
                    raise osv.except_osv(_('Invalid Date Error !'), _('Either you have selected wrong day for the date or you have selected invalid date.'))
        return True
    
class exam_exam(osv.Model):
   
    _name = 'exam.exam'
    _description = 'Exam Information'
    
    _columns = {
        'name': fields.char("Exam Name", size = 35, required = True),
        'exam_code': fields.char('Exam Code', size=64, required=True, readonly=True),
        'standard_id': fields.many2many('school.standard','school_standard_exam_rel','standard_id','event_id','Participant Standards'),
        'start_date': fields.date("Exam Start Date",help="Exam will start from this date"),
        'end_date': fields.date("Exam End date", help="Exam will end at this date"),
        'create_date': fields.date("Exam Created Date", help="Exam Created Date"),
        'write_date': fields.date("Exam Update Date", help="Exam Update Date"),
        'exam_timetable_ids' : fields.one2many('time.table', 'exam_id', 'Exam Schedule'),
        'state' : fields.selection([('draft','Draft'),('running','Running'),('finished','Finished'),('cancelled','Cancelled')], 'State', readonly=True)
    }

    def set_to_draft(self, cr, uid, ids, context=None):
        self.write(cr, uid, ids, {'state' : 'draft'}, context=context)
        
    def set_running(self, cr, uid, ids, context=None):
        exam_data = self.browse(cr, uid, ids, context=context)
        if exam_data[0] and exam_data[0].exam_timetable_ids:
            self.write(cr, uid, ids, {'state' : 'running'}, context=context)
        else:
            raise osv.except_osv(_('Exam Schedule'), _('You must add one Exam Schedule'))
    
    def set_finish(self, cr, uid, ids, context=None):
        self.write(cr, uid, ids, {'state' : 'finished'}, context=context)
    
    def set_cancel(self, cr, uid, ids, context=None):
        self.write(cr, uid, ids, {'state' : 'cancelled'}, context=context)
        

    def _validate_date(self, cr, uid, ids, context=None):
        for exm in self.browse(cr, uid, ids, context=context):
            if exm.start_date > exm.end_date:
                return False
        return True

    _defaults = {
        'exam_code': lambda obj, cr, uid, context:obj.pool.get('ir.sequence').get(cr, uid, 'exam.exam'),
        'state' : 'draft'
    }
    
class additional_exam(osv.Model):
    
    _name = 'additional.exam'
    _description = 'additional Exam Information'
    
    _columns = {
        'name': fields.char("Additional Exam Name", size = 35,required=True),
        'addtional_exam_code': fields.char('Exam Code', size=64, required=True, readonly=True),
        'standard_id': fields.many2one("school.standard", "Standard"),
        'subject_id': fields.many2one("subject.subject", "Subject Name"),
        'exam_date': fields.date("Exam Date"),
        'maximum_marks': fields.integer("Maximum Mark", size=30),
        'minimum_marks': fields.integer("Minimum Mark", size = 30),
        'weightage': fields.char("Weightage", size = 30),
        'create_date': fields.date("Created Date", help="Exam Created Date"),
        'write_date': fields.date("Updated date", help="Exam Updated Date"),
    }
    
    _defaults = {
        'addtional_exam_code': lambda obj, cr, uid, context:obj.pool.get('ir.sequence').get(cr, uid, 'additional.exam'),
    }
        
    def on_change_stadard_name(self, cr, uid, ids, standard_id, context=None):
        val = {}
        school_standard_obj = self.pool.get('school.standard')
        school_line = school_standard_obj.browse(cr, uid, standard_id, context=context)
        if school_line.medium_id.id:
            val['medium_id'] = school_line.medium_id.id
        if school_line.division_id.id:
            val['division_id'] = school_line.division_id.id
        return {'value': val}

class exam_result(osv.Model):

    _name = 'exam.result'
    _rec_name = 's_exam_ids'
    _description = 'exam result Information'

    def _compute_total(self, cr, uid, ids, name, arg, context=None):
        if context is None:
            context = {}
        res = {}
        for sub_line in self.browse(cr, uid, ids, context=context):
            total=0.0
            for l in sub_line.result_ids:
                obtain_marks = l.obtain_marks
                if l.state == "re-evaluation":
                    obtain_marks = l.marks_reeval
                elif l.state == "re-access":
                    obtain_marks = l.marks_access
                total += obtain_marks
        res[sub_line.id] = total
        return res

    def _compute_per(self, cr, uid, ids, context=None):
        if context is None:
            context = {}
        res={}
        for result in self.browse(cr, uid, ids, context=context):
            total = 0.0
            obtained_total = 0.0
            obtain_marks = 0.0
            per = 0.0
            grd = ""
            for sub_line in result.result_ids:
                if sub_line.state == "re-evaluation":
                    obtain_marks = sub_line.marks_reeval
                elif sub_line.state == "re-access":
                    obtain_marks = sub_line.marks_access
                obtain_marks = sub_line.obtain_marks
                total += sub_line.maximum_marks or 0
                obtained_total += obtain_marks
            if total != 0.0:
                per = (obtained_total/total)  * 100
                for grade_id in result.student_id.year.grade_id.grade_ids:
                    if per >= grade_id.from_mark and per <= grade_id.to_mark: 
                        grd = grade_id.grade
                res[result.id] = {'percentage':per,'grade':grd}
        return res
    
    def _compute_result(self, cr, uid, ids, name, arg, context=None):
        if context is None:
            context = {}
        res={}
        flag = False
        for sub_line in self.browse(cr, uid, ids, context=context) or []:
            for l in sub_line.result_ids:
                if sub_line.student_id.year.grade_id.grade_ids:
                    for grades in sub_line.student_id.year.grade_id.grade_ids:
                        if grades.grade:
                            if not grades.fail:
                                res[sub_line.id] = 'Pass'
                            else:
                                flag=True
                else:
                        raise osv.except_osv(_('Configuration Error !'), _('First Select Grade System in Student->year->.'))
                if flag:
                    res[sub_line.id] = 'Fail'
            return res

    def on_change_student(self, cr, uid, ids, student, exam_id, standard_id, context=None):
        val = {}
        if not student:
            return {}
        if not exam_id:
            raise osv.except_osv(_('Input Error !'), _('First Select Exam.'))
        student_obj = self.pool.get('student.student')
        student_data = student_obj.browse(cr, uid, student, context=context)
        val.update({'standard_id' : student_data.standard_id.id,
                    'roll_no_id' : student_data.roll_no})
        return {'value': val}

    _columns = {
            's_exam_ids': fields.many2one("exam.exam", "Examination",required = True),
            'student_id': fields.many2one("student.student", "Student Name", required = True),
            'roll_no_id': fields.related("student_id", "roll_no", type="integer", string="Roll No", readonly=True),
            'pid': fields.related("student_id", "pid", type="char", size=64, string="Student ID", readonly=True),
            'standard_id': fields.many2one("school.standard", "Standard", required=True),
            'result_ids': fields.one2many("exam.subject","exam_id","Exam Subjects"),
            'total': fields.function(_compute_total, string ='Obtain Total', method=True, type='float', store=True),
            're_total': fields.float('Re-access Obtain Total', readonly=True),
            'percentage': fields.float("Percentage", readonly=True ),
            'result': fields.function(_compute_result, string ='Result', readonly=True, method=True,type = 'char', store=True, size =30),
            'grade' : fields.char("Grade", size=15, readonly=True),
            'state': fields.selection([('draft','Draft'), ('confirm','Confirm'), ('re-access','Re-Access'),('re-access_confirm','Re-Access-Confirm'), ('re-evaluation','Re-Evaluation'),('re-evaluation_confirm','Re-Evaluation Confirm')], 'State', readonly=True),
            'color': fields.integer('Color'),
        }
    
    _defaults = {
        'state': 'draft',
    }

    def result_confirm(self, cr, uid, ids, context=None):
        vals = {}
        res = self._compute_per(cr, uid, ids, context=context)
        if not res:
            raise osv.except_osv(_('Warning!'), _('Please Enter the students Marks.'))
        vals.update({'grade' : res[ids[0]]['grade'], 'percentage' : res[ids[0]]['percentage'], 'state':'confirm'})
        self.write(cr, uid, ids, vals, context=context)
        return True

    def result_re_access(self, cr, uid, ids, context=None):
        self.write(cr, uid, ids, {'state':'re-access'})
        return True

    def re_result_confirm(self, cr, uid, ids, context=None):
        if context is None:
            context = {}
        res={}
        for result in self.browse(cr, uid, ids, context=context):
            opt_marks = []
            acc_mark  = []
            sum = 0.0
            total = 0.0
            obtained_total = 0.0
            obtain_marks = 0.0
            per = 0.0
            grd = 0.0
            for sub_line in result.result_ids:
                opt_marks.append(sub_line.obtain_marks)
                acc_mark.append(sub_line.marks_access)
            for i in range(0, len(opt_marks)):
                if acc_mark[i] != 0.0:    
                    opt_marks[i]=acc_mark[i]
            for i in range(0, len(opt_marks)):
                sum = sum + opt_marks[i]
                total += sub_line.maximum_marks or 0
            if total != 0.0:
                per = (sum/total)  * 100
                for grade_id in result.student_id.year.grade_id.grade_ids:
                    if per >= grade_id.from_mark and per <= grade_id.to_mark:
                        grd = grade_id.grade
                res.update({'grade' : grd, 'percentage' : per, 'state':'re-access_confirm','re_total':sum})
            self.write(cr, uid, ids, res, context=context)
        return True
    
    def re_evaluation_confirm(self, cr, uid, ids, context=None):
        if context is None:
            context = {}
        res={}
        for result in self.browse(cr, uid, ids, context=context):
            opt_marks = []
            eve_marks = []
            sum = 0.0
            total = 0.0
            obtained_total = 0.0
            obtain_marks = 0.0
            per = 0.0
            grd = 0.0
            for sub_line in result.result_ids:
                opt_marks.append(sub_line.obtain_marks)
                eve_marks.append(sub_line.marks_reeval)
            for i in range(0, len(opt_marks)):
                if eve_marks[i] != 0.0:    
                    opt_marks[i]=eve_marks[i]
            for i in range(0, len(opt_marks)):
                sum = sum + opt_marks[i]
                total += sub_line.maximum_marks or 0
            if total != 0.0:
                per = (sum/total)  * 100
                for grade_id in result.student_id.year.grade_id.grade_ids:
                    if per >= grade_id.from_mark and per <= grade_id.to_mark:
                        grd = grade_id.grade
                res.update({'grade' : grd, 'percentage' : per, 'state':'re-evaluation_confirm','re_total':sum})
            self.write(cr, uid, ids, res, context=context)
        return True

    def result_re_evaluation(self, cr, uid, ids, context=None):
        self.write(cr, uid, ids, {'state':'re-evaluation'})
        return True

class exam_grade_line(osv.Model):
    _name = "exam.grade.line"
    _description = 'Exam Subject Information'
    _rec_name = 'standard_id'
    _columns = {
            'standard_id': fields.many2one('standard.standard', 'Standard'), 
            'exam_id': fields.many2one('exam.result', 'Result'),
            'grade' : fields.char(string='Grade',size=21)
     }

class exam_subject(osv.Model):
    _name = "exam.subject"
    _description = 'Exam Subject Information'
    _rec_name = 'subject_id'
    
    def _validate_marks(self, cr, uid, ids, context=None):
        for marks_line in self.browse(cr, uid, ids, context=context):
            if marks_line.obtain_marks > marks_line.maximum_marks or marks_line.minimum_marks > marks_line.maximum_marks:
                return False
        return True
    
    def _get_grade(self, cr, uid, ids, name, arg, context=None):
        if context is None:
            context = {}
        res={}
        for sub_id in self.browse(cr, uid, ids, context):
            if sub_id.exam_id.student_id.year.grade_id.grade_ids:
                for grade_id in sub_id.exam_id.student_id.year.grade_id.grade_ids:
                    if sub_id.obtain_marks >= grade_id.from_mark and sub_id.obtain_marks <= grade_id.to_mark:
                        res[sub_id.id]=grade_id.grade
        return res
    
    _columns = {
            'exam_id': fields.many2one('exam.result', 'Result'),
            'state': fields.related('exam_id', 'state', type="char", string="State", size=10),
            'subject_id': fields.many2one("subject.subject","Subject Name"),
            'obtain_marks': fields.float("Obtain Marks", group_operator="avg"),
            'minimum_marks':fields.float("Minimum Marks"),
            'maximum_marks':fields.float("Maximum Marks"),
            'marks_access':fields.float("Marks After Access"),
            'marks_reeval':fields.float("Marks After Re-evaluation"),
            'grade_id' : fields.many2one('grade.master',"Grade"),
            'grade' : fields.function(_get_grade, string='Grade', type="char",method=True),
     }

    _constraints = [(_validate_marks, 'The obtained marks and minimum marks should not extend maximum marks.', ['obtain_marks','minimum_marks'])]

class exam_result_batchwise(osv.Model):

    _name = 'exam.batchwise.result'
    _rec_name='standard_id'
    _description = 'exam result Information by Batch wise'
                    
    def compute_grade(self, cr, uid, ids, name, arg, context=None):
        if context is None: context = {}
        res = {}
        fina_tot=0
        count=0
        divi=0
        year_obj=self.pool.get('academic.year')
        stud_obj = self.pool.get('exam.result')
        s = self.browse(cr, uid, ids[0], context)
        year_ob=year_obj.browse(cr, uid, s.year.id, context=context)
        stand_id = stud_obj.search(cr, uid, [('standard_id', '=', s.standard_id.id )])
        for id in stand_id:
            student_ids = stud_obj.browse(cr,uid, id) 
            if student_ids.result_ids:
                for res_line in student_ids.result_ids:
                    count+= 1
                fina_tot += student_ids.total
            divi=fina_tot/count#Total_obtain mark of all student
    
            if year_ob.grade_id.grade_ids:
                for grade_id in year_ob.grade_id.grade_ids:
                    if divi >= grade_id.from_mark and divi <= grade_id.to_mark:
                        res[s.id]=grade_id.grade
        return res
    
    _columns = {
            'standard_id': fields.many2one("school.standard", "Standard", required=True),
            'year':fields.many2one('academic.year', 'Academic Year', required=True),
            'grade' : fields.function(compute_grade, string='Grade', type="char", method=True, store=True)
        }
    
class additional_exam_result(osv.Model):

    _name = 'additional.exam.result'
    _description = 'subject result Information'
    
    def _calc_result(self, cr, uid, ids, name, arg, context=None):
        res = {}
        for l in self.browse(cr, uid, ids, context=context):
            min_mark = l.a_exam_id.subject_id.minimum_marks
            if min_mark <= l.obtain_marks:
                res[l.id] = 'Pass'
            else:
                res[l.id] = 'Fail'
        return res

    def on_change_student(self, cr, uid, ids, student, context=None):
        val = {}
        student
        student_obj = self.pool.get('student.student')
        student_data = student_obj.browse(cr, uid, student, context=context)
        val.update({'standard_id' : student_data.standard_id.id,
                    'roll_no_id' : student_data.roll_no})
        return {'value': val}
    
    def _validate_marks(self, cr, uid, ids, context=None):
        for marks_line in self.browse(cr, uid, ids, context=context):
            if marks_line.obtain_marks > marks_line.a_exam_id.subject_id.maximum_marks:
                return False
        return True

    _columns = {
            'a_exam_id': fields.many2one("additional.exam", "Additional Examination", required=True),
            'student_id': fields.many2one("student.student", "Student Name", required=True),
            'roll_no_id': fields.related("student_id", "roll_no", type="integer", string="Roll No", readonly=True),
            'standard_id': fields.related("student_id", "standard_id", type="many2one", relation="school.standard", string="Standard", readonly=True),
            'obtain_marks': fields.float("Obtain Marks"),
            'result': fields.function(_calc_result, string ='Result', method=True, type='char'),
        }

    _constraints = [(_validate_marks, 'The obtained marks should not extend maximum marks.', ['obtain_marks'])]

class student_student(osv.Model):
    _name = 'student.student'
    _inherit = 'student.student'
    _description = 'Student Information'

    def search(self, cr, uid, args, offset=0, limit=None, order=None, context=None, count=False):
        if context is None:
            context = {}
        if context.get('exam'):
            exam_obj = self.pool.get('exam.exam')
            exam_data = exam_obj.browse(cr, uid, context['exam'], context=context)
            std_ids = [std_id.id for std_id in exam_data.standard_id]
            args.append(('class_id','in',std_ids))
        return super(student_student, self).search(cr, uid, args, offset, limit, order, context, count)

# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4:
