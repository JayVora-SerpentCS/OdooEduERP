# -*- coding: utf-8 -*-
# Part of Odoo. See LICENSE file for full copyright and licensing details.

from openerp import models, fields, api, _
from openerp.exceptions import except_orm, Warning as UserError


class BoardBoard(models.Model):
    _inherit = 'board.board'


class ExtendedTimeTable(models.Model):
    _inherit = 'time.table'

    timetable_type = fields.Selection([('exam', 'Exam'),
                                       ('regular', 'Regular')],
                                      'Time Table Type', required=True)
    exam_id = fields.Many2one('exam.exam', 'Exam')


class ExtendedStudentStudent(models.Model):
    _inherit = 'student.student'

    exam_results_ids = fields.One2many('exam.result', 'student_id',
                                       'Exam History', readonly=True)


# class ExtendedTimeTableLine(models.Model):
#    _inherit = 'time.table.line'
#
#    exm_date = fields.Date('Exam Date')
#    day_of_week = fields.Char('Week Day')
#
#    @api.multi
#    def on_change_date_day(self, exm_date):
#        val = {}
#        if exm_date:
#            week_day = datetime.strptime(exm_date, "%Y-%m-%d")
#            val['week_day'] = week_day.strftime("%A").lower()
#        return {'value': val}
#
#    @api.multi
#    def _check_date(self):
#        for line in self:
#            if line.exm_date:
#                dt = datetime.strptime(line.exm_date, "%Y-%m-%d")
#                if line.week_day != dt.strftime("%A").lower():
#                    return False
#                elif dt.__str__() < datetime.strptime(date.today().__str__(),
#                                                      "%Y-%m-%d").__str__():
#                    raise except_orm(_('Invalid Date Error !'),
#                                     _('Either you have selected wrong day'
#                                       'for the date or you have selected'
#                                       'invalid date.'))
#        return True


class ExamExam(models.Model):
    _name = 'exam.exam'
    _description = 'Exam Information'
    
    @api.one
    @api.depends('exam_timetable_ids','exam_timetable_ids.standard_id')
    def _get_standards(self):
        self.standard_id = list(set([timetable.standard_id.id\
                        for timetable in self.exam_timetable_ids\
                        if timetable.standard_id]))

    @api.one
    @api.onchange('start_date','end_date')
    def _check_dates(self):
        if self.start_date and self.end_date:
            if self.start_date > self.end_date:
                raise except_orm(_('Warning'),
                                 _('Kindly check exam dates!'))

    name = fields.Char("Exam Name", required=True)
    exam_code = fields.Char('Exam Code', required=True, readonly=True,
                            default=lambda obj:
                            obj.env['ir.sequence'].get('exam.exam'))
    standard_id = fields.Many2many('school.standard',
                                   'school_standard_exam_rel', 'exam_id',
                                   'standard_id', 'Standards',
                                   compute="_get_standards")
    start_date = fields.Date("Exam Start Date",
                             help="Exam will start from this date")
    end_date = fields.Date("Exam End date", help="Exam will end at this date")
    create_date = fields.Date("Exam Created Date", help="Exam Created Date")
    write_date = fields.Date("Exam Update Date", help="Exam Update Date")
    exam_timetable_ids = fields.One2many('time.table', 'exam_id',
                                         'Exam Schedule')
    state = fields.Selection([('draft', 'Draft'),
                              ('confirm', 'Confirmed'),
                              ('running', 'Running'),
                              ('finished', 'Finished'),
                              ('cancelled', 'Cancelled')], 'State',
                             readonly=True, default='draft')

    @api.multi
    def set_to_draft(self):
        return self.write({'state': 'draft'})

    @api.multi
    def set_to_confirm(self):
        return self.write({'state' : 'confirm'})

    @api.multi
    def set_running(self):
        for rec in self:
            if not rec.exam_timetable_ids:
                raise except_orm(_('Exam Schedule'),
                                 _('You must add one Exam Schedule'))
            rec.write({'state': 'running'})
        return True

    @api.multi
    def set_finish(self):
        return self.write({'state': 'finished'})

    @api.multi
    def set_cancel(self):
        return self.write({'state': 'cancelled'})

    @api.multi
    def _validate_date(self):
        for exm in self:
            if exm.start_date > exm.end_date:
                return False
        return True


class AdditionalExam(models.Model):
    _name = 'additional.exam'
    _description = 'additional Exam Information'

    name = fields.Char("Additional Exam Name", required=True)
    addtional_exam_code = fields.Char('Exam Code', required=True,
                          readonly=True,
                          default=lambda obj:
                          obj.env['ir.sequence'].get('additional.exam'))
    standard_id = fields.Many2one("school.standard", "Standard")
    subject_id = fields.Many2one("subject.subject", "Subject Name")
    exam_date = fields.Date("Exam Date")
    maximum_marks = fields.Integer("Maximum Mark")
    minimum_marks = fields.Integer("Minimum Mark")
    weightage = fields.Char("WEIGHTAGE")
    create_date = fields.Date("Created Date", help="Exam Created Date")
    write_date = fields.Date("Updated date", help="Exam Updated Date")

    @api.onchange('standard_id')
    def on_change_stadard_name(self):
        val = {}
        if self.standard_id and self.standard_id.medium_id:
            val.update({'medium_id': self.standard_id.medium_id.id})
        if self.standard_id and self.standard_id.division_id:
            val.update({'division_id': self.standard_id.division_id.id})
        return {'value': val}


class ExamResult(models.Model):
    _name = 'exam.result'
    _rec_name = 's_exam_ids'
    _description = 'exam result Information'

    @api.one
    @api.depends('result_ids', 'result_ids.obtain_marks',
                 'result_ids.marks_reeval', 'result_ids.marks_access',
                 'state')
    def _compute_total(self):
        total = 0.0
        marks_total = 0.0
        eval_state = ['re-evaluation', 're-evaluation_confirm']
        acc_state = ['re-access', 're-access_confirm']
        for line in self.result_ids:
            marks_total += line.maximum_marks or 0
            obtain_marks = line.obtain_marks
            if line.state in eval_state and line.marks_reeval:
                obtain_marks = line.marks_reeval
            elif line.state in acc_state and line.marks_access:
                obtain_marks = line.marks_access
            total += obtain_marks
        self.total = total
        self.re_total = total
        if marks_total:
            self.percentage = (total / marks_total) * 100
            for grade_id in self.student_id.year.grade_id.grade_ids:
                if self.percentage >= grade_id.from_mark and\
                    self.percentage <= grade_id.to_mark:
                    self.grade = grade_id.grade
                    self.result = grade_id.fail and 'Fail' or 'Pass'

    @api.one
    @api.depends('percentage', 'student_id')
    def _compute_result(self):
        self.result = 'Fail'
        if self.student_id:
            if self.student_id.year.grade_id.grade_ids:
                for grade_id in self.student_id.year.grade_id.grade_ids:
                    if self.percentage >= grade_id.from_mark and \
                        self.percentage <= grade_id.to_mark:
                        self.result = grade_id.fail and 'Fail' or 'Pass'
            else:
                raise except_orm(_('Configuration Error !'),
                                 _('First Select Grade System in'
                                   'Student->year->.'))

    @api.onchange('student_id', 's_exam_ids', 'standard_id')
    def on_change_student(self):
        if not self.student_id:
            return {}
        if not self.s_exam_ids:
            raise except_orm(_('Input Error !'), _('First Select Exam.'))
        return {'value': {'standard_id': self.student_id.standard_id.id,
                          'roll_no_id': self.student_id.roll_no}}

    s_exam_ids = fields.Many2one("exam.exam", "Examination", required=True)
    student_id = fields.Many2one("student.student", "Student Name",
                                 required=True)
    roll_no_id = fields.Integer(related='student_id.roll_no',
                                string="Roll No",
                                readonly=True)
    pid = fields.Char(related='student_id.pid', string="Student ID",
                      readonly=True)
    standard_id = fields.Many2one("school.standard", "Standard",
                                  required=True)
    result_ids = fields.One2many("exam.subject", "exam_id",
                                 "Exam Subjects")
    total = fields.Float(compute='_compute_total', string='Obtain Total',
                         method=True, store=True)
    re_total = fields.Float(compute='_compute_total', string='Obtain Total',
                            readonly=True)
    percentage = fields.Float(compute='_compute_total', string="Percentage",
                              readonly=True)
    result = fields.Char(compute='_compute_result', string='Result',
                         readonly=True, method=True, store=True)
    grade = fields.Char(compute='_compute_result',string="Grade",
                        readonly=True)
    state = fields.Selection([('draft', 'Draft'),
                              ('confirm', 'Confirm'),
                              ('re-access', 'Re-Access'),
                              ('re-access_confirm', 'Re-Access-Confirm'),
                              ('re-evaluation', 'Re-Evaluation'),
                              ('re-evaluation_confirm',
                               'Re-Evaluation Confirm')],
                             'State', readonly=True, default='draft')
    color = fields.Integer('Color')

    @api.multi
    def result_confirm(self):
        return self.write({'state' : 'confirm'})

    @api.multi
    def result_re_access(self):
        self.write({'state': 're-access'})

    @api.multi
    def re_result_confirm(self):
        return self.write({'state': 're-access_confirm'})

    @api.multi
    def re_evaluation_confirm(self):
        return self.write({'state': 're-evaluation_confirm'})

    @api.multi
    def result_re_evaluation(self):
        return self.write({'state': 're-evaluation'})


class ExamGradeLine(models.Model):
    _name = "exam.grade.line"
    _description = 'Exam Subject Information'
    _rec_name = 'standard_id'

    standard_id = fields.Many2one('standard.standard', 'Standard')
    exam_id = fields.Many2one('exam.result', 'Result')
    grade = fields.Char(string='Grade')


class ExamSubject(models.Model):
    _name = "exam.subject"
    _description = 'Exam Subject Information'
    _rec_name = 'subject_id'

    @api.constrains('obtain_marks', 'minimum_marks')
    def _validate_marks(self):
        if (self.obtain_marks > self.maximum_marks
                or self.minimum_marks > self.maximum_marks):
            raise UserError(_('The obtained marks and minimum marks\
                             should not extend maximum marks.'))

    @api.one
    @api.depends('exam_id', 'obtain_marks',
                 'marks_access', 'marks_reeval',
                 'state')
    def _get_grade(self):
        eval_state = ['re-evaluation', 're-evaluation_confirm']
        acc_state = ['re-access', 're-access_confirm']
        if (self.exam_id and self.exam_id.student_id
                and self.exam_id.student_id.year.grade_id.grade_ids):
            marks = self.obtain_marks
            if self.state in eval_state and self.marks_reeval:
                marks = self.marks_reeval
            elif self.state in acc_state and self.marks_access:
                marks = self.marks_access
            for grade_id in self.exam_id.student_id.year.grade_id.grade_ids:
                if (marks >= grade_id.from_mark
                        and marks <= grade_id.to_mark):
                    self.grade = grade_id.grade

    exam_id = fields.Many2one('exam.result', 'Result')
    state = fields.Selection([('draft', 'Draft'), ('confirm', 'Confirm'),
                              ('re-access', 'Re-Access'),
                              ('re-access_confirm', 'Re-Access-Confirm'),
                              ('re-evaluation', 'Re-Evaluation'),
                              ('re-evaluation_confirm',
                               'Re-Evaluation Confirm')],
                             related='exam_id.state', string="State")
    subject_id = fields.Many2one("subject.subject", "Subject Name")
    obtain_marks = fields.Float("Obtain Marks", group_operator="avg")
    minimum_marks = fields.Float("Minimum Marks")
    maximum_marks = fields.Float("Maximum Marks")
    marks_access = fields.Float("Marks After Access")
    marks_reeval = fields.Float("Marks After Re-evaluation")
    grade_id = fields.Many2one('grade.master', "Grade")
    grade = fields.Char(compute='_get_grade', string='Grade', 
                        type="char", store=False)


class ExamResultBatchwise(models.Model):
    _name = 'exam.batchwise.result'
    _rec_name = 'standard_id'
    _description = 'exam result Information by Batch wise'

    @api.one
    @api.depends('standard_id', 'year')
    def compute_grade(self):
        total = 0.0
        lines = 0.0
        result_obj = self.env['exam.result']
        if self.standard_id and self.year:
            result_ids = result_obj.search([
                ('standard_id', '=', self.standard_id.id)])
            for result in result_ids:
                lines += len(result.result_ids)
                if result.state == 'confirm':
                    total += result.total
                elif result.state in ['re-evaluation_confirm', 're-access_confirm']:
                    total += result.re_total
            per = total / (lines or 1.0)
            for grade_id in self.year.grade_id.grade_ids:
                if (per >= grade_id.from_mark
                        and per <= grade_id.to_mark):
                    self.grade = grade_id.grade

    standard_id = fields.Many2one("school.standard", "Standard", required=True)
    year = fields.Many2one('academic.year', 'Academic Year', required=True)
    grade = fields.Char(compute='compute_grade', string='Grade', method=True)


class AdditionalExamResult(models.Model):
    _name = 'additional.exam.result'
    _description = 'subject result Information'

    @api.one
    @api.depends('a_exam_id', 'obtain_marks')
    def _calc_result(self):
        self.result = 'Fail'
        if (self.a_exam_id and self.a_exam_id.subject_id
                and self.a_exam_id.subject_id.minimum_marks):
            if self.a_exam_id.subject_id.minimum_marks <= self.obtain_marks:
                self.result = 'Pass'

    @api.onchange('student_id')
    def on_change_student(self):
        val = {}
        if self.student_id:
            val.update({'standard_id': self.student_id.standard_id.id,
                        'roll_no_id': self.student_id.roll_no})
        return {'value': val}

    @api.constrains('obtain_marks')
    def _validate_marks(self):
        if self.obtain_marks > self.a_exam_id.subject_id.maximum_marks:
            raise UserError(_('The obtained marks should not extend'
                            'maximum marks.'))
        return True

    a_exam_id = fields.Many2one('additional.exam', 'Additional Examination',
                                required=True)
    student_id = fields.Many2one('student.student', 'Student Name',
                                 required=True)
    roll_no_id = fields.Integer(related='student_id.roll_no',
                                string="Roll No", readonly=True)
    standard_id = fields.Many2one(related='student_id.standard_id',
                                  string="Standard", readonly=True)
    obtain_marks = fields.Float('Obtain Marks')
    result = fields.Char(compute='_calc_result', string='Result',
                         method=True)


class StudentStudent(models.Model):
    _name = 'student.student'
    _inherit = 'student.student'
    _description = 'Student Information'

    @api.model
    def name_search(self, name, args=None, operator='ilike', limit=100):
        context = self._context and dict(self._context) or {}
        args = args or []
        if context.get('exam', False):
            exam_data = self.env['exam.exam'].browse(context['exam'])
            std_ids = [std_id.id for std_id in exam_data.standard_id]
            args.append(('standard_id', 'in', std_ids))
        return super(StudentStudent, self).name_search(name, args=args, \
                                                       operator='ilike', \
                                                       limit=limit)

    @api.model
    def search(self, args, offset=0, limit=None, order=None, count=False):
        context = self._context and dict(self._context) or {}
        if args is None:
            args = []
        if context.get('exam', False):
            exam_data = self.env['exam.exam'].browse(context['exam'])
            std_ids = [std_id.id for std_id in exam_data.standard_id]
            args.append(('standard_id', 'in', std_ids))
        return super(StudentStudent, self).search(args=args, offset=offset,
                                                  limit=limit, order=order,
                                                  count=count)


class SchoolStandard(models.Model):
    ''' Defining a standard related to school '''
    _inherit = 'school.standard'

    @api.model
    def name_search(self, name, args=None, operator='ilike', limit=100):
        context = self._context and dict(self._context) or {}
        args = args or []
        if context.get('exam', False):
            exam_data = self.env['exam.exam'].browse(context['exam'])
            std_ids = [std_id.id for std_id in exam_data.standard_id]
            args.append(('id', 'in', std_ids))
        return super(SchoolStandard, self).name_search(name, args=args,\
                                                       operator='ilike',\
                                                       limit=limit)

    @api.model
    def search(self, args, offset=0, limit=None, order=None, count=False):
        context = self._context and dict(self._context) or {}
        if args is None:
            args = []
        if context.get('exam', False):
            exam_data = self.env['exam.exam'].browse(context['exam'])
            std_ids = [std_id.id for std_id in exam_data.standard_id]
            args.append(('id', 'in', std_ids))
        return super(SchoolStandard, self).search(args=args, offset=offset,
                                                  limit=limit, order=order,
                                                  count=count)