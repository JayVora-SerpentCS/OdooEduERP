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
import time
from openerp.tools.translate import _

class school_standard(osv.Model):
    
    _inherit = 'school.standard'
    _name = 'school.standard'
    _rec_name = 'event_ids'
    _columns = {
        'event_ids':fields.many2many('school.event', 'school_standard_event_rel', 'event_id', 'standard_id', 'Events', readonly=True),
    }

# Class for event parameter based on which score will given
class school_event_parameter(osv.Model):
    
    _name = 'school.event.parameter'
    _description = 'Event Parameter'
    _columns = {
        'name':fields.char('Parameter Name', size=50, required=True),
    }

#class for Participant which are participeted in events
class school_event_participant(osv.Model):
    
    _name = 'school.event.participant'
    _description = 'Participant Information'
    _order = "sequence"
    
    _columns = {
        'name': fields.many2one('student.student', 'Participant Name',readonly=True),
        'score': fields.float('Score'),
        'event_id': fields.many2one('school.event', 'Event', readonly=True),
        'stu_pid': fields.char('Personal Identification Number', size=50,required=True, readonly=True),
        'win_parameter_id': fields.many2one('school.event.parameter', 'Parameter', readonly=True),
        'sequence': fields.integer('Rank',  help="The sequence field is used to Give Rank to the Participant "),
    }
    _defaults = {
        'sequence': 0,
        'score': 0,
    }

#class for events
class school_event(osv.Model):
    
    _name = 'school.event'
    _description = 'Event Information'

    def _participants(self, cr, uid, ids, name, vals, context=None):
        ''' This method calculate event's participants
        @param self : Object Pointer
        @param cr : Database Cursor
        @param uid : Current Logged in User
        @param ids : Current Records
        @param name : Functional field's name
        @param vals : Other arguments
        @param context : standard Dictionary
        @return : Dictionary having identifier of the record as key and the event's participants as value 
        '''
        
        res= {}
        for event in self.browse(cr, uid, ids, context=context):
            res[event.id] = len(event.part_ids)
        return res
    _rec_name = 'name'
    _columns = {
        'name':fields.char('Event Name', size=50,  help= "Full Name of the event"),
        'event_type':fields.selection([('intra','Intra School'),
                                      ('inter','Inter School')],'Event Type',help='Event is either Intra chool or Inter school'),
        'start_date': fields.date('Start Date', help="Event Starting Date"),
        'end_date': fields.date('End Date',help="Event Ending Date"),
        'start_reg_date': fields.date('Start Registration Date', help="Event registration starting date"),
        'last_reg_date': fields.date('Last Registration Date',help="Last Date of registration"),
        'contact_per_id': fields.many2one('hr.employee', 'Contact Person', help="Event contact person"),
        'supervisor_id': fields.many2one('hr.employee', 'Supervisor', help="Event Supervisor Name"),
        'parameter_id': fields.many2one('school.event.parameter', 'Parameter', help="Parameters of the Event like (Goal, Point)"),
        'maximum_participants': fields.integer('Maximum Participants', help='Maximum Participant of the Event'),
        'participants': fields.function(_participants, method=True, string='Participants', type="integer", readonly=True),
        'part_standard_ids': fields.many2many('school.standard', 'school_standard_event_rel', 'standard_id', 'event_id', 'Participant Standards', help="The Participant is from whcih standard"),
        'state': fields.selection([
                                ('draft','Draft'),
                                ('open','Running'),
                                ('close','Close'),
                                ('cancel','Cancel')],
                                'State', readonly=True),
        'part_ids':fields.many2many('school.event.participant', 'event_participants_rel', 'participant_id', 'event_id', 'Participants', readonly=True, order_by='score'),
        'code':fields.many2one('school.school','Organiser School', help='Event Organised School'),
        'is_holiday':fields.boolean('Is Holiday', help='Checked if the event is organised on holiday.'),
        'color': fields.integer('Color Index'),
    }
    
    _defaults={
        'state':'draft',
        'color': 0,
    }

    def _check_dates(self, cr, uid, ids, context=None):
        ''' This method is a constraint, it's checks event start and end date
        @param self : Object Pointer
        @param cr : Database Cursor
        @param uid : Current Logged in User
        @param ids : Current Records
        @param context : standard Dictionary
        @return : if Constraint violate then return False otherwise True 
        '''
        for event in self.browse(cr, uid, ids, context = context):
            if event.start_date and event.end_date and event.start_date > event.end_date:
                return False
        return True
     

    def _check_all_dates(self, cr, uid, ids, context=None):
        ''' This method is a constraint, it's checks event date
        @param self : Object Pointer
        @param cr : Database Cursor
        @param uid : Current Logged in User
        @param ids : Current Records
        @param context : standard Dictionary
        @return : if Constraint violate then return False otherwise True 
        '''
        
        for event in self.browse(cr, uid, ids, context=context):
            if event.start_date and event.end_date and event.start_reg_date and event.last_reg_date:
                if event.start_reg_date > event.last_reg_date:
                    return False
                elif event.last_reg_date >= event.start_date:
                    return False
        return True 
    
    _constraints = [
        (_check_dates, 'Error! Event start-date must be lower then Event end-date.',[ 'start_date', 'end_date']),
        (_check_all_dates, 'Error! Event  Registration last-date must be lower than Event end-date or greater than start-date.', ['start_date', 'last_reg_date', 'end_date', 'last_reg_date']),
    ]

    def search(self, cr, uid, args, offset=0, limit=None, order=None, context=None, count=False):
        ''' This method search IDs of participants in event
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
        if context.get('part_name_id'):
            student_obj = self.pool.get('student.student')
            student_data = student_obj.browse(cr, uid, context['part_name_id'], context=context)
            args.append(('part_standard_ids', 'in', [student_data.class_id.id]))
        return super(school_event, self).search(cr, uid, args, offset, limit, order, context, count)
    
    def event_open(self, cr, uid, ids, context=None):
        ''' This method change the state of event as Open
        @param self : Object Pointer
        @param cr : Database Cursor
        @param uid : Current Logged in User
        @param ids : Current Records
        @param context : standard Dictionary
        @return : True 
        '''
        event_data = self.browse(cr, uid, ids, context=context)
        if event_data[0] and event_data[0].part_ids:
            self.write(cr, uid, ids, {'state' : 'open'}, context=context)
        else:
            raise osv.except_osv(_('No Participants !'), _('No Participants to open the Event.'))

    def event_close(self, cr, uid, ids, context=None):
        ''' This method change the state of event as Open
        @param self : Object Pointer
        @param cr : Database Cursor
        @param uid : Current Logged in User
        @param ids : Current Records
        @param context : standard Dictionary
        @return : True 
        '''
        
        self.write(cr, uid, ids, {'state' : 'close'}, context=context)
        return True

    def event_draft(self, cr, uid, ids, context=None):
        ''' This method change the state of event as draft
        @param self : Object Pointer
        @param cr : Database Cursor
        @param uid : Current Logged in User
        @param ids : Current Records
        @param context : standard Dictionary
        @return : True 
        '''
        
        self.write(cr, uid, ids, {'state' : 'draft'}, context=context)
        return True

    def event_cancel(self, cr, uid, ids, context=None):
        ''' This method change the state of event as cancel
        @param self : Object Pointer
        @param cr : Database Cursor
        @param uid : Current Logged in User
        @param ids : Current Records
        @param context : standard Dictionary
        @return : True 
        '''
        
        self.write(cr, uid, ids, {'state' : 'cancel'}, context=context)
        return True

#class for registration by students for events
class school_event_registration(osv.Model):
    
    _name = 'school.event.registration'
    _description = 'Event Registration'
    _columns = {
        'name': fields.many2one('school.event','Event Name', domain=[('state','=','draft')], required=True),
        'part_name_id': fields.many2one('student.student','Participant Name', required=True),
        'reg_date': fields.date('Registration Date', readonly=True),
        'state':fields.selection([('draft','Draft'),
                                      ('confirm','Confirm'),
                                      ('cancel','Cancel')
                                     ], 'State', readonly=True),
        'is_holiday':fields.boolean('Is Holiday',help = 'Checked if the event is organised on holiday.'),
        }

    _defaults={
        'state':'draft',
        "reg_date": lambda *a: time.strftime("%Y-%m-%d %H:%M:%S")
    }
#on cancellation of registration it will remove entry from events of students and Participant of events
    def regi_cancel(self, cr, uid, ids, context=None):
        ''' This method cancel of event registration
        @param self : Object Pointer
        @param cr : Database Cursor
        @param uid : Current Logged in User
        @param ids : Current Records
        @param context : standard Dictionary
        @return : True 
        '''
        if context is None:
            context = {}
        event_obj = self.pool.get('school.event')
        student_obj = self.pool.get('student.student')
        event_part_obj = self.pool.get('school.event.participant')
        self.write(cr, uid, ids, {'state' : 'cancel'}, context=context)
        for reg_data in self.browse(cr, uid, ids, context=context):
            event_data = event_obj.browse(cr, uid, reg_data.name.id, context=context)
            prt_data = student_obj.browse(cr, uid, reg_data.part_name_id.id, context=context)
            #delete etry of participant
            stu_prt_data = event_part_obj.search(cr, uid, [('stu_pid', '=', prt_data.pid), ('event_id', '=', reg_data.name.id), ('name', '=', reg_data.part_name_id.id)])
            event_part_obj.unlink(cr, uid, stu_prt_data, context=context)
            #remove entry of event from student
            list1 = []
            for part in prt_data.event_ids:
                part = student_obj.browse(cr, uid, part.id, context=context)
                list1.append(part.id)
            flag = True
            for part in list1:
                data = event_part_obj.browse(cr, uid, part, context=context)
                if data.event_id.id == reg_data.name.id:
                    flag = False
            if flag == False:
                list1.remove(part)
            student_obj.write(cr, uid, reg_data.part_name_id.id, {'event_ids':[(6,0,list1)]}, context=context)
            list1 =[]
            
            #remove etry of participant from event
            flag = True
            for par in event_data.part_ids:
                part = event_part_obj.browse(cr, uid, par.id, context=context)
                list1.append(part.id)
            for par in list1:
                data = event_part_obj.browse(cr, uid, par, context=context)
                if data.name.id == reg_data.part_name_id.id:
                    parii = par
                    flag = False
            if flag == False:
                list1.remove(parii)
            participants = int(event_data.participants) - 1
            event_obj.write(cr, uid, reg_data.name.id, {'part_ids':[(6,0,list1)], 'participants': participants}, context=context)
        return True

#on confirmation of registration it will make entry in events of students and Participant of events    
    def regi_confirm(self, cr, uid, ids, context=None):
        ''' This method confirm of event registration
        @param self : Object Pointer
        @param cr : Database Cursor
        @param uid : Current Logged in User
        @param ids : Current Records
        @param context : standard Dictionary
        @return : True 
        '''
        
        self.write(cr, uid, ids, {'state' : 'confirm'}, context=context)
        event_obj = self.pool.get('school.event')
        student_obj = self.pool.get('student.student')
        event_part_obj = self.pool.get('school.event.participant')
        for reg_data in self.browse(cr, uid, ids, context=context):
            event_data = event_obj.browse(cr, uid, reg_data.name.id, context=context)
            prt_data = student_obj.browse(cr, uid, reg_data.part_name_id.id, context=context)
            
            participants = int(event_data.participants) + 1
            #check participation is full or not.
            if participants > event_data.maximum_participants:
                raise osv.except_osv(_('Error !'),_('Participation in this Event is Full.'))
            
            #check last registration date is over or not
            if reg_data.reg_date > event_data.last_reg_date:
                raise osv.except_osv(_('Error !'),_('Last Registration date is over for this Event.'))
            
            # make entry in participant
            val  = {
                'stu_pid': str(prt_data.pid),
                'score': 0,
                'win_parameter_id': event_data.parameter_id.id,
                'event_id': reg_data.name.id,
                'name': reg_data.part_name_id.id,
            }
            temp = event_part_obj.create(cr, uid, val, context)
            #make entry of event in student
            list1 = []
            for evt in prt_data.event_ids:
                part = student_obj.browse(cr, uid, evt.id, context=context)
                list1.append(part.id)
            flag = True
            for evt in list1:
                data = event_part_obj.browse(cr, uid, evt, context=context)
                if data.event_id.id == reg_data.name.id:
                    flag = False
            if flag:
                list1.append(temp)
            student_obj.write(cr, uid, reg_data.part_name_id.id, {'event_ids':[(6,0,list1)]}, context=context)
            #make entry of participant in event
            list1 =[]
            flag = True
            for evt in event_data.part_ids:
                part = event_part_obj.browse(cr, uid, evt.id, context=context)
                list1.append(part.id)
            for evt in list1:
                data = event_part_obj.browse(cr, uid, evt, context=context)
                if data.name.id == reg_data.part_name_id.id:
                    flag = False
            if flag:
                list1.append(temp)
            event_obj.write(cr, uid, reg_data.name.id, {'part_ids':[(6,0,list1)]}, context=context)
        return True

class student_student(osv.Model):
    
    _name = 'student.student'
    _inherit = 'student.student'
    _description = 'Student Information'
    _columns = {
        'event_ids': fields.many2many('school.event.participant', 'event_participant_student_rel', 'event_id', 'stu_id', 'Events', readonly=True),
    }

    def search(self, cr, uid, args, offset=0, limit=None, order=None, context=None, count=False):
        ''' This method search IDs of student  
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
        if context.get('name'):
            event_obj = self.pool.get('school.event')
            event_data = event_obj.browse(cr, uid, context['name'], context=context)
            std_ids = [std_id.id for std_id in event_data.part_standard_ids]
            args.append(('class_id','in',std_ids))
        return super(student_student, self).search(cr, uid, args, offset, limit, order, context, count)
        
# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4: