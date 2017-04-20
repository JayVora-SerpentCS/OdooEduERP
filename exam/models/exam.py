# -*- coding: utf-8 -*-
# See LICENSE file for full copyright and licensing details.

from datetime import date, datetime
from odoo import models, fields, api, _
from odoo.exceptions import UserError, Warning as UserError


class BoardBoard(models.AbstractModel):
    _inherit = 'board.board'


class ExtendedTimeTable(models.Model):
    _inherit = 'time.table'

    timetable_type = fields.Selection([('exam', 'Exam'),
                                       ('regular', 'Regular')],
                                      'Time Table Type', required=True)
    exam_id = fields.Many2one('exam.exam', 'Exam')


class StudentStudent(models.Model):
    _inherit = 'student.student'
    _description = 'Student Information'

    exam_results_ids = fields.One2many('exam.result', 'student_id',
                                       'Exam History', readonly=True)

    @api.model
    def search(self, args, offset=0, limit=None, order=None, count=False):
        if self._context.get('exam'):
            exam_obj = self.env['exam.exam']
            exam_data = exam_obj.browse(self._context['exam'])
            std_ids = [std_id.id for std_id in exam_data.standard_id]
            args.append(('class_id', 'in', std_ids))
        return super(StudentStudent, self).search(args=args, offset=offset,
                                                  limit=limit, order=order,
                                                  count=count)


class ExtendedTimeTableLine(models.Model):
    _inherit = 'time.table.line'

    exm_date = fields.Date('Exam Date')
    day_of_week = fields.Char('Week Day')

    @api.multi
    def on_change_date_day(self, exm_date):
        val = {}
        if exm_date:
            week_day = datetime.strptime(exm_date, "%Y-%m-%d")
            val['week_day'] = week_day.strftime("%A").lower()
        return {'value': val}

    @api.multi
    def _check_date(self):
        for line in self:
            if line.exm_date:
                dt = datetime.strptime(line.exm_date, "%Y-%m-%d")
                if line.week_day != dt.strftime("%A").lower():
                    return False
                elif dt.__str__() < datetime.strptime(date.today().__str__(),
                                                      "%Y-%m-%d").__str__():
                    raise UserError(_('Invalid Date Error !\
                        Either you have selected wrong day\
                                       for the date or you have selected\
                                       invalid date.'))
        return True


class ExamExam(models.Model):
    _name = 'exam.exam'
    _description = 'Exam Information'

    @api.constrains('start_date', 'end_date')
    def check_date_exam(self):
        if self.end_date < self.start_date:
            raise UserError(_('End date of Exam should be \
                              greater than start date'))

    name = fields.Char("Exam Name", required=True)
    exam_code = fields.Char('Exam Code', required=True, readonly=True,
                            default=lambda obj:
                            obj.env['ir.sequence'].next_by_code('exam.exam'))
    standard_id = fields.Many2many('school.standard',
                                   'school_standard_exam_rel', 'standard_id',
                                   'event_id', 'Participant Standards')
    start_date = fields.Date("Exam Start Date",
                             help="Exam will start from this date")
    end_date = fields.Date("Exam End date", help="Exam will end at this date")
    create_date = fields.Date("Exam Created Date", help="Exam Created Date")
    write_date = fields.Date("Exam Update Date", help="Exam Update Date")
    exam_timetable_ids = fields.One2many('time.table', 'exam_id',
                                         'Exam Schedule')
    state = fields.Selection([('draft', 'Draft'),
                              ('running', 'Running'),
                              ('finished', 'Finished'),
                              ('cancelled', 'Cancelled')], 'State',
                             readonly=True, default='draft')
    grade_system = fields.Many2one('grade.master', "Grade System")

    @api.multi
    def set_to_draft(self):
        self.state = 'draft'

    @api.multi
    def set_running(self):
        if self.exam_timetable_ids:
            self.state = 'running'
        else:
            raise UserError(_('Exam Schedule\
                             You must add one Exam Schedule'))

    @api.multi
    def set_finish(self):
        self.state = 'finished'

    @api.multi
    def set_cancel(self):
        self.state = 'cancelled'

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

    @api.multi
    def on_change_stadard_name(self, standard_id):
        val = {}
        school_standard_obj = self.env['school.standard']
        school_line = school_standard_obj.browse(standard_id)
        if school_line.medium_id.id:
            val['medium_id'] = school_line.medium_id.id
        if school_line.division_id.id:
            val['division_id'] = school_line.division_id.id
        return {'value': val}


class ExamResult(models.Model):
    _name = 'exam.result'
    _rec_name = 's_exam_ids'
    _description = 'exam result Information'

    @api.multi
    @api.depends('result_ids', 'result_ids.obtain_marks')
    def _compute_total(self):
        for rec in self:
            total = 0.0
            if rec.result_ids:
                for line in rec.result_ids:
                    obtain_marks = line.obtain_marks
                    if line.state == "re-evaluation":
                        obtain_marks = line.marks_reeval
                    elif line.state == "re-access":
                        obtain_marks = line.marks_access
                    total += obtain_marks
            rec.total = total

    @api.multi
    @api.depends('result_ids', 'result_ids.obtain_marks')
    def _compute_per(self):
        total = 0.0
        obtained_total = 0.0
        obtain_marks = 0.0
        per = 0.0
        for result in self:
            for sub_line in result.result_ids:
                if sub_line.state == "re-evaluation":
                    obtain_marks = sub_line.marks_reeval
                elif sub_line.state == "re-access":
                    obtain_marks = sub_line.marks_access
                obtain_marks = sub_line.obtain_marks
                total += sub_line.maximum_marks or 0
                obtained_total += obtain_marks
            if total > 1.0:
                per = (obtained_total / total) * 100
                if result.grade_system:
                    for grade_id in result.grade_system.grade_ids:
                        if per >= grade_id.from_mark\
                            and per <= grade_id.to_mark:
                            result.grade = grade_id.grade or ''
                result.percentage = per
        return True

    @api.multi
    @api.depends('result_ids')
    def _compute_result(self):
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

    @api.multi
    def on_change_student(self, student, exam_id, standard_id):
        if not student:
            return True
        if not exam_id:
            raise UserError(_('Input Error ! First Select Exam.'))
        student_obj = self.env['student.student']
        student_data = student_obj.browse(student)
        self.standard_id = student_data.standard_id.id
        self.roll_no_id = student_data.roll_no
        return True

    s_exam_ids = fields.Many2one("exam.exam", "Examination", required=True)
    student_id = fields.Many2one("student.student", "Student Name",
                                 required=True)
    roll_no_id = fields.Integer(related='student_id.roll_no', string="Roll No",
                                readonly=True)
    pid = fields.Char(related='student_id.pid', string="Student ID",
                      readonly=True)
    standard_id = fields.Many2one("school.standard", "Standard", required=True)
    result_ids = fields.One2many("exam.subject", "exam_id", "Exam Subjects")
    total = fields.Float(compute='_compute_total', string='Obtain Total',
                         method=True, store=True)
    re_total = fields.Float('Re-access Obtain Total', readonly=True)
    percentage = fields.Float("Percentage", compute="_compute_per",
                              readonly=True, store=True)
    result = fields.Char(compute='_compute_result', string='Result',
                         readonly=True, method=True, store=True)
    grade = fields.Char("Grade", compute="_compute_per",
                              readonly=True, store=True)
    state = fields.Selection([('draft', 'Draft'),
                              ('confirm', 'Confirm'),
                              ('re-access', 'Re-Access'),
                              ('re-access_confirm', 'Re-Access-Confirm'),
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
                    raise UserError(_('Warning!'),
                             _('Kindly add maximum marks of subject\
                             "%s".') % (line.subject_id.name))
                elif line.minimum_marks == 0:
                    raise UserError(_('Warning!'),
                             _('Kindly add minimum marks of subject\
                             "%s".') % (line.subject_id.name))
                elif ((line.maximum_marks == 0 or
                       line.minimum_marks == 0)
                      and line.obtain_marks):
                    raise UserError(_('Warning!'),
                            _('Kindly add marks details of subject \
                                   "%s".') % (line.subject_id.name))
            vals = {'grade': rec.grade,
                     'percentage': rec.percentage,
                     'state': 'confirm'}
            self.write(vals)
        return True

    @api.multi
    def result_re_access(self):
        self.state = 're-access'

    @api.multi
    def re_result_confirm(self):
        res = {}
        opt_marks = []
        acc_mark = []
        total = 0.0
        per = 0.0
        grd = 0.0
        add = 0.0
        for result in self:
            for sub_line in result.result_ids:
                opt_marks.append(sub_line.obtain_marks)
                acc_mark.append(sub_line.marks_access)
                total += sub_line.maximum_marks or 0.0
            for i in range(0, len(opt_marks)):
                if acc_mark[i] != 0.0:
                    opt_marks[i] = acc_mark[i]
            for i in range(0, len(opt_marks)):
                add = add + opt_marks[i]

            if total > 1.0:
                per = (add / total) * 100
                for grade_id in result.grade_system.grade_ids:
                    if per >= grade_id.from_mark and per <= grade_id.to_mark:
                        grd = grade_id.grade
                res.update({'grade': grd,
                            'percentage': per,
                            'state': 're-access_confirm',
                            're_total': add})
            self.write(res)
        return True

    @api.multi
    def re_evaluation_confirm(self):
        res = {}
        opt_marks = []
        eve_marks = []
        add = 0.0
        total = 0.0
        per = 0.0
        grd = 0.0
        for result in self:
            for sub_line in result.result_ids:
                opt_marks.append(sub_line.obtain_marks)
                eve_marks.append(sub_line.marks_reeval)
                total += sub_line.maximum_marks or 0.0
            for i in range(0, len(opt_marks)):
                if eve_marks[i] != 0.0:
                    opt_marks[i] = eve_marks[i]
            for i in range(0, len(opt_marks)):
                add += opt_marks[i]

            if total > 1.0:
                # Sum cannot be used here as it is reserved keyword
                per = (add / total) * 100
                for grade_id in result.grade_system.grade_ids:
                    if per >= grade_id.from_mark and per <= grade_id.to_mark:
                        grd = grade_id.grade
                res.update({'grade': grd,
                            'percentage': per,
                            'state': 're-evaluation_confirm',
                            're_total': add})
            self.write(res)
        return True

    @api.multi
    def result_re_evaluation(self):
        self.state = 're-evaluation'
        return True

    @api.multi
    def set_done(self):
        history_obj = self.env['student.history']
        for rec in self:
            vals = {'student_id': rec.student_id.id,
                    'academice_year_id': rec.student_id.year.id,
                    'standard_id': rec.standard_id.id,
                    'percentage': rec.percentage,
                    'result': rec.result}
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
        min_mark = self.minimum_marks > self.maximum_marks
        if (self.obtain_marks > self.maximum_marks or min_mark):
            raise UserError(_('The obtained marks and minimum marks\
                              should not extend maximum marks.'))

    @api.multi
    @api.depends('exam_id', 'obtain_marks')
    def _compute_grade(self):
        for rec in self:
            grade_lines = rec.exam_id.grade_system.grade_ids
            if (rec.exam_id and rec.exam_id.student_id and grade_lines):
                for grade_id in grade_lines:
                    b_id = rec.obtain_marks <= grade_id.to_mark
                    if (rec.obtain_marks >= grade_id.from_mark and b_id):
                        # rec.grade = grade_id.grade
                        rec.grade_line_id = grade_id

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
    grade_line_id = fields.Many2one('grade.line', "Grade",
                                    compute='_compute_grade')
    # grade = fields.Char(compute='_compute_grade', string='Grade')


class ExamResultBatchwise(models.Model):
    _name = 'exam.batchwise.result'
    _rec_name = 'standard_id'
    _description = 'exam result Information by Batch wise'

    @api.multi
    @api.depends('standard_id', 'year')
    def _compute_student_grade(self):
        for rec in self:
            fina_tot = 0
            count = 0
            divi = 0
            year_obj = self.env['academic.year']
            stud_obj = self.env['exam.result']
            if rec.standard_id and rec.year:
                year_ob = year_obj.browse(rec.year.id)
                stand_id = stud_obj.search([
                    ('standard_id', '=', rec.standard_id.id)])
                for stand in stand_id:
                    student_ids = stud_obj.browse(stand.id)
                    if student_ids.result_ids:
                        count += 1
                        fina_tot += student_ids.total
                    divi = fina_tot / count
                    # Total_obtained mark of all student
                    if year_ob.grade_id.grade_ids:
                        # divis = divi <= year_ob.grade_id.to_mark
                        for grade_id in year_ob.grade_id.grade_ids:
                            if (divi >= grade_id.from_mark and
                                divi <= grade_id.to_mark):
                                rec.grade = grade_id.grade
    standard_id = fields.Many2one("school.standard", "Standard", required=True)
    year = fields.Many2one('academic.year', 'Academic Year', required=True)
    grade = fields.Char(compute='_compute_student_grade', string='Grade',
                        method=True,
                        store=True)


class AdditionalExamResult(models.Model):
    _name = 'additional.exam.result'
    _description = 'subject result Information'
    _rec_name = 'a_exam_id'

    @api.multi
    @api.depends('a_exam_id', 'obtain_marks')
    def _compute_student_result(self):
        for rec in self:
            min_m = rec.a_exam_id.subject_id.minimum_marks
            if (rec.a_exam_id and rec.a_exam_id.subject_id and min_m):
                if rec.a_exam_id.subject_id.minimum_marks <= rec.obtain_marks:
                    rec.result = 'Pass'
                else:
                    rec.result = 'Fail'

    @api.multi
    def on_change_student(self, student):
        val = {}
        student_obj = self.env['student.student']
        student_data = student_obj.browse(student)
        val.update({'standard_id': student_data.standard_id.id,
                    'roll_no_id': student_data.roll_no})
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
    roll_no_id = fields.Integer(related='student_id.roll_no', string="Roll No",
                                readonly=True)
    standard_id = fields.Many2one(related='student_id.standard_id',
                                  string="Standard", readonly=True)
    obtain_marks = fields.Float('Obtain Marks')
    result = fields.Char(compute='_compute_student_result', string='Result',
                         method=True)
