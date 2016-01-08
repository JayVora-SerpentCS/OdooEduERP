# -*- coding: utf-8 -*-
# Part of Odoo. See LICENSE file for full copyright and licensing details.

from openerp import models, fields, api, _
from openerp.exceptions import Warning as UserError


class BoardBoard(models.Model):
    _inherit = 'board.board'


class TimeTable(models.Model):
    _description = 'Time Table'
    _name = 'time.table'

    name = fields.Char('Description')
    standard_id = fields.Many2one('school.standard', 'Academic Class',
                                  required=True)
    year_id = fields.Many2one('academic.year', 'Year', required=True)
    timetable_ids = fields.One2many('time.table.line', 'table_id', 'TimeTable')

    @api.one
    @api.constrains('timetable_ids')
    def _check_lecture(self):
        for rec in self.timetable_ids:
            records = [(rec_check.id for rec_check in self.timetable_ids \
                           if (rec.week_day == rec_check.week_day \
                                and rec.start_time == rec_check.start_time \
                                and rec.end_time == rec_check.end_time))]
            if len(records) > 1:
                raise UserError(_("You can not set lecture at same time\
                                 at same day..!!!"))
        return True


class TimeTableLine(models.Model):
    _description = 'Time Table Line'
    _name = 'time.table.line'
    _rec_name = 'table_id'

    @api.onchange('is_break')
    def onchange_recess(self):
        if self.is_break:
            domain = [('name', 'ilike', 'Recess')]
            sub_id = self.env['subject.subject'].search(domain)
            if not sub_id:
                raise UserError(_("You must have a 'Recess' as a subject"))
            return {'value': {'subject_id': sub_id.id}}
        return {'value': {}}
    
    def _check_times(self):
        if self.start_time and self.end_time:
            if self.start_time < self.end_time:
                raise UserError(_("Please check timings!"))

    teacher_id = fields.Many2one('hr.employee', 'Supervisor Name')
    subject_id = fields.Many2one('subject.subject', 'Subject Name',
                                 required=True)
    table_id = fields.Many2one('time.table', 'TimeTable')
    start_time = fields.Float('Start Time', required=True)
    end_time = fields.Float('End Time', required=True)
    is_break = fields.Boolean('Is Break')
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
        context = dict(self._context) or {}
        if args is None:
            args = []
        teacher_id = context.get('teacher_id', False)
        if teacher_id:
            args.append(('teacher_ids', 'in', [teacher_id]))
        return super(SubjectSubject, self).search(args, offset, limit, order,
                                                  count=count)
