# See LICENSE file for full copyright and licensing details.

from odoo import models, fields, api, _
from odoo.exceptions import ValidationError


class TimeTable(models.Model):
    _description = 'Time Table'
    _name = 'time.table'

    @api.depends('timetable_ids')
    def _compute_user(self):
        '''Method to compute user'''
        for rec in self:
            rec.user_ids = [teacher.teacher_id.employee_id.user_id.id
                            for teacher in rec.timetable_ids
                            ]
        return True

    name = fields.Char('Description')
    standard_id = fields.Many2one('school.standard', 'Academic Class',
                                  required=True,
                                  help="Select Standard")
    year_id = fields.Many2one('academic.year', 'Year', required=True,
                              help="select academic year")
    timetable_ids = fields.One2many('time.table.line', 'table_id', 'TimeTable')
    timetable_type = fields.Selection([('regular', 'Regular')],
                                      'Time Table Type', default="regular",
                                      inivisible=True)
    user_ids = fields.Many2many('res.users', string="Users",
                                compute="_compute_user", store=True)
    class_room_id = fields.Many2one('class.room', 'Room Number')

    @api.constrains('timetable_ids')
    def _check_lecture(self):
        '''Method to check same lecture is not assigned on same day'''
        if self.timetable_type == 'regular':
            domain = [('table_id', 'in', self.ids)]
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
                                            24 hours!'''))
                if rec.end_time > 24:
                    raise ValidationError(_('''End Time should be less than
                                            24 hours!'''))
            return True


class TimeTableLine(models.Model):
    _description = 'Time Table Line'
    _name = 'time.table.line'
    _rec_name = 'table_id'

    @api.multi
    @api.constrains('teacher_id', 'subject_id')
    def check_teacher(self):
        '''Check if lecture is not related to teacher than raise error'''
        if (self.teacher_id.id not in self.subject_id.teacher_ids.ids and
                self.table_id.timetable_type == 'regular'):
            raise ValidationError(_('''The subject %s is not assigned to
                                    teacher %s.''') % (self.subject_id.name,
                                                       self.teacher_id.name))

    teacher_id = fields.Many2one('school.teacher', 'Faculty Name',
                                 help="Select Teacher")
    subject_id = fields.Many2one('subject.subject', 'Subject Name',
                                 help="Select Subject")
    table_id = fields.Many2one('time.table', 'TimeTable')
    start_time = fields.Float('Start Time', required=True,
                              help="Time according to timeformat of 24 hours")
    end_time = fields.Float('End Time', required=True,
                            help="Time according to timeformat of 24 hours")
    week_day = fields.Selection([('mon', 'Monday'),
                                 ('tue', 'Tuesday'),
                                 ('wed', 'Wednesday'),
                                 ('thu', 'Thursday'),
                                 ('fri', 'Friday'),
                                 ('sat', 'Saturday'),
                                 ('sun', 'Sunday')], "Week day")
    class_room_id = fields.Many2one('class.room', 'Room Number')

    @api.constrains('teacher_id', 'class_room_id')
    def check_teacher_room(self):
        timetable_rec = self.env['time.table'].search([('id', '!=',
                                                        self.table_id.id)])
        if timetable_rec:
            for data in timetable_rec:
                for record in data.timetable_ids:
                    if (data.timetable_type == 'regular' and
                            self.table_id.timetable_type == 'regular' and
                            self.teacher_id == record.teacher_id and
                            self.week_day == record.week_day and
                            self.start_time == record.start_time):
                            raise ValidationError(_('''There is a lecture of
                            Lecturer at same time!'''))
                    if (data.timetable_type == 'regular' and
                            self.table_id.timetable_type == 'regular' and
                            self.class_room_id == record.class_room_id and
                            self.start_time == record.start_time):
                            raise ValidationError(_("The room is occupied."))


class SubjectSubject(models.Model):
    _inherit = "subject.subject"

    @api.model
    def _search(self, args, offset=0, limit=None, order=None, count=False,
                access_rights_uid=None):
        '''Override method to get subject related to teacher'''
        teacher_id = self._context.get('teacher_id')
        if teacher_id:
            for teacher_data in self.env['school.teacher'].browse(teacher_id):
                args.append(('teacher_ids', 'in', [teacher_data.id]))
        return super(SubjectSubject, self)._search(
            args=args, offset=offset, limit=limit, order=order, count=count,
            access_rights_uid=access_rights_uid)
