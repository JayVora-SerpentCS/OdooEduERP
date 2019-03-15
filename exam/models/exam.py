# See LICENSE file for full copyright and licensing details.

from datetime import date, datetime
from odoo import models, fields, api, _
from odoo.exceptions import ValidationError


class StudentStudent(models.Model):
    _inherit = 'student.student'
    _description = 'Student Information'

    exam_results_ids = fields.One2many('exam.result', 'student_id',
                                       'Exam History', readonly=True)

    @api.multi
    def set_alumni(self):
        '''Override method to make exam results of student active false
        when student is alumni'''
        for rec in self:
            addexam_result = self.env['additional.exam.result'].\
                search([('student_id', '=', rec.id)])
            regular_examresult = self.env['exam.result'].\
                search([('student_id', '=', rec.id)])
            if addexam_result:
                addexam_result.write({'active': False})
            if regular_examresult:
                regular_examresult.write({'active': False})
        return super(StudentStudent, self).set_alumni()

    @api.model
    def _search(self, args, offset=0, limit=None, order=None, count=False,
                access_rights_uid=None):
        '''Override method to get exam of student selected'''
        if self._context.get('exam'):
            exam_obj = self.env['exam.exam']
            exam_data = exam_obj.browse(self._context['exam'])
            std_ids = [std_id.id for std_id in exam_data.standard_id]
            args.append(('standard_id', 'in', std_ids))
        return super(StudentStudent, self)._search(
            args=args, offset=offset, limit=limit, order=order, count=count,
            access_rights_uid=access_rights_uid)


class ExtendedTimeTable(models.Model):
    _inherit = 'time.table'

    @api.multi
    def unlink(self):
        exam = self.env['exam.exam']
        schedule_line = self.env['exam.schedule.line']
        for rec in self:
            exam_search = exam.search([('state', '=', 'running')])
            for data in exam_search:
                schedule_line_search = schedule_line.search([('exam_id', '=',
                                                              data.id),
                                                             ('timetable_id',
                                                              '=', rec.id)])
                if schedule_line_search:
                    raise ValidationError(_('''You cannot delete schedule of
                    exam which is in running!'''))
        return super(ExtendedTimeTable, self).unlink()

    timetable_type = fields.Selection(selection_add=[('exam', 'Exam')],
                                      string='Time Table Type', required=True,
                                      inivisible=False)
    exam_timetable_line_ids = fields.One2many('time.table.line', 'table_id',
                                              'TimeTable Lines')
    exam_id = fields.Many2one('exam.exam', 'Exam')

    @api.constrains('exam_timetable_line_ids')
    def _check_exam(self):
        '''Method to check same exam is not assigned on same day'''
        if self.timetable_type == 'exam':
            if not self.exam_timetable_line_ids:
                raise ValidationError(_(''' Please Enter Exam Timetable!'''))
            domain = [('table_id', 'in', self.ids)]
            line_ids = self.env['time.table.line'].search(domain)
            for rec in line_ids:
                records = [rec_check.id for rec_check in line_ids
                           if (rec.day_of_week == rec_check.day_of_week and
                               rec.start_time == rec_check.start_time and
                               rec.end_time == rec_check.end_time and
                               rec.teacher_id.id == rec.teacher_id.id and
                               rec.exm_date == rec.exm_date)]
                if len(records) > 1:
                    raise ValidationError(_('''You cannot set exam at same
                                            time %s  at same day %s for
                                            teacher %s!''') %
                                           (rec.start_time, rec.day_of_week,
                                            rec.teacher_id.name))


class ExtendedTimeTableLine(models.Model):
    _inherit = 'time.table.line'

    exm_date = fields.Date('Exam Date')
    day_of_week = fields.Char('Week Day')
    class_room_id = fields.Many2one('class.room', 'Classroom')

    @api.onchange('exm_date')
    def onchange_date_day(self):
        '''Method to get weekday from date'''
        for rec in self:
            rec.day_of_week = False
            if rec.exm_date:
                week_day = datetime.strptime(str(rec.exm_date), "%Y-%m-%d")
                rec.day_of_week = week_day.strftime("%A").title()

    @api.multi
    def _check_date(self):
        '''Method to check constraint of start date and end date'''
        for line in self:
            if line.exm_date:
                dt = datetime.strptime(line.exm_date, "%Y-%m-%d")
                if line.week_day != dt.strftime("%A").lower():
                    return False
                elif dt.__str__() < datetime.strptime(date.today().__str__(),
                                                      "%Y-%m-%d").__str__():
                    raise ValidationError(_('''Invalid Date Error !
                        Either you have selected wrong day
                                       for the date or you have selected\
                                       invalid date!'''))

    @api.constrains('teacher_id')
    def check_supervisior_exam(self):
            for rec in self:
                if (rec.table_id.timetable_type == 'exam' and
                        not rec.teacher_id):
                        raise ValidationError(_('''PLease Enter Supervisior!
                        '''))

    @api.constrains('start_time', 'end_time')
    def check_time(self):
        for rec in self:
            if rec.start_time >= rec.end_time:
                raise ValidationError(_('''Start time should be less than end
                time!'''))

    @api.constrains('teacher_id', 'class_room_id')
    def check_teacher_room(self):
        timetable_rec = self.env['time.table'].search([('id', '!=',
                                                        self.table_id.id)])
        if timetable_rec:
            for data in timetable_rec:
                for record in data.timetable_ids:
                    if (data.timetable_type == 'exam' and
                            self.table_id.timetable_type == 'exam' and
                            self.class_room_id == record.class_room_id and
                            self.start_time == record.start_time):
                            raise ValidationError(_("The room is occupied!"))

    @api.constrains('subject_id', 'class_room_id')
    def check_exam_date(self):
        for rec in self.table_id.exam_timetable_line_ids:
            record = self.table_id
            if rec.id not in self.ids:
                if (record.timetable_type == 'exam' and
                        self.exm_date == rec.exm_date and
                        self.start_time == rec.start_time):
                    raise ValidationError(_('''There is already Exam at
                        same Date and Time!'''))
                if (record.timetable_type == 'exam' and
                        self.table_id.timetable_type == 'exam' and
                        self.subject_id == rec.subject_id):
                        raise ValidationError(_('''%s Subject Exam Already
                        Taken''') % (self.subject_id.name))
                if (record.timetable_type == 'exam' and
                        self.table_id.timetable_type == 'exam' and
                        self.exm_date == rec.exm_date and
                        self.class_room_id == rec.class_room_id and
                        self.start_time == rec.start_time):
                    raise ValidationError(_('''%s is occupied by '%s' for %s
                    class!''') % (self.class_room_id.name, record.name,
                                  record.standard_id.standard_id.name))


class ExamExam(models.Model):
    _name = 'exam.exam'
    _description = 'Exam Information'

    @api.constrains('start_date', 'end_date')
    def check_date_exam(self):
        '''Method to check constraint of exam start date and end date'''
        for rec in self:
            if rec.end_date < rec.start_date:
                raise ValidationError(_('''Exam end date should be
                                  greater than start date!'''))
            for line in rec.exam_schedule_ids:
                if line.timetable_id:
                    for tt in line.timetable_id.exam_timetable_line_ids:
                        if not rec.start_date <= tt.exm_date <= rec.end_date:
                            raise ValidationError(_('Invalid Exam Schedule\
                            \n\nExam Dates must be in between Start\
                            date and End date !'))

    @api.constrains('active')
    def check_active(self):
        '''if exam results is not in done state then raise an
        validation Warning'''
        result_obj = self.env['exam.result']
        if not self.active:
            for result in result_obj.search([('s_exam_ids', '=', self.id)]):
                if result.state != 'done':
                    raise ValidationError(_('Kindly,mark as done %s\
                    examination results!') % (self.name))

    active = fields.Boolean('Active', default="True")
    name = fields.Char("Exam Name", required=True,
                       help="Name of Exam")
    exam_code = fields.Char('Exam Code', required=True, readonly=True,
                            help="Code of exam",
                            default=lambda obj:
                            obj.env['ir.sequence'].next_by_code('exam.exam'))
    standard_id = fields.Many2many('standard.standard',
                                   'standard_standard_exam_rel', 'standard_id',
                                   'event_id', 'Participant Standards',
                                   help="Select Standard")
    start_date = fields.Date("Exam Start Date",
                             help="Exam will start from this date")
    end_date = fields.Date("Exam End date", help="Exam will end at this date")
    state = fields.Selection([('draft', 'Draft'),
                              ('running', 'Running'),
                              ('finished', 'Finished'),
                              ('cancelled', 'Cancelled')], 'State',
                             readonly=True, default='draft')
    grade_system = fields.Many2one('grade.master', "Grade System",
                                   help="Select Grade System")
    academic_year = fields.Many2one('academic.year', 'Academic Year',
                                    help="Select Academic Year")
    exam_schedule_ids = fields.One2many('exam.schedule.line', 'exam_id',
                                        'Exam Schedule')

    @api.multi
    def set_to_draft(self):
        '''Method to set state to draft'''
        self.state = 'draft'

    @api.multi
    def set_running(self):
        '''Method to set state to running'''
        for rec in self:
            if not rec.standard_id:
                raise ValidationError(_('Please Select Standard!'))
            if rec.exam_schedule_ids:
                rec.state = 'running'
            else:
                raise ValidationError(_('You must add one Exam Schedule!'))

    @api.multi
    def set_finish(self):
        '''Method to set state to finish'''
        self.state = 'finished'

    @api.multi
    def set_cancel(self):
        '''Method to set state to cancel'''
        self.state = 'cancelled'

    @api.multi
    def generate_result(self):
        '''Method to generate result'''
        result_obj = self.env['exam.result']
        student_obj = self.env['student.student']
        result_list = []
        for rec in self:
            for exam_schedule in rec.exam_schedule_ids:
                domain = [('standard_id', '=', exam_schedule.standard_id.id),
                          ('year', '=', rec.academic_year.id),
                          ('state', '=', 'done'),
                          ('school_id', '=', exam_schedule.standard_id.school_id.id)]
                students = student_obj.search(domain)
                for student in students:
                    domain = [('standard_id', '=',
                               student.standard_id.id),
                              ('student_id', '=', student.id),
                              ('s_exam_ids', '=', rec.id)]
                    result_exists = result_obj.search(domain)
                    if result_exists:
                        [result_list.append(res.id) for res in result_exists]
                    else:
                        rs_dict = {'s_exam_ids': rec.id,
                                   'student_id': student.id,
                                   'standard_id': student.standard_id.id,
                                   'roll_no_id': student.roll_no,
                                   'grade_system': rec.grade_system.id,
                                   }
                        exam_line = []
                        timetable = exam_schedule.sudo().timetable_id
                        for line in timetable.sudo().timetable_ids:
                            min_mrks = line.subject_id.minimum_marks
                            max_mrks = line.subject_id.maximum_marks
                            sub_vals = {'subject_id': line.subject_id.id,
                                        'minimum_marks': min_mrks,
                                        'maximum_marks': max_mrks}
                            exam_line.append((0, 0, sub_vals))
                        rs_dict.update({'result_ids': exam_line})
                        result = result_obj.create(rs_dict)
                        
                        result_list.append(result.id)
        return {'name': _('Result Info'),
                'view_type': 'form',
                'view_mode': 'tree,form',
                'res_model': 'exam.result',
                'type': 'ir.actions.act_window',
                'domain': [('id', 'in', result_list)]}


class ExamScheduleLine(models.Model):
    _name = 'exam.schedule.line'
    _description = "Exam Schedule Line Details"

    @api.onchange('standard_ids')
    def onchange_standard(self):
        '''Method to get standard according to the standard selected'''
        standard_ids = []
        for rec in self:
            standard_ids = [std.id for std in rec.standard_ids]
        return {'domain': {'standard_id': [('standard_id', 'in',
                                            standard_ids)]}}

    standard_id = fields.Many2one('school.standard', 'Standard',
                                  help="Select Standard")
    timetable_id = fields.Many2one('time.table', 'Exam Schedule')
    exam_id = fields.Many2one('exam.exam', 'Exam')
    standard_ids = fields.Many2many('standard.standard',
                                    string='Participant Standards')


class AdditionalExam(models.Model):
    _name = 'additional.exam'
    _description = 'additional Exam Information'

    @api.multi
    def _compute_color_name(self):
        for rec in self:
            rec.color_name = rec.subject_id.id

    name = fields.Char("Additional Exam Name", required=True,
                       help="Name of Exam")
    addtional_exam_code = fields.Char('Exam Code', required=True,
                                      help="Exam Code",
                                      readonly=True,
                                      default=lambda obj:
                                      obj.env['ir.sequence'].
                                      next_by_code('additional.exam'))
    standard_id = fields.Many2one("school.standard", "Standard")
    subject_id = fields.Many2one("subject.subject", "Subject Name")
    exam_date = fields.Date("Exam Date")
    maximum_marks = fields.Integer("Maximum Mark",
                                   help="Minimum Marks of exam")
    minimum_marks = fields.Integer("Minimum Mark",
                                   help="Maximum Marks of Exam")
    weightage = fields.Char("WEIGHTAGE")
    create_date = fields.Date("Created Date", help="Exam Created Date")
    write_date = fields.Date("Updated date", help="Exam Updated Date")
    color_name = fields.Integer("Color index of creator",
                                compute='_compute_color_name', store=False)

    @api.constrains('maximum_marks', 'minimum_marks')
    def check_marks(self):
        if self.minimum_marks > self.maximum_marks:
            raise ValidationError(_('''Configure Maximum marks greater than
            minimum marks!'''))

    @api.model
    def create(self, vals):
        curr_dt = datetime.now()
        new_dt = datetime.strftime(curr_dt, '%m/%d/%Y')
        vals.update({'create_date': new_dt})
        return super(AdditionalExam, self).create(vals)

    @api.multi
    def write(self, vals):
        curr_dt = datetime.now()
        new_dt = datetime.strftime(curr_dt, '%m/%d/%Y')
        vals.update({'write_date': new_dt})
        return super(AdditionalExam, self).write(vals)


class ExamResult(models.Model):
    _name = 'exam.result'
    _inherit = ["mail.thread", "resource.mixin"]
    _rec_name = 'roll_no_id'
    _description = 'exam result Information'

    @api.depends('result_ids', 'result_ids.obtain_marks',
                 'result_ids.marks_reeval')
    def _compute_total(self):
        '''Method to compute total'''
        for rec in self:
            total = 0.0
            if rec.result_ids:
                for line in rec.result_ids:
                    obtain_marks = line.obtain_marks
                    if line.state == "re-evaluation":
                        obtain_marks = line.marks_reeval
                    total += obtain_marks
            rec.total = total

    @api.depends('total')
    def _compute_per(self):
        '''Method to compute percentage'''
        total = 0.0
        obtained_total = 0.0
        obtain_marks = 0.0
        per = 0.0
        for result in self:
            for sub_line in result.result_ids:
                if sub_line.state == "re-evaluation":
                    obtain_marks = sub_line.marks_reeval
                else:
                    obtain_marks = sub_line.obtain_marks
                total += sub_line.maximum_marks or 0
                obtained_total += obtain_marks
            if total > 1.0:
                per = (obtained_total / total) * 100
                if result.grade_system:
                    for grade_id in result.grade_system.grade_ids:
                        if per >= grade_id.from_mark and\
                                per <= grade_id.to_mark:
                            result.grade = grade_id.grade or ''
            result.percentage = per

    @api.depends('percentage')
    def _compute_result(self):
        '''Method to compute result'''
        for rec in self:
            flag = False
            if rec.result_ids:
                for grade in rec.result_ids:
                    if not grade.grade_line_id.fail:
                            rec.result = 'Pass'
                    else:
                        flag = True
            if flag:
                rec.result = 'Fail'

    @api.model
    def create(self, vals):
        if vals.get('student_id'):
            student = self.env['student.student'].browse(vals.get('student_id'
                                                                  ))
            vals.update({'roll_no_id': student.roll_no,
                         'standard_id': student.standard_id.id
                         })
        return super(ExamResult, self).create(vals)

    @api.multi
    def write(self, vals):
        if vals.get('student_id'):
            student = self.env['student.student'].browse(vals.get('student_id'
                                                                  ))
            vals.update({'roll_no_id': student.roll_no,
                         'standard_id': student.standard_id.id
                         })
        return super(ExamResult, self).write(vals)

    @api.multi
    def unlink(self):
        for rec in self:
            if rec.state != 'draft':
                raise ValidationError(_('''You can delete record in unconfirm
                state only!'''))
        return super(ExamResult, self).unlink()

    @api.onchange('student_id')
    def onchange_student(self):
        '''Method to get standard and roll no of student selected'''
        self.standard_id = False
        self.roll_no_id = False
        if self.student_id:
            self.standard_id = self.student_id.standard_id.id
            self.roll_no_id = self.student_id.roll_no

    s_exam_ids = fields.Many2one("exam.exam", "Examination", required=True,
                                 help="Select Exam")
    student_id = fields.Many2one("student.student", "Student Name",
                                 required=True,
                                 help="Select Student")
    roll_no_id = fields.Integer(string="Roll No",
                                readonly=True)
    pid = fields.Char(related='student_id.pid', string="Student ID",
                      readonly=True)
    standard_id = fields.Many2one("school.standard", "Standard",
                                  help="Select Standard")
    result_ids = fields.One2many("exam.subject", "exam_id", "Exam Subjects")
    total = fields.Float(compute='_compute_total', string='Obtain Total',
                         store=True, help="Total of marks")
    percentage = fields.Float("Percentage", compute="_compute_per",
                              store=True,
                              help="Percentage Obtained")
    result = fields.Char(compute='_compute_result', string='Result',
                         store=True, help="Result Obtained")
    grade = fields.Char("Grade", compute="_compute_per",
                        store=True, help="Grade Obtained")
    state = fields.Selection([('draft', 'Draft'),
                              ('confirm', 'Confirm'),
                              ('re-evaluation', 'Re-Evaluation'),
                              ('re-evaluation_confirm',
                               'Re-Evaluation Confirm'),
                              ('done', 'Done')],
                             'State', readonly=True,
                             track_visibility='onchange',
                             default='draft')
    color = fields.Integer('Color')
    active = fields.Boolean('Active', default=True)
    grade_system = fields.Many2one('grade.master', "Grade System",
                                   help="Grade System selected")
    message_ids = fields.One2many('mail.message', 'res_id', 'Messages',
                                  domain=lambda self: [('model', '=',
                                                        self._name)],
                                  auto_join=True)
    message_follower_ids = fields.One2many('mail.followers', 'res_id',
                                           'Followers',
                                           domain=lambda self: [('res_model',
                                                                 '=',
                                                                 self._name
                                                                 )])

    @api.multi
    def result_confirm(self):
        '''Method to confirm result'''
        for rec in self:
            for line in rec.result_ids:
                if line.maximum_marks == 0:
                    # Check subject marks not greater than maximum marks
                    raise ValidationError(_('Kindly add maximum\
                            marks of subject "%s".') % (line.subject_id.name))
                elif line.minimum_marks == 0:
                    raise ValidationError(_('Kindly add minimum\
                        marks of subject "%s".') % (line.subject_id.name))
                elif ((line.maximum_marks == 0 or line.minimum_marks == 0) and
                      line.obtain_marks):
                    raise ValidationError(_('Kindly add marks\
                        details of subject "%s"!') % (line.subject_id.name))
            vals = {'grade': rec.grade,
                    'percentage': rec.percentage,
                    'state': 'confirm'
                    }
            rec.write(vals)

    @api.multi
    def re_evaluation_confirm(self):
        '''Method to change state to re_evaluation_confirm'''
        self.state = 're-evaluation_confirm'

    @api.multi
    def result_re_evaluation(self):
        '''Method to set state to re-evaluation'''
        for rec in self:
            for line in rec.result_ids:
                line.marks_reeval = line.obtain_marks
            rec.state = 're-evaluation'

    @api.multi
    def set_done(self):
        '''Method to obtain history of student'''
        history_obj = self.env['student.history']
        for rec in self:
            vals = {'student_id': rec.student_id.id,
                    'academice_year_id': rec.student_id.year.id,
                    'standard_id': rec.standard_id.id,
                    'percentage': rec.percentage,
                    'result': rec.result}
            history = history_obj.search([('student_id', '=',
                                           rec.student_id.id),
                                          ('academice_year_id', '=',
                                           rec.student_id.year.id),
                                          ('standard_id', '=',
                                           rec.standard_id.id)
                                          ])
            if history:
                history_obj.write(vals)
            elif not history:
                history_obj.create(vals)
            rec.state = 'done'


class ExamGradeLine(models.Model):
    _name = "exam.grade.line"
    _description = 'Exam Subject Information'
    _rec_name = 'standard_id'

    standard_id = fields.Many2one('standard.standard', 'Standard')
    exam_id = fields.Many2one('exam.result', 'Result')
    grade = fields.Char('Grade')


class ExamSubject(models.Model):
    _name = "exam.subject"
    _description = 'Exam Subject Information'
    _rec_name = 'subject_id'

    @api.constrains('obtain_marks', 'minimum_marks', 'maximum_marks',
                    'marks_reeval')
    def _validate_marks(self):
        
        for rec in self:
            '''Method to validate marks'''
            if rec.obtain_marks > rec.maximum_marks:
                raise ValidationError(_('''The obtained marks
                should not extend maximum marks!'''))
            if rec.minimum_marks > rec.maximum_marks:
                raise ValidationError(_('''The minimum marks
                should not extend maximum marks!'''))
            if(rec.marks_reeval > rec.maximum_marks):
                raise ValidationError(_('''The revaluation marks
                should not extend maximum marks!'''))

    @api.depends('exam_id', 'obtain_marks', 'marks_reeval')
    def _compute_grade(self):
        '''Method to compute grade after re-evaluation'''
        for rec in self:
            grade_lines = rec.exam_id.grade_system.grade_ids
            if (rec.exam_id and rec.exam_id.student_id and grade_lines):
                for grade_id in grade_lines:
                    if rec.obtain_marks and rec.marks_reeval <= 0.0:
                        b_id = rec.obtain_marks <= grade_id.to_mark
                        if (rec.obtain_marks >= grade_id.from_mark and b_id):
                            rec.grade_line_id = grade_id
                    if rec.marks_reeval and rec.obtain_marks >= 0.0:
                        r_id = rec.marks_reeval <= grade_id.to_mark
                        if (rec.marks_reeval >= grade_id.from_mark and r_id):
                            rec.grade_line_id = grade_id

    exam_id = fields.Many2one('exam.result', 'Result')
    state = fields.Selection([('draft', 'Draft'), ('confirm', 'Confirm'),
                              ('re-evaluation', 'Re-Evaluation'),
                              ('re-evaluation_confirm',
                               'Re-Evaluation Confirm')],
                             related='exam_id.state', string="State")
    subject_id = fields.Many2one("subject.subject", "Subject Name")
    obtain_marks = fields.Float("Obtain Marks", group_operator="avg")
    minimum_marks = fields.Float("Minimum Marks",
                                 help="Minimum Marks of subject")
    maximum_marks = fields.Float("Maximum Marks",
                                 help="Maximum Marks of subject")
    marks_reeval = fields.Float("Marks After Re-evaluation",
                                help="Marks Obtain after Re-evaluation")
    grade_line_id = fields.Many2one('grade.line', "Grade",
                                    compute='_compute_grade')


class AdditionalExamResult(models.Model):
    _name = 'additional.exam.result'
    _description = 'subject result Information'
    _rec_name = 'roll_no_id'

    @api.depends('a_exam_id', 'obtain_marks')
    def _compute_student_result(self):
        '''Method to compute result of student'''
        for rec in self:
            if rec.a_exam_id and rec.a_exam_id:
                if rec.a_exam_id.minimum_marks < \
                        rec.obtain_marks:
                    rec.result = 'Pass'
                else:
                    rec.result = 'Fail'

    @api.model
    def create(self, vals):
        '''Override create method to get roll no and standard'''
        student = self.env['student.student'].browse(vals.get('student_id'))
        vals.update({'roll_no_id': student.roll_no,
                     'standard_id': student.standard_id.id
                     })
        return super(AdditionalExamResult, self).create(vals)

    @api.multi
    def write(self, vals):
        '''Override write method to get roll no and standard'''
        student = self.env['student.student'].browse(vals.get('student_id'))
        vals.update({'roll_no_id': student.roll_no,
                     'standard_id': student.standard_id.id
                     })
        return super(AdditionalExamResult, self).write(vals)

    @api.onchange('student_id')
    def onchange_student(self):
        ''' Method to get student roll no and standard by selecting student'''
        self.standard_id = self.student_id.standard_id.id
        self.roll_no_id = self.student_id.roll_no

    @api.constrains('obtain_marks')
    def _validate_obtain_marks(self):
        if self.obtain_marks > self.a_exam_id.subject_id.maximum_marks:
            raise ValidationError(_('''The obtained marks should not extend
                                    maximum marks!'''))

    a_exam_id = fields.Many2one('additional.exam', 'Additional Examination',
                                required=True,
                                help="Select Additional Exam")
    student_id = fields.Many2one('student.student', 'Student Name',
                                 required=True,
                                 help="Select Student")
    roll_no_id = fields.Integer("Roll No",
                                readonly=True)
    standard_id = fields.Many2one('school.standard',
                                  "Standard", readonly=True)
    obtain_marks = fields.Float('Obtain Marks', help="Marks obtain in exam")
    result = fields.Char(compute='_compute_student_result', string='Result',
                         help="Result Obtained", store=True)
    active = fields.Boolean('Active', default=True)
