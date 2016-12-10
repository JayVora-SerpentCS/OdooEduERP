# -*- coding: utf-8 -*-
# Part of Odoo. See LICENSE file for full copyright and licensing details.

import time
from openerp import models, fields, api


class StudentEvaluation(models.Model):
    _name = "student.evaluation"
    _rec_name = 'student_id'

    def get_record(self):
        eval_line_obj = self.env['student.evaluation.line']
        eval_temp_obj = self.env['student.evaluation.template']
        eval_list = []
        for stu_eval_rec in self.browse(self.ids):
            if stu_eval_rec.eval_line:
                self._cr.execute('delete from student_evaluation_line\
                                  where eval_id=%s', (stu_eval_rec.id,))
            type_eval = stu_eval_rec.type
            domain = [('type', '=', type_eval)]
            eval_temp_ids = eval_temp_obj.search(domain)
            for eval_temp_id in eval_temp_ids:
                eval_list.append(eval_temp_id.id)
            for i in range(0, len(eval_list)):
                eval_line_obj.create({'stu_eval_id': eval_list[i],
                                      'eval_id': self.id})
        return True

    @api.depends('eval_line')
    def _compute_total_points(self):
        total = 0
        if self.eval_line:
            for line in self.eval_line:
                if line.point_id.point:
                    total += line.point_id.point
            self.total = total
        else:
            self.total = total

    @api.model
    def get_user(self):
        return self._uid

    student_id = fields.Many2one('student.student', 'Student Name',
                                 required=True)
    type = fields.Selection([('faculty', 'Faculty'), ('student', 'Student')],
                            'User Type', required=True)
    date = fields.Date('Evaluation Date', required=True,
                       default=lambda * a: time.strftime('%Y-%m-%d'))
    evaluator_id = fields.Many2one('hr.employee', 'Faculty Name')
    eval_line = fields.One2many('student.evaluation.line', 'eval_id',
                                'Questionnaire')
    total = fields.Float('Total Points', compute='_compute_total_points',
                         method=True)
    state = fields.Selection([('draft', 'Draft'), ('start', 'Start'),
                              ('finished', 'Finish'), ('cancelled', 'Cancel')],
                             'State', readonly=True, default='draft')
    user_id = fields.Many2one('res.users', 'User', readonly=True,
                              default=get_user)

    @api.multi
    def set_start(self):
        self.write({'state': 'start'})
        return True

    @api.multi
    def set_finish(self):
        self.write({'state': 'finished'})
        return True

    @api.multi
    def set_cancel(self):
        self.write({'state': 'cancelled'})
        return True

    @api.multi
    def set_draft(self):
        self.write({'state': 'draft'})
        return True


class StudentEvaluationLine(models.Model):
    _name = 'student.evaluation.line'

    @api.multi
    def onchange_point(self, point_id):
        if point_id:
            for point_obj in self.env['rating.rating'].browse(point_id):
                return {'value': {'rating': point_obj.rating}}

    eval_id = fields.Many2one('student.evaluation', 'Evaluation id')
    stu_eval_id = fields.Many2one('student.evaluation.template', 'Question')
    point_id = fields.Many2one('rating.rating', 'Rating',
                               domain="[('rating_id', '=', stu_eval_id)]")
    rating = fields.Char('Remarks')

    _sql_constraints = [
        ('number_uniq', 'unique(eval_id, stu_eval_id)',
         'Questions already exist!'),
    ]


class StudentEvaluationTemplate(models.Model):
    _name = "student.evaluation.template"
    _rec_name = 'desc'

    desc = fields.Char('Description', required=True)
    type = fields.Selection([('faculty', 'Faculty'), ('student', 'Student')],
                            'User Type', required=True, default='faculty')
    rating_line = fields.One2many('rating.rating', 'rating_id', 'Rating')


class RatingRating(models.Model):
    _name = 'rating.rating'
    _rec_name = 'point'

    rating_id = fields.Many2one('student.evaluation.template', 'Stud')
    point = fields.Integer('Rating in points', required=True)
    rating = fields.Char('Remarks', required=True)
