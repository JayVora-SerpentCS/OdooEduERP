# -*- encoding: utf-8 -*-
##############################################################################
#
#    OpenERP, Open Source Management Solution
#    Copyright (C) 2004-2009 Tiny SPRL (<http://tiny.be>).
#    Copyright (C) 2011-2012 Serpent Consulting Services (<http://www.serpentcs.com>)
#    Copyright (C) 2013-2014 Serpent Consulting Services (<http://www.serpentcs.com>)
#    Copyright (C) 2015 Serpent Consulting Services (<http://www.serpentcs.com>)
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
from openerp.exceptions import except_orm, Warning, RedirectWarning

class time_table(models.Model):
    
    _description ='Time Table'
    _name = 'time.table'
    
    name = fields.Char('Description', size=64) 
    standard_id = fields.Many2one('school.standard', 'Academic Class', required=True)
    year_id = fields.Many2one('academic.year', 'Year', required=True)
    timetable_ids = fields.One2many('time.table.line', 'table_id', 'TimeTable')
    do_not_create = fields.Boolean('Do not Create')
    
    @api.one
    @api.constrains('name')
    def _check_lecture(self):
        records=[]
        line_obj = self.env['time.table.line']
        line_ids = line_obj.search([('table_id', '=', self.ids)])
        for rec in line_ids:
            count=0
            for i in line_ids:
                if (rec.week_day == i.week_day) and (rec.start_time == i.start_time) and  (rec.end_time == i.end_time):
                    count=count+1
                    if count >1:
                        records.append(i.id)
                        raise Warning(_('Warning!'), _("You can Not set lecture at same time at same day..!!!"))
        return True

class time_table_line(models.Model):
    
    _description ='Time Table Line'
    _name = 'time.table.line'
    _rec_name ="table_id"
    
    @api.multi
    def onchange_recess(self,recess):
        recess = {}
        sub_obj = self.env['subject.subject']
        emp_obj = self.env['resource.resource']
        hr_obj = self.env['hr.employee']
        sub_id = sub_obj.search([('name', 'like', 'Recess')])
        if not sub_id:
             raise Warning(_('Warning!'), _("You must have a 'Recess' as a subject"))
        recess.update({'value':{'subject_id':sub_id.id}})
        return recess

    teacher_id = fields.Many2one('hr.employee', 'Supervisor Name') 
    subject_id = fields.Many2one('subject.subject', 'Subject Name', required=True) 
    table_id  = fields.Many2one('time.table', 'TimeTable') 
    start_time = fields.Float('Start Time', required=True) 
    end_time = fields.Float('End Time', required=True) 
    is_break = fields.Boolean('Is Break') 
    week_day = fields.Selection([('monday', 'Monday'), ('tuesday', 'Tuesday'), ('wednesday', 'Wednesday'), ('thursday', 'Thursday'), ('friday', 'Friday'), ('saturday', 'Saturday'), ('sunday', 'Sunday')], "Week day",) 

class subject_subject(models.Model):
    
    _inherit ="subject.subject"
    
    @api.model
    def search(self, args, offset=0, limit=None, order=None, count=False):
        if self._context is None:
            context = {}
        if self._context.get('teacher_id'):
            teacher_obj = self.env['hr.employee']
            for teacher_data in teacher_obj.browse(self._context['teacher_id']):
                args.append(('teacher_ids', 'in', [teacher_data.id]))
        return super(subject_subject, self).search(args, offset, limit, order, count=count)
# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4: