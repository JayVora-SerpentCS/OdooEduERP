# -*- coding: utf-8 -*-
# See LICENSE file for full copyright and licensing details.

from odoo import models, fields, api, _
from odoo.exceptions import Warning as UserError


class BoardBoard(models.AbstractModel):
    _inherit = 'board.board'


class TimeTable(models.Model):
    _description = 'Time Table'
    _name = 'time.table'

    name = fields.Char('Description')
    standard_id = fields.Many2one('school.standard', 'Academic Class',
                                  required=True)
    year_id = fields.Many2one('academic.year', 'Year', required=True)
    timetable_ids = fields.One2many('time.table.line', 'table_id', 'TimeTable')
    do_not_create = fields.Boolean('Do not Create')

    @api.multi
    @api.constrains('timetable_ids')
    def _check_lecture(self):
        domain = [('table_id', '=', self.ids)]
        line_ids = self.env['time.table.line'].search(domain)
        for rec in line_ids:
            records = [rec_check.id for rec_check in line_ids
                       if (rec.week_day == rec_check.week_day and
                           rec.start_time == rec_check.start_time and
                           rec.end_time == rec_check.end_time)]
            if len(records) > 1:
                raise UserError(_("You can Not set lecture at same time\
                                 at same day..!!!"))
        return True


class TimeTableLine(models.Model):
    _description = 'Time Table Line'
    _name = 'time.table.line'
    _rec_name = 'table_id'

    @api.multi
    def onchange_recess(self, recess):
        recess = {}
        domain = [('name', 'like', 'Recess')]
        sub_id = self.env['subject.subject'].search(domain)
        if not sub_id:
            raise UserError(_("You must have a 'Recess' as a subject"))
        recess.update({'value': {'subject_id': sub_id.id}})
        return recess

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
        teacher_id = self._context.get('teacher_id')
        if teacher_id:
            for teacher_data in self.env['hr.employee'].browse(teacher_id):
                args.append(('teacher_ids', 'in', [teacher_data.id]))
        return super(SubjectSubject, self).search(args, offset, limit, order,
                                                  count=count)
