# -*- coding: utf-8 -*-
# See LICENSE file for full copyright and licensing details.

from odoo import models, fields, api, _
from odoo.exceptions import ValidationError


class TimeTable(models.Model):
    _description = 'Time Table'
    _name = 'time.table'

    name = fields.Char('Description')
    standard_id = fields.Many2one('school.standard', 'Academic Class',
                                  required=True)
    year_id = fields.Many2one('academic.year', 'Year', required=True)
    timetable_ids = fields.One2many('time.table.line', 'table_id', 'TimeTable')
    timetable_type = fields.Selection([('regular', 'Regular')],
                                      'Time Table Type', default="regular",
                                      inivisible=True)
#    do_not_create = fields.Boolean('Do not Create')

    _sql_constraints = [
        ('standard_year_unique', 'unique(standard_id,year_id)',
         'Academic class and year should be unique !')
    ]

    @api.multi
    @api.constrains('timetable_ids')
    def _check_lecture(self):
        '''Method to check same lecture is not assigned on same day'''
        domain = [('table_id', '=', self.ids)]
        line_ids = self.env['time.table.line'].search(domain)
        for rec in line_ids:
            records = [rec_check.id for rec_check in line_ids
                       if (rec.week_day == rec_check.week_day and
                           rec.start_time == rec_check.start_time and
                           rec.end_time == rec_check.end_time and
                           rec.teacher_id.id == rec.teacher_id.id)]
            if len(records) > 1:
                raise ValidationError(_('''You cannot set lecture at same
                                        time %s  at same day %s for teacher
                                        %s..!''') % (rec.start_time,
                                                     rec.week_day,
                                                     rec.teacher_id.name))
            # Checks if time is greater than 24 hours than raise error
            if rec.start_time > 24:
                raise ValidationError(_('''Start Time should be less than
                                        24 hours'''))
            if rec.end_time > 24:
                raise ValidationError(_('''End Time should be less than
                                        24 hours'''))
        return True


class TimeTableLine(models.Model):
    _description = 'Time Table Line'
    _name = 'time.table.line'
    _rec_name = 'table_id'

#    @api.multi
#    def onchange_recess(self, recess):
#        recess = {}
#        domain = [('name', 'like', 'Recess')]
#        sub_id = self.env['subject.subject'].search(domain)
#        if not sub_id:
#            raise UserError(_("You must have a 'Recess' as a subject"))
#        recess.update({'value': {'subject_id': sub_id.id}})
#        return recess
    @api.multi
    @api.constrains('teacher_id', 'subject_id')
    def check_teacher(self):
        '''Check if lecture is not related to teacher than raise error'''
        if (self.teacher_id.id not in self.subject_id.teacher_ids.ids and
                self.table_id.timetable_type == 'regular'):
            raise ValidationError(_('''The subject %s is not assigned to
                                    teacher %s.''') % (self.subject_id.name,
                                                       self.teacher_id.name))

    teacher_id = fields.Many2one('hr.employee', 'Faculty Name')
    subject_id = fields.Many2one('subject.subject', 'Subject Name',
                                 required=True)
    table_id = fields.Many2one('time.table', 'TimeTable')
    start_time = fields.Float('Start Time', required=True,
                              help="Time according to timeformat of 24 hours")
    end_time = fields.Float('End Time', required=True,
                            help="Time according to timeformat of 24 hours")
#    is_break = fields.Boolean('Is Break')
    week_day = fields.Selection([('monday', 'Monday'),
                                 ('tuesday', 'Tuesday'),
                                 ('wednesday', 'Wednesday'),
                                 ('thursday', 'Thursday'),
                                 ('friday', 'Friday'),
                                 ('saturday', 'Saturday'),
                                 ('sunday', 'Sunday')], "Week day",)


class SubjectSubject(models.Model):
    _inherit = "subject.subject"

    @api.model
    def search(self, args, offset=0, limit=None, order=None, count=False):
        teacher_id = self._context.get('teacher_id')
        if teacher_id:
            for teacher_data in self.env['hr.employee'].browse(teacher_id):
                args.append(('teacher_ids', 'in', [teacher_data.id]))
        return super(SubjectSubject, self).search(args, offset, limit, order,
                                                  count=count)
