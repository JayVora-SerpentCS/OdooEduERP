# -*- encoding: utf-8 -*-
##############################################################################
#
#    OpenERP, Open Source Management Solution
#    Copyright (C) 2004-2009 Tiny SPRL (<http://tiny.be>).
#    Copyright (C) 2011-2012 Serpent Consulting Services
#    (<http://www.serpentcs.com>)
#    Copyright (C) 2013-2014 Serpent Consulting Services
#    (<http://www.serpentcs.com>)
#    Copyright (C) 2015 Serpent Consulting Services
#    (<http://www.serpentcs.com>)
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
import datetime

from openerp import models, fields, api, _
from openerp.exceptions import Warning


class time_table(models.Model):

    _description = 'Time Table'
    _name = 'time.table'

    name = fields.Char('Description')
    standard_id = fields.Many2one('school.standard', 'Academic Class',
                                  required=True)
    year_id = fields.Many2one('academic.year', 'Year', required=True)
    timetable_ids = fields.One2many('time.table.line', 'table_id', 'TimeTable')
    do_not_create = fields.Boolean('Do not Create')

    @api.one
    @api.constrains('timetable_ids')
    def _check_lecture(self):
        line_ids = self.env['time.table.line'].search([('table_id', '=',
                                                        self.ids)])
        for rec in line_ids:
            records = [rec_check.id for rec_check in line_ids
                       if (rec.week_day == rec_check.week_day) and
                       (rec.start_time == rec_check.start_time) and
                       (rec.end_time == rec_check.end_time)]
            if len(records) > 1:
                raise Warning(_('Warning!'), _("You can Not set lecture at"
                                               "same time at same day..!!!"))
        return True


class time_table_line(models.Model):

    _description = 'Time Table Line'
    _name = 'time.table.line'
    _rec_name = "table_id"

    @api.multi
    def onchange_recess(self, recess):
        recess = {}
        sub_id = self.env['subject.subject'].search([('name', 'like',
                                                      'Recess')])
        if not sub_id:
            raise Warning(_('Warning!'),
                          _("You must have a 'Recess' as a'' subject"))
        recess.update({'value': {'subject_id': sub_id.id}})
        return recess

    @api.onchange('sub_exam_date')
    def _get_day(self):
        if self.sub_exam_date:
            date1 = self.sub_exam_date
            new_date = datetime.datetime.strptime(date1, '%Y-%m-%d')
            self.week_day = new_date.strftime("%A")

    teacher_id = fields.Many2one('hr.employee', 'Supervisor Name')
    subject_id = fields.Many2one('subject.subject', 'Subject Name',
                                 required=True)
    table_id = fields.Many2one('time.table', 'TimeTable')
    tables_id = fields.Many2one('exam.exam', 'TimeTable')
    start_time = fields.Float('Start Time', required=True)
    end_time = fields.Float('End Time', required=True)
    is_break = fields.Boolean('Is Break')
    week_day = fields.Char('Day')
    sub_exam_date = fields.Date('Subject Exam Date')
    standard_id = fields.Many2one("school.standard", "Standard")

    @api.constrains('sub_exam_date', 'tables_id.end_date')
    def _check_sub_exam_date(self):
        if self.sub_exam_date > self.tables_id.end_date:
                raise Warning(_('Please Check The Subject Exam Date'))
        return True

    @api.constrains('sub_exam_date', 'tables_id.start_date')
    def _check_sub_exam_start_date(self):
        if self.sub_exam_date < self.tables_id.start_date:
                raise Warning(_('Please Check The Subject Exam Date'))
        return True

    @api.multi
    @api.onchange('standard_id')
    def onchange_ad_standard(self):
        sub_list = []
        for exam_obj in self:
            for time_table in exam_obj.standard_id:
                for sub_id in time_table.subject_ids:
                    sub_list.append(sub_id.id)
        return {'domain': {'subject_id': [('id', 'in', sub_list)]}}


class subject_subject(models.Model):

    _inherit = "subject.subject"

    @api.model
    def search(self, args, offset=0, limit=None, order=None, count=False):
        if self._context.get('teacher_id'):
            for teacher_data in self.env['hr.employee'].browse(self.
                                                               _context
                                                               ['teacher_id']
                                                               ):
                args.append(('teacher_ids', 'in', [teacher_data.id]))
        return super(subject_subject, self).search(args, offset, limit,
                                                   order, count=count)
# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4:
