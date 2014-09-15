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

class student_evaluation(osv.Model):
    
    _name = "student.evaluation"
    
    def get_record(self, cr, uid, ids, context=None):
        ''' This method get record of Questions
        @param self : Object Pointer
        @param cr : Database Cursor
        @param uid : Current Logged in User
        @param ids : Current Records
        @param context : standard Dictionary
        @return : True 
        '''
        
        eval_line_obj = self.pool.get('student.evaluation.line') 
        eval_temp_obj = self.pool.get('student.evaluation.template')
        
        for stu_eval_rec in self.browse(cr , uid , ids, context=context):
            if stu_eval_rec.eval_line:
                cr.execute('delete from student_evaluation_line where eval_id=%s',(stu_eval_rec.id,))
            type = stu_eval_rec.type
            eval_temp_rec = eval_temp_obj.search(cr, uid, [('type', '=', type)], context=context)
            
            for i in range(0, len(eval_temp_rec)):
                eval_line_obj.create(cr , uid, {"stu_eval_id" : eval_temp_rec[i], "eval_id" : ids[0]}, context=context)        
        return True
    
    def _compute_total_points(self, cr, uid, ids, name, arg, context=None):
        ''' This method calculate total point of evaluation
        @param self : Object Pointer
        @param cr : Database Cursor
        @param uid : Current Logged in User
        @param ids : Current Records
        @param name : Functional field's name
        @param args : Other arguments
        @param context : standard Dictionary
        @return : Dictionary having identifier of the record as key and the  total point of evaluation
        '''
        if context is None:
            context = {}
        res = {}
        
        for rate_line in self.browse(cr, uid, ids, context=context):
            total=0
            for l in rate_line.eval_line:
                if l.point_id.point:
                    obtain_marks = l.point_id.point
                    total += obtain_marks
            res[rate_line.id] = total
        return res
    
    _rec_name = 'student_id'
    _columns = {
            'student_id' : fields.many2one('student.student', 'Student Name',required=True),
            'type' : fields.selection([('faculty', 'Faculty'), ('student', 'Student')], 'User Type', required=True),
            'date' : fields.date('Evaluation Date',required=True),
            'evaluator_id' : fields.many2one('hr.employee', 'Faculty Name'),
            'eval_line':fields.one2many('student.evaluation.line', 'eval_id', 'Questionnaire'),
            'total' : fields.function(_compute_total_points, method=True, string="Total Points"),
            'state' : fields.selection([('draft','Draft'),('start','Start'),('finished','Finish'),('cancelled','Cancel')], 'State',readonly=True),
            'user_id':fields.many2one('res.users','User',readonly=True)
        }
    
    def get_user(self,cr,uid,context=None):
        ''' This method return user
        @param self : Object Pointer
        @param cr : Database Cursor
        @param uid : Current Logged in User
        @param context : standard Dictionary
        @return : User id
        ''' 
        return uid
    _defaults = {
            'date':lambda * a: time.strftime('%Y-%m-%d'),
            'state' : 'draft',
            'user_id':get_user
      }
    
    def set_start(self, cr, uid, ids, context=None):
        ''' This method set state of the record
        @param self : Object Pointer
        @param cr : Database Cursor
        @param uid : Current Logged in User
        @param ids :  Current Records
        @param context : standard Dictionary
        @return : True
        ''' 
        self.write(cr, uid, ids, {'state' : 'start'}, context=context)
        return True
    
    def set_finish(self, cr, uid, ids, context=None):
        ''' This method set finish state of the record
        @param self : Object Pointer
        @param cr : Database Cursor
        @param uid : Current Logged in User
        @param ids :  Current Records
        @param context : standard Dictionary
        @return : True
        '''
        self.write(cr, uid, ids, {'state' : 'finished'}, context=context)
        return True
        
    def set_cancel(self, cr, uid, ids, context=None):
        ''' This method set cancel state of the record
        @param self : Object Pointer
        @param cr : Database Cursor
        @param uid : Current Logged in User
        @param ids :  Current Records
        @param context : standard Dictionary
        @return : True
        '''
        self.write(cr, uid, ids, {'state' : 'cancelled'}, context=context) 
        return True
    
    def set_draft(self, cr, uid, ids, context=None):
        ''' This method set draft state of the record
        @param self : Object Pointer
        @param cr : Database Cursor
        @param uid : Current Logged in User
        @param ids :  Current Records
        @param context : standard Dictionary
        @return : True
        '''
        self.write(cr, uid, ids, {'state' : 'draft'}, context=context)
        return True

class student_evaluation_line(osv.Model):
    
    _name = 'student.evaluation.line'
      
    def onchange_point(self,cr, uid, ids, point_id, context=None):
        point_obj = self.pool.get('rating.rating').browse(cr , uid, point_id)
        return {'value':{'rating':point_obj.rating}}
    
    _columns = {
            'eval_id' : fields.many2one('student.evaluation', 'eval id'),
            'stu_eval_id' : fields.many2one('student.evaluation.template', 'Question'),
            'point_id': fields.many2one('rating.rating','Rating', domain="[('rating_id','=',stu_eval_id)]"),
            'rating': fields.char('Remarks',size=45)
            } 
    _sql_constraints = [
        ('number_uniq', 'unique(eval_id, stu_eval_id)', 'Questions are already in Exists!'),
    ]

class student_evaluation_template(osv.Model):
    
    _name = "student.evaluation.template"
    
    _rec_name = 'desc'
    
    _columns = {
            'desc' : fields.char('Description', size=50, required=True),
            'type' : fields.selection([('faculty', 'Faculty'), ('student', 'Student')], 'User Type', required=True),
            'rating_line' : fields.one2many('rating.rating','rating_id','Rating')
        }
    
    _defaults = {
            'type' :'faculty',
                 }
        
class rating_rating(osv.Model):
    
    _name = 'rating.rating'
    
    _rec_name = 'point'
    _columns = {
                    'rating_id':fields.many2one('student.evaluation.template','Stud'),
                    'point' :fields.integer('Rating in points', required=True),
                    'rating' : fields.char('Remarks', size=50,required=True),
                }

# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4:                
