# -*- coding: utf-8 -*-
# See LICENSE file for full copyright and licensing details.

from datetime import date, datetime
from odoo import models, fields, api, _
from odoo.exceptions import ValidationError


class StudentStudent(models.Model):
    _inherit = 'student.student'
    _description = 'Student Information'

    exam_results_ids = fields.One2many('exam.result', 'student_id',
                                       'Exam History', readonly=True)

    @api.model
    def name_search(self, name='', args=None, operator='ilike',
                    limit=100):
        '''Overide method to get student according to exam'''
        args = args or []
        if self._context.get('exam'):
            exam_obj = self.env['exam.exam']
            exam_data = exam_obj.browse(self._context['exam'])
            std_ids = [std_id.id for std_id in exam_data.standard_id]
            args.append(('standard_id', 'in', std_ids))
        if self._context.get('a_exam'):
            add_exam = self.env['additional.exam']
            add_exam_data = add_exam.browse(self._context.get('a_exam'))
            standards = [stds_id.id for stds_id in add_exam_data.standard_id]
            args.append(('standard_id', 'in', standards))
        return super(StudentStudent, self).name_search(name=name, args=args,
                                                       operator=operator,
                                                       limit=limit)


class ExtendedTimeTable(models.Model):
    _inherit = 'time.table'

    timetable_type = fields.Selection(selection_add=[('exam', 'Exam')],
                                      string='Time Table Type', required=True,
                                      inivisible=False)
    exam_timetable_line_ids = fields.One2many('time.table.line', 'table_id',
                                              'TimeTable')
    exam_id = fields.Many2one('exam.exam', 'Exam')


class ExtendedTimeTableLine(models.Model):
    _inherit = 'time.table.line'

    exm_date = fields.Date('Exam Date')
    day_of_week = fields.Char('Week Day')

    @api.multi
    @api.onchange('exm_date')
    def onchange_date_day(self):
        '''Method to get weekday from date'''
        for rec in self:
            if rec.exm_date:
                week_day = datetime.strptime(rec.exm_date, "%Y-%m-%d")
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
                    raise ValidationError(_('Invalid Date Error !\
                        Either you have selected wrong day\
                                       for the date or you have selected\
                                       invalid date.'))
        return True


class ExamExam(models.Model):
    _name = 'exam.exam'
    _description = 'Exam Information'

    @api.constrains('start_date', 'end_date')
    def check_date_exam(self):
        '''Method to check constraint of exam start date and end date'''
        for rec in self:
            if rec.end_date < rec.start_date:
                raise ValidationError(_('Exam end date should be \
                                  greater than start date'))
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
                    examination results') % (self.name))

    active = fields.Boolean('Active', default="True")
    name = fields.Char("Exam Name", required=True)
    exam_code = fields.Char('Exam Code', required=True, readonly=True,
                            default=lambda obj:
                            obj.env['ir.sequence'].next_by_code('exam.exam'))
    standard_id = fields.Many2many('standard.standard',
                                   'standard_standard_exam_rel', 'standard_id',
                                   'event_id', 'Participant Standards')
    start_date = fields.Date("Exam Start Date",
                             help="Exam will start from this date")
    end_date = fields.Date("Exam End date", help="Exam will end at this date")
#    exam_timetable_ids = fields.One2many('time.table', 'exam_id',
#                                         'Exam Schedule')
    state = fields.Selection([('draft', 'Draft'),
                              ('running', 'Running'),
                              ('finished', 'Finished'),
                              ('cancelled', 'Cancelled')], 'State',
                             readonly=True, default='draft')
    grade_system = fields.Many2one('grade.master', "Grade System")
    academic_year = fields.Many2one('academic.year', 'Academic Year')
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
                raise ValidationError(_('Please Select Standard Id.'))
            if rec.exam_schedule_ids:
                rec.state = 'running'
            else:
                raise ValidationError(_('You must add one Exam Schedule'))
        return True

    @api.multi
    def set_finish(self):
        '''Method to set state to finish'''
        self.state = 'finished'

    @api.multi
    def set_cancel(self):
        '''Method to set state to cancel'''
        self.state = 'cancelled'

    @api.multi
    def _validate_date(self):
        '''Method to check start date should be less than end date'''
        for exm in self:
            if exm.start_date > exm.end_date:
                return False
        return True

    @api.multi
    def generate_result(self):
        '''Method to genrate result'''
        result_obj = self.env['exam.result']
        result_list = []
        for rec in self:
            for exam_schedule in rec.exam_schedule_ids:
                for student in exam_schedule.standard_id.student_ids:
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
                                   'grade_system': rec.grade_system.id}
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

    @api.multi
    @api.onchange('standard_ids')
    def onchange_standard(self):
        '''Method to get standard according to the standard selected'''
        standard_ids = []
        for rec in self:
            standard_ids = [std.id for std in rec.standard_ids]
        return {'domain': {'standard_id': [('standard_id', 'in',
                                            standard_ids)]}}

    standard_id = fields.Many2one('school.standard', 'Standard')
    timetable_id = fields.Many2one('time.table', 'Exam Schedule')
    exam_id = fields.Many2one('exam.exam', 'Exam')
    standard_ids = fields.Many2many('standard.standard',
                                    string='Participant Standards')


class AdditionalExam(models.Model):
    _name = 'additional.exam'
    _description = 'additional Exam Information'

    name = fields.Char("Additional Exam Name", required=True)
    addtional_exam_code = fields.Char('Exam Code', required=True,
                                      readonly=True,
                                      default=lambda obj:
                                      obj.env['ir.sequence'].
                                      next_by_code('additional.exam'))
    standard_id = fields.Many2one("school.standard", "Standard")
    subject_id = fields.Many2one("subject.subject", "Subject Name")
    exam_date = fields.Date("Exam Date")
    maximum_marks = fields.Integer("Maximum Mark")
    minimum_marks = fields.Integer("Minimum Mark")
    weightage = fields.Char("WEIGHTAGE")
    create_date = fields.Date("Created Date", help="Exam Created Date")
    write_date = fields.Date("Updated date", help="Exam Updated Date")


class ExamResult(models.Model):
    _name = 'exam.result'
    _rec_name = 'roll_no_id'
    _description = 'exam result Information'

    @api.multi
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

    @api.multi
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
        return True

    @api.multi
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

    @api.onchange('student_id')
    def onchange_student(self):
        '''Method to get standard and roll no of student selected'''
        if self.student_id:
            self.standard_id = self.student_id.standard_id.id
            self.roll_no_id = self.student_id.roll_no

    s_exam_ids = fields.Many2one("exam.exam", "Examination", required=True)
    student_id = fields.Many2one("student.student", "Student Name",
                                 required=True)
    roll_no_id = fields.Integer(string="Roll No",
                                readonly=True)
    pid = fields.Char(related='student_id.pid', string="Student ID",
                      readonly=True)
    standard_id = fields.Many2one("school.standard", "Standard")
    result_ids = fields.One2many("exam.subject", "exam_id", "Exam Subjects")
    total = fields.Float(compute='_compute_total', string='Obtain Total',
                         store=True)
    percentage = fields.Float("Percentage", compute="_compute_per",
                              store=True)
    result = fields.Char(compute='_compute_result', string='Result',
                         store=True)
    grade = fields.Char("Grade", compute="_compute_per",
                        store=True)
    state = fields.Selection([('draft', 'Draft'),
                              ('confirm', 'Confirm'),
                              ('re-evaluation', 'Re-Evaluation'),
                              ('re-evaluation_confirm',
                               'Re-Evaluation Confirm'),
                              ('done', 'Done')],
                             'State', readonly=True, default='draft')
    color = fields.Integer('Color')
    grade_system = fields.Many2one('grade.master', "Grade System")

    @api.multi
    def result_confirm(self):
        for rec in self:
            for line in rec.result_ids:
                if line.maximum_marks == 0:
                    raise ValidationError(_('Kindly add maximum\
                            marks of subject "%s".') % (line.subject_id.name))
                elif line.minimum_marks == 0:
                    raise ValidationError(_('Kindly add minimum\
                        marks of subject "%s".') % (line.subject_id.name))
                elif ((line.maximum_marks == 0 or line.minimum_marks == 0) and
                      line.obtain_marks):
                    raise ValidationError(_('Kindly add marks\
                        details of subject "%s".') % (line.subject_id.name))
            vals = {'grade': rec.grade,
                    'percentage': rec.percentage,
                    'state': 'confirm'
                    }
            rec.write(vals)
        return True

    @api.multi
    def re_evaluation_confirm(self):
        '''Method to change state to re_evaluation_confirm'''
        for rec in self:
            rec.state = 're-evaluation_confirm'
        return True

    @api.multi
    def result_re_evaluation(self):
        '''Method to set state to re-evaluation'''
        for rec in self:
            for line in rec.result_ids:
                line.marks_reeval = line.obtain_marks
            rec.state = 're-evaluation'
        return True

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
            rec.write({'state': 'done'})
        return True


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

    @api.constrains('obtain_marks', 'minimum_marks')
    def _validate_marks(self):
        '''Method to validate marks'''
        min_mark = self.minimum_marks > self.maximum_marks
        if (self.obtain_marks > self.maximum_marks or min_mark):
            raise ValidationError(_('The obtained marks and minimum marks\
                              should not extend maximum marks.'))

    @api.multi
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
    minimum_marks = fields.Float("Minimum Marks")
    maximum_marks = fields.Float("Maximum Marks")
    marks_reeval = fields.Float("Marks After Re-evaluation")
    grade_line_id = fields.Many2one('grade.line', "Grade",
                                    compute='_compute_grade')


class AdditionalExamResult(models.Model):
    _name = 'additional.exam.result'
    _description = 'subject result Information'
    _rec_name = 'roll_no_id'

    @api.multi
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
    def _validate_marks(self):
        if self.obtain_marks > self.a_exam_id.subject_id.maximum_marks:
            raise ValidationError(_('''The obtained marks should not extend
                              maximum marks.'''))
        return True

    a_exam_id = fields.Many2one('additional.exam', 'Additional Examination',
                                required=True)
    student_id = fields.Many2one('student.student', 'Student Name',
                                 required=True)
    roll_no_id = fields.Integer("Roll No",
                                readonly=True)
    standard_id = fields.Many2one('school.standard',
                                  "Standard", readonly=True)
    obtain_marks = fields.Float('Obtain Marks')
    result = fields.Char(compute='_compute_student_result', string='Result')
