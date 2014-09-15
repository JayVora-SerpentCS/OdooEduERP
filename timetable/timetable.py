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
from openerp.tools.translate import _

class time_table(osv.Model):
    
    _description ='Time Table'
    _name = 'time.table'
    
    _columns = {
    	'name': fields.char('Description', size=64), 
    	'standard_id': fields.many2one('school.standard', 'Academic Class', required=True), 
		'year_id': fields.many2one('academic.year', 'Year', required=True), 
       	'timetable_ids':fields.one2many('time.table.line', 'table_id', 'TimeTable'),
        'do_not_create' : fields.boolean('Do not Create')
    }
    
    def _check_lecture(self, cr, uid , ids, context=None):
        '''This method is a constraint that checks lectures 
        @param self : Object Pointer
        @param cr : Database Cursor
        @param uid : Current Logged in User
        @param ids : Current Records
        @param context : standard Dictionary
        @return : False if lecture set as same time otherwise True
        '''

        records=[]
        line_obj = self.pool.get('time.table.line')
        line_ids = line_obj.search(cr, uid, [('table_id', '=', ids[0])])
        rec_ids = line_obj.browse(cr, uid, line_ids)
        for rec in rec_ids:
            count=0
            for i in rec_ids:
                if (rec.week_day == i.week_day) and (rec.start_time == i.start_time) and  (rec.end_time == i.end_time):
                    count=count+1
                    if count >1:
                        records.append(i.id)
                        return False      
        return True
    
    _constraints=[
                  (_check_lecture,'You can Not set lecture at same time at same day..!!!',['name'])
                  ]

class time_table_line(osv.Model):
    
    _description ='Time Table Line'
    _name = 'time.table.line'
    
    def onchange_recess(self, cr, uid, ids, recess):
        '''This method automatically change value when time for recess 
        @param self : Object Pointer
        @param cr : Database Cursor
        @param uid : Current Logged in User
        @param ids : Current Records
        @param recces : Apply method on this Field name
        @return : Dictionary having identifier of the record as key and the value of recess
        '''

        recess = {}
        sub_obj = self.pool.get('subject.subject')
        emp_obj = self.pool.get('resource.resource')
        hr_obj = self.pool.get('hr.employee')        
        sub_id = sub_obj.search(cr, uid, [('name', 'like', 'Recess')])
        if not sub_id:
             raise osv.except_osv(_('Warning!'), _("You must have a 'Recess' as a subject"))
        recess.update({'value':{'subject_id':sub_id[0]}})
        return recess

    _rec_name ="table_id"
    _columns = {
		'teacher_id': fields.many2one('hr.employee', 'Supervisor Name',), 
        'subject_id': fields.many2one('subject.subject', 'Subject Name', required=True),#,domain="[('subject_id','=',subject_id)]" 
		'table_id': fields.many2one('time.table', 'TimeTable'), 
		'start_time' : fields.float('Start Time', required=True), 
		'end_time' : fields.float('End Time', required=True), 
        'is_break': fields.boolean('Is Break'), 
		'week_day' : fields.selection([('monday', 'Monday'), ('tuesday', 'Tuesday'), ('wednesday', 'Wednesday'), ('thursday', 'Thursday'), ('friday', 'Friday'), ('saturday', 'Saturday'), ('sunday', 'Sunday')], "Week day",), 
    }

class subject_subject(osv.Model):
    
    _name = 'subject.subject'
    _inherit ="subject.subject"
    _columns = {

    }
    def search(self, cr, uid, args, offset=0, limit=None, order=None, context=None, count=False):
        ''' This method search IDs of Teacher 
        @param self : Object Pointer
        @param cr : Database Cursor
        @param uid : Current Logged in User
        @param args : [(‘field_name’, ‘operator’, value), ...]. Pass an empty list to match all records.
        @param limit : max number of records to return (default: None)
        @param order : columns to sort by (default: self._order=id )
        @param context : context arguments, like lang, time zone
        @param count : (default: False), if True, returns only the number of records matching the criteria, not their ids
        @return : id or list of ids of records matching the criteria          
        '''
        if context is None:
            context = {}
        if context.get('teacher_id'):
            teacher_obj = self.pool.get('hr.employee')
            teacher_data = teacher_obj.browse(cr, uid, context['teacher_id'], context=context)
            args.append(('teacher_ids', 'in', [teacher_data.id]))
        return super(subject_subject, self).search(cr, uid, args, offset, limit, order, context, count)

# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4: