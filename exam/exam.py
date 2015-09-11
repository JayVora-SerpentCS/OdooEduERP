# -*- encoding: utf-8 -*-
##############################################################################
#
#    OpenERP, Open Source Management Solution
#    Copyright (C) 2004-2009 Tiny SPRL (<http://tiny.be>).
#    Copyright (C) 2011-2012 Serpent Consulting Services
#    (<http://www.serpentcs.com>)
#    Copyright (C) 2013-2014 Serpent Consulting Services
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
from datetime import date, datetime
from openerp import models, fields, api, _
from openerp.exceptions import Warning


class extended_time_table(models.Model):

    _inherit = 'time.table'

    timetable_type = fields.Selection([('exam', 'Exam'),
                                       ('regular', 'Regular')],
                                      "Time Table Type", required=True)
    exam_id = fields.Many2one('exam.exam', 'Exam')


class extended_student_student(models.Model):

    _inherit = 'student.student'

    exam_results_ids = fields.One2many('exam.result', 'student_id',
                                       'Exam History', readonly=True)


class extended_time_table_line(models.Model):

    _inherit = 'time.table.line'

    exm_date = fields.Date('Exam Date')
    day_of_week = fields.Char('Week Day')

    @api.multi
    @api.onchange('exm_date')
    def on_change_date_day(self):
        val = {}
        if self.exm_date:
            val['week_day'] = datetime.strptime
            (self.exm_date, "%Y-%m-%d").strftime("%A").lower()
        return {'value': val}

    @api.multi
    def _check_date(self):
        for line in self:
            if line.exm_date:
                dt = datetime.strptime(line.exm_date, "%Y-%m-%d")
                if line.week_day != datetime.strptime(line.exm_date,
                                                      "%Y-%m-%d"). \
                                                      strftime("%A"). \
                                                      lower():
                    return False
                elif dt.__str__() < datetime.strptime(date.today().__str__(),
                                                      "%Y-%m-%d").__str__():
                    raise Warning(_('Invalid Date Error !'),
                                  _('Either you''have selected wrong day'
                                    'for the date or you have selected'
                                    'invalid date.'))
        return True


class exam_exam(models.Model):

    _name = 'exam.exam'
    _description = 'Exam Information'

    name = fields.Char("Exam Name", required=True)
    exam_code = fields.Char('Exam Code', required=True, readonly=True,
                            default=lambda obj: obj.env['ir.sequence'].
                            get('exam.exam'))
    standard_id = fields.Many2many('school.standard',
                                   'school_standard_exam_rel', 'standard_id',
                                   'event_id', 'Participant Standards')
    start_date = fields.Date("Exam Start Date",
                             help="Exam will start from this date")
    end_date = fields.Date("Exam End date", help="Exam will end at this date")
    create_date = fields.Date("Exam Created Date", help="Exam Created Date")
    write_date = fields.Date("Exam Update Date", help="Exam Update Date")
    timetable_ids = fields.One2many('time.table.line', 'tables_id',
                                    'TimeTable')
    state = fields.Selection([('draft', 'Draft'), ('running', 'Running'),
                              ('finished', 'Finished'),
                              ('cancelled', 'Cancelled')], 'State',
                             readonly=True, default='draft')

    @api.multi
    def set_to_draft(self):
        self.write({'state': 'draft'})

    @api.multi
    def set_running(self):
        if self.exam_timetable_ids:
            self.write({'state': 'running'})
        else:
            raise Warning(_('Exam Schedule'), _('You must add one'
                                                'Exam Schedule'))

    @api.multi
    def set_finish(self):
        self.write({'state': 'finished'})

    @api.multi
    def set_cancel(self):
        self.write({'state': 'cancelled'})

    @api.multi
    def _validate_date(self):
        for exm in self:
            if exm.start_date > exm.end_date:
                return False
        return True


class additional_exam(models.Model):

    _name = 'additional.exam'
    _description = 'additional Exam Information'

    name = fields.Char("Additional Exam Name", required=True)
    addtional_exam_code = fields.Char('Exam Code', required=True,
                                      readonly=True,
                                      default=lambda obj: obj.
                                      env['ir.sequence'].
                                      get('additional.exam'))
    standard_id = fields.Many2one("school.standard", "Standard")
    subject_id = fields.Many2one("subject.subject", "Subject Name")
    exam_date = fields.Date("Exam Date")
    maximum_marks = fields.Integer("Maximum Mark")
    minimum_marks = fields.Integer("Minimum Mark")
    weightage = fields.Char("Weightage")
    create_date = fields.Date("Created Date", help="Exam Created Date")
    write_date = fields.Date("Updated date", help="Exam Updated Date")

    @api.multi
    @api.onchange('standard_id')
    def onchange_ad_standard(self):
        sub_list = []
        for exam_obj in self:
            for time_table in exam_obj.standard_id:
                for sub_id in time_table.subject_ids:
                    sub_list.append(sub_id.id)
            return {'domain': {'subject_id': [('id', 'in', sub_list)]}}


class exam_result(models.Model):

    _name = 'exam.result'
    _rec_name = 's_exam_ids'
    _description = 'exam result Information'

    @api.one
    @api.depends('result_ids')
    def _compute_total(self):
        total = 0.0
        for total_obj in self:
            if total_obj.result_ids:
                for line in total_obj.result_ids:
                    obtain_marks = line.obtain_marks
                    if line.state == "re-evaluation":
                        obtain_marks = line.marks_reeval
                    elif line.state == "re-access":
                        obtain_marks = line.marks_access
                    total += obtain_marks
                total_obj.total = total

    @api.multi
    def _compute_per(self):
        res = {}
        for result in self.browse(self.ids):
            total = 0.0
            obtained_total = 0.0
            obtain_marks = 0.0
            per = 0.0
            grd = ""
            for sub_line in result.result_ids:
                if sub_line.state == "re-evaluation":
                    obtain_marks = sub_line.marks_reeval
                elif sub_line.state == "re-access":
                    obtain_marks = sub_line.marks_access
                obtain_marks = sub_line.obtain_marks
                total += sub_line.maximum_marks or 0
                obtained_total += obtain_marks
            if total != 0.0:
                per = (obtained_total / total) * 100
                for grade_id in result.student_id.year.grade_id.grade_ids:
                    if per >= grade_id.from_mark and per <= grade_id.to_mark:
                        grd = grade_id.grade
                res[result.id] = {'percentage': per, 'grade': grd}
        return res

    @api.multi
    @api.depends('result_ids', 'student_id')
    def _compute_result(self):
        flag = False
        for result_obj in self:
            if result_obj.result_ids and result_obj.student_id:
                if result_obj.student_id.year.grade_id.grade_ids:
                    for grades in result_obj.student_id.year.grade_id \
                            .grade_ids:
                        if grades.grade:
                            if not grades.fail:
                                result_obj.result = 'Pass'
                            else:
                                flag = True
                else:
                    raise Warning(_('Configuration Error !'),
                                  _('First Select Grade System'
                                    'in Student->year->.'))
            if flag:
                result_obj.result = 'Fail'

    @api.multi
    @api.onchange('student_id')
    def on_change_student(self):
        #         student_lst = []
        #         attendence_lst = []
        attendence_line_obj = self.env['daily.attendance.line']
        tt_line_obj = self.env['time.table.line']
        for rec in self:
            #             student_id = rec.student_id.id
            for line in rec.result_ids:
                tt_lines = tt_line_obj.search([('subject_id', '=',
                                                line.subject_id.id),
                                               ('tables_id', '=',
                                                rec.s_exam_ids.id)])
                if tt_lines:
                    exam_date = tt_lines[0].sub_exam_date
                    attendace_lines = attendence_line_obj \
                        .search([('stud_id', '=', rec.student_id.id),
                                 ('standard_id.date', '=', exam_date)])
                    if attendace_lines:
                        line.absent = attendace_lines[0].is_absent

    @api.onchange('s_exam_ids')
    def onchange_exam(self):
        standard_lst = []
        #         sub_res = {}
        for exam_obj in self:
            for rec in exam_obj.s_exam_ids.standard_id:
                standard_lst.append(rec.id)
        return {'domain': {'standard_id': [('id', 'in', standard_lst)]}}

    @api.onchange('standard_id')
    def onchange_standard(self):
        student_lst = []
        sub_list = []
        for standard_obj in self:
            for exam_student_rec in standard_obj.standard_id.student_ids:
                student_lst.append(exam_student_rec.id)
            for time_table in standard_obj.s_exam_ids.timetable_ids:
                if time_table.standard_id.id == standard_obj.standard_id.id:
                    for sub_id in time_table.subject_id:
                        sub_val = {'subject_id': sub_id.id
                                   }
                        sub_list.append(sub_val)
        standard_obj.result_ids = sub_list
        return {'domain': {'student_id': [('id', 'in', student_lst)]}}

    s_exam_ids = fields.Many2one("exam.exam", "Examination",
                                 required=True)
    student_id = fields.Many2one("student.student", "Student Name",
                                 required=True)

    roll_no_id = fields.Integer(related='student_id.roll_no',
                                string="Roll No", readonly=True)
    pid = fields.Char(related='student_id.pid', string="Student ID",
                      readonly=True)
    standard_id = fields.Many2one("school.standard", "Standard",
                                  required=True)
    result_ids = fields.One2many("exam.subject", "exam_id", "Exam Subjects")
    total = fields.Float(compute='_compute_total', string='Obtain Total',
                         method=True, store=True)
    re_total = fields.Float('Re-access Obtain Total', readonly=True)
    percentage = fields.Float("Percentage", readonly=True)
    result = fields.Char(compute='_compute_result', string='Result',
                         readonly=True, method=True, store=True)
    grade = fields.Char("Grade", readonly=True)
    state = fields.Selection([('draft', 'Draft'), ('confirm', 'Confirm'),
                              ('re-access', 'Re-Access'),
                              ('re-access_confirm', 'Re-Access-Confirm'),
                              ('re-evaluation', 'Re-Evaluation'),
                              ('re-evaluation_confirm',
                               'Re-Evaluation Confirm')],
                             'State', readonly=True, default='draft')
    color = fields.Integer('Color')

    @api.multi
    def result_confirm(self):
        vals = {}
        res = self._compute_per()
        if not res:
            raise Warning(_('Warning!'), _('Please Enter the'
                                           'students Marks.'))
        vals.update({'grade': res[self.id]['grade'],
                     'percentage': res[self.id]['percentage'],
                     'state': 'confirm'})
        self.write(vals)
        return True

    @api.multi
    def result_re_access(self):
        self.write({'state': 're-access'})

    @api.multi
    def re_result_confirm(self):
        res = {}
        for result in self.browse(self.ids):
            opt_marks = []
            acc_mark = []
            sum1 = 0.0
            total = 0.0
#             obtained_total = 0.0
#             obtain_marks = 0.0
            per = 0.0
            grd = 0.0
            for sub_line in result.result_ids:
                opt_marks.append(sub_line.obtain_marks)
                acc_mark.append(sub_line.marks_access)
            for i in range(0, len(opt_marks)):
                if acc_mark[i] != 0.0:
                    opt_marks[i] = acc_mark[i]
            for i in range(0, len(opt_marks)):
                sum1 = sum1 + opt_marks[i]
                total += sub_line.maximum_marks or 0
            if total != 0.0:
                per = (sum1 / total) * 100
                for grade_id in result.student_id.year.grade_id.grade_ids:
                    if per >= grade_id.from_mark and per <= grade_id.to_mark:
                        grd = grade_id.grade
                res.update({'grade': grd, 'percentage': per,
                            'state': 're-access_confirm', 're_total': sum1})
            self.write(res)
        return True

    @api.multi
    def re_evaluation_confirm(self):
        res = {}
        for result in self.browse(self.ids):
            opt_marks = []
            eve_marks = []
            sum1 = 0.0
            total = 0.0
#             obtained_total = 0.0
#             obtain_marks = 0.0
            per = 0.0
            grd = 0.0
            for sub_line in result.result_ids:
                opt_marks.append(sub_line.obtain_marks)
                eve_marks.append(sub_line.marks_reeval)
            for i in range(0, len(opt_marks)):
                if eve_marks[i] != 0.0:
                    opt_marks[i] = eve_marks[i]
            for i in range(0, len(opt_marks)):
                sum1 = sum + opt_marks[i]
                total += sub_line.maximum_marks or 0
            if total != 0.0:
                per = (sum1 / total) * 100
                for grade_id in result.student_id.year.grade_id.grade_ids:
                    if per >= grade_id.from_mark and per <= grade_id.to_mark:
                        grd = grade_id.grade
                res.update({'grade': grd, 'percentage': per,
                            'state': 're-evaluation_confirm',
                            're_total': sum1})
            self.write(res)
        return True

    @api.multi
    def result_re_evaluation(self):
        self.write({'state': 're-evaluation'})
        return True


class exam_grade_line(models.Model):
    _name = "exam.grade.line"
    _description = 'Exam Subject Information'
    _rec_name = 'standard_id'

    standard_id = fields.Many2one('standard.standard', 'Standard')
    exam_id = fields.Many2one('exam.result', 'Result')
    grade = fields.Char(string='Grade')


class exam_subject(models.Model):
    _name = "exam.subject"
    _description = 'Exam Subject Information'
    _rec_name = 'subject_id'

    @api.constrains('obtain_marks', 'minimum_marks')
    def _validate_marks(self):
        for marks_obj in self:
            if marks_obj.obtain_marks > marks_obj.maximum_marks or \
                    marks_obj.minimum_marks > marks_obj.maximum_marks:
                raise Warning(_('The obtained marks and minimum marks'
                                'should not extend maximum marks.'))

    @api.multi
    @api.depends('exam_id', 'obtain_marks')
    def _get_grade(self):
        for grade_obj in self:
            if grade_obj.exam_id and grade_obj.exam_id.student_id and \
               grade_obj.exam_id.student_id.year.grade_id.grade_ids:
                for grade_id in grade_obj.exam_id.student_id.year.\
                        grade_id.grade_ids:
                    if grade_obj.obtain_marks >= grade_id.from_mark and \
                            grade_obj.obtain_marks <= grade_id.to_mark:
                        grade_obj.grade = grade_id.grade

    exam_id = fields.Many2one('exam.result', 'Result')
    state = fields.Selection([('draft', 'Draft'), ('confirm', 'Confirm'),
                              ('re-access', 'Re-Access'),
                              ('re-access_confirm', 'Re-Access-Confirm'),
                              ('re-evaluation', 'Re-Evaluation'),
                              ('re-evaluation_confirm',
                               'Re-Evaluation Confirm')],
                             related='exam_id.state', string="State")
    subject_id = fields.Many2one("subject.subject", "Subject Name")
    absent = fields.Boolean("Absent")
    obtain_marks = fields.Float("Obtain Marks", group_operator="avg")
    minimum_marks = fields.Float("Minimum Marks")
    maximum_marks = fields.Float("Maximum Marks")
    marks_access = fields.Float("Marks After Access")
    marks_reeval = fields.Float("Marks After Re-evaluation")
    grade_id = fields.Many2one('grade.master', "Grade")
    grade = fields.Char(compute='_get_grade', string='Grade', type="char")


class exam_result_batchwise(models.Model):

    _name = 'exam.batchwise.result'
    _rec_name = 'standard_id'
    _description = 'exam result Information by Batch wise'

    @api.one
    @api.depends('standard_id', 'year')
    def compute_grade(self):
        fina_tot = 0
        count = 0
        divi = 0
        year_obj = self.env['academic.year']
        stud_obj = self.env['exam.result']
        if self.standard_id and self.year:
            year_ob = year_obj.browse(self.year.id)
            stand_id = stud_obj.search([('standard_id', '=',
                                         self.standard_id.id)])
            for stand in stand_id:
                student_ids = stud_obj.browse(stand.id)
                if student_ids.result_ids:
                    for res_line in student_ids.result_ids:
                        count += 1
                    fina_tot += student_ids.total
                divi = fina_tot / count  # Total_obtain mark of all student
                if year_ob.grade_id.grade_ids:
                    for grade_id in year_ob.grade_id.grade_ids:
                        if divi >= grade_id.from_mark and \
                                divi <= grade_id.to_mark:
                                self.grade = grade_id.grade

    standard_id = fields.Many2one("school.standard", "Standard", required=True)
    year = fields.Many2one('academic.year', 'Academic Year', required=True)
    grade = fields.Char(compute='compute_grade', string='Grade', method=True,
                        store=True)


class additional_exam_result(models.Model):

    _name = 'additional.exam.result'
    _description = 'subject result Information'

    @api.one
    @api.depends('a_exam_id', 'obtain_marks')
    def _calc_result(self):
        if self.a_exam_id and self.a_exam_id.subject_id and \
                self.a_exam_id.subject_id.minimum_marks:
            if self.a_exam_id.subject_id.minimum_marks <= self.obtain_marks:
                self.result = 'Pass'
            else:
                self.result = 'Fail'

    @api.onchange('a_exam_id')
    def onchange_exam(self):
        #         standard_lst = []
        student_lst = []
        #         sub_res = {}
        for exam_obj in self:
            for rec in exam_obj.a_exam_id.standard_id:
                for student_obj in rec.student_ids:
                    student_lst.append(student_obj.id)
        return {'domain': {'student_id': [('id', 'in', student_lst)]}}

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
            raise Warning(_('The obtained marks should not'
                            'extend maximum marks.'))
        return True

    a_exam_id = fields.Many2one("additional.exam", "Additional Examination",
                                required=True)
    student_id = fields.Many2one("student.student", "Student Name",
                                 required=True)
    roll_no_id = fields.Integer(related='student_id.roll_no',
                                string="Roll No", readonly=True)
    standard_id = fields.Many2one(related='student_id.standard_id',
                                  string="Standard", readonly=True)
    obtain_marks = fields.Float("Obtain Marks")
    result = fields.Char(compute='_calc_result', string='Result', method=True)


class student_student(models.Model):
    _name = 'student.student'
    _inherit = 'student.student'
    _description = 'Student Information'

    @api.model
    def search(self, args, offset=0, limit=None, order=None, count=False):
        if self._context.get('exam'):
            exam_obj = self.env['exam.exam']
            exam_data = exam_obj.browse(self._context['exam'])
            std_ids = [std_id.id for std_id in exam_data.standard_id]
            args.append(('id', 'in', std_ids))
        return super(student_student, self).search(args=args, offset=offset,
                                                   limit=limit, order=order,
                                                   count=count)

# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4:
