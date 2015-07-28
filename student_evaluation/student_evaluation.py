# -*- encoding: utf-8 -*-
##############################################################################
#
#    OpenERP, Open Source Management Solution
#    Copyright (C) 2004-2009 Tiny SPRL (<http://tiny.be>).
#    Copyright (C) 2011-2012 Serpent Consulting Services
#    (<http://www.serpentcs.com>)
#    Copyright (C) 2013-2014 Serpent Consulting Services
#    (<http://www.serpentcs.com>)
#    Copyright (C) 2015 Serpent Consulting Services
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

from openerp import models, fields, api
import time


class student_evaluation(models.Model):

    _name = "student.evaluation"
    _rec_name = 'student_id'

    @api.one
    def get_record(self):
        eval_line_obj = self.env['student.evaluation.line']
        eval_temp_obj = self.env['student.evaluation.template']
        eval_list = []
        for stu_eval_rec in self.browse(self.ids):
            if stu_eval_rec.eval_line:
                self._cr.execute('delete from student_evaluation_line where'
                                 'eval_id=%s', (stu_eval_rec.id,))
            type = stu_eval_rec.type
            eval_temp_rec_browse = eval_temp_obj.search([('type', '=', type)])
            for eval_temp_rec in eval_temp_rec_browse:
                eval_list.append(eval_temp_rec.id)
            for i in range(0, len(eval_list)):
                eval_line_obj.create({"stu_eval_id": eval_list[i],
                                      "eval_id": self.id})
        return True

    @api.one
    @api.depends('eval_line')
    def _compute_total_points(self):
        for rate_line in self:
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
    total = fields.Float(compute='_compute_total_points', method=True,
                         string="Total Points")
    state = fields.Selection([('draft', 'Draft'), ('start', 'Start'),
                              ('finished', 'Finish'),
                              ('cancelled', 'Cancel')], 'State',
                             readonly=True, default='draft')
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


class student_evaluation_line(models.Model):

    _name = 'student.evaluation.line'

    @api.multi
    def onchange_point(self, point_id):
        if point_id:
            for point_obj in self.env['rating.rating'].browse(point_id):
                return {'value': {'rating': point_obj.rating}}

    eval_id = fields.Many2one('student.evaluation', 'eval id')
    stu_eval_id = fields.Many2one('student.evaluation.template', 'Question')
    point_id = fields.Many2one('rating.rating','Rating',
                               domain= "[('rating_id', '=', stu_eval_id)]")
    rating = fields.Char('Remarks')

    _sql_constraints = [
        ('number_uniq', 'unique(eval_id, stu_eval_id)',
         'Questions are already in Exists!'),
    ]


class student_evaluation_template(models.Model):

    _name = "student.evaluation.template"
    _rec_name = 'desc'

    desc = fields.Char('Description', required=True)
    type = fields.Selection([('faculty', 'Faculty'), ('student', 'Student')],
                            'User Type', required=True, default='faculty')
    rating_line = fields.One2many('rating.rating', 'rating_id', 'Rating')


class rating_rating(models.Model):

    _name = 'rating.rating'
    _rec_name = 'point'

    rating_id = fields.Many2one('student.evaluation.template', 'Stud')
    point = fields.Integer('Rating in points', required=True)
    rating = fields.Char('Remarks', required=True)

# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4:
