# -*- encoding: utf-8 -*-
##############################################################################
#
#    OpenERP, Open Source Management Solution
#    Copyright (C) 2004-2009 Tiny SPRL (<http://tiny.be>).
#    Copyright (C) 2011-Today Serpent Consulting Services PVT. LTD.
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
from openerp import models, fields, api, _
from openerp.exceptions import Warning
import time
from calendar import monthrange
from datetime import datetime


class attendance_sheet(models.Model):

    ''' Defining Monthly Attendance sheet Information '''
    _description = 'Attendance Sheet'
    _name = 'attendance.sheet'

    name = fields.Char('Description', readonly=True)
    standard_id = fields.Many2one('school.standard', 'Academic Class',
                                  required=True)
    month_id = fields.Many2one('academic.month', 'Month', required=True)
    year_id = fields.Many2one('academic.year', 'Year', required=True)
    attendance_ids = fields.One2many('attendance.sheet.line', 'standard_id',
                                                              'Attendance')
    user_id = fields.Many2one('hr.employee', 'Faculty')
    attendance_type = fields.Selection([('daily', 'FullDay'), ('lecture',
                                         'Lecture Wise')], 'Type')

    @api.multi
    def onchange_class_info(self, standard_id):
        res = {}
        student_list = []
        stud_obj = self.env['student.student']
        stud_ids = stud_obj.search([('standard_id', '=', standard_id)])
        for stud_id in stud_ids:
            student_list.append({'roll_no': stud_id.roll_no,
                                 'name': stud_id.name})
        res.update({'value': {'attendance_ids': student_list}})
        return res

    @api.model
    def fields_view_get(self, view_id=None, view_type='form', context=None,
                            toolbar=False, submenu=False):
        res = super(attendance_sheet,
                    self).fields_view_get(view_id=view_id,
                                          view_type=view_type,
                                          context=context,
                                          toolbar=toolbar,
                                          submenu=submenu)
        if context is None:
            context = {}
        if context.get('month_id', False):
            no_of_days = monthrange(context['year_id'][0],
                                    context['month_id'][0])[1]
            att_form = res['fields']['attendance_ids']['views']['form']
            att_tree = res['fields']['attendance_ids']['views']['tree']
            if no_of_days == 31:
                pass

            elif no_of_days == 30:
                if 'attendance_ids' in res['fields']:
                    att = res['fields']['attendance_ids']
                    if 'views' in att:
                        att_tree['fields']['three_1'].update({'invisible': 1})
                        att_form['fields']['three_1'].update({'invisible': 1})

            elif no_of_days == 29:
                if 'attendance_ids' in res['fields']:
                    att = res['fields']['attendance_ids']
                    if 'views' in att:
                        att_tree['fields']['three_1'].update({'invisible': 1})
                        att_form['fields']['three_1'].update({'invisible': 1})
                        att_tree['fields']['two_0'].update({'invisible': 1})
                        att_form['fields']['two_0'].update({'invisible': 1})
            else:

                if 'attendance_ids' in res['fields']:
                    att = res['fields']['attendance_ids']
                    if 'views' in att:
                        att_tree['fields']['three_1'].update({'invisible': 1})
                        att_form['fields']['three_1'].update({'invisible': 1})
                        att_tree['fields']['two_0'].update({'invisible': 1})
                        att_form['fields']['two_0'].update({'invisible': 1})
                        att_tree['fields']['two_9'].update({'invisible': 1})
                        att_form['fields']['two_9'].update({'invisible': 1})

        return res


class attendance_sheet_line(models.Model):

    ''' Defining Attendance Sheet Line Information '''

    @api.multi
    def attendance_percentage(self):
        res = {}
        for attendance_sheet_data in self:
            att_count = 0
            percentage = 0.0
            if attendance_sheet_data.one:
                att_count = att_count+1
            if attendance_sheet_data.two:
                att_count = att_count+1
            if attendance_sheet_data.three:
                att_count = att_count+1
            if attendance_sheet_data.four:
                att_count = att_count+1
            if attendance_sheet_data.five:
                att_count = att_count+1
            if attendance_sheet_data.six:
                att_count = att_count+1
            if attendance_sheet_data.seven:
                att_count = att_count+1
            if attendance_sheet_data.eight:
                att_count = att_count+1
            if attendance_sheet_data.nine:
                att_count = att_count+1
            if attendance_sheet_data.ten:
                att_count = att_count+1
            if attendance_sheet_data.one_1:
                att_count = att_count+1
            if attendance_sheet_data.one_2:
                att_count = att_count+1
            if attendance_sheet_data.one_3:
                att_count = att_count+1
            if attendance_sheet_data.one_4:
                att_count = att_count+1
            if attendance_sheet_data.one_5:
                att_count = att_count+1
            if attendance_sheet_data.one_6:
                att_count = att_count+1
            if attendance_sheet_data.one_7:
                att_count = att_count+1
            if attendance_sheet_data.one_8:
                att_count = att_count+1
            if attendance_sheet_data.one_9:
                att_count = att_count+1
            if attendance_sheet_data.one_0:
                att_count = att_count+1

            if attendance_sheet_data.two_1:
                att_count = att_count+1
            if attendance_sheet_data.two_2:
                att_count = att_count+1
            if attendance_sheet_data.two_3:
                att_count = att_count+1
            if attendance_sheet_data.two_4:
                att_count = att_count+1
            if attendance_sheet_data.two_5:
                att_count = att_count+1
            if attendance_sheet_data.two_6:
                att_count = att_count+1
            if attendance_sheet_data.two_7:
                att_count = att_count+1
            if attendance_sheet_data.two_8:
                att_count = att_count+1
            if attendance_sheet_data.two_9:
                att_count = att_count+1
            if attendance_sheet_data.two_0:
                att_count = att_count+1
            if attendance_sheet_data.three_1:
                att_count = att_count+1
            percentage = (float(att_count/31.00))*100
            res[attendance_sheet_data.id] = percentage
        return res

    _description = 'Attendance Sheet Line'
    _name = 'attendance.sheet.line'
    _order = 'roll_no'

    roll_no = fields.Integer('Roll Number', required=True,
                             help='Roll Number of Student')
    standard_id = fields.Many2one('attendance.sheet', 'Standard')
#     name = fields.Many2one('student.student','Student Name', required=True)
    name = fields.Char('Student Name', required=True, readonly=True)
    one = fields.Boolean('1')
    two = fields.Boolean('2')
    three = fields.Boolean('3')
    four = fields.Boolean('4')
    five = fields.Boolean('5')
    seven = fields.Boolean('7')
    six = fields.Boolean('6')
    eight = fields.Boolean('8')
    nine = fields.Boolean('9')
    ten = fields.Boolean('10')
    one_1 = fields.Boolean('11')
    one_2 = fields.Boolean('12')
    one_3 = fields.Boolean('13')
    one_4 = fields.Boolean('14')
    one_5 = fields.Boolean('15')
    one_6 = fields.Boolean('16')
    one_7 = fields.Boolean('17')
    one_8 = fields.Boolean('18')
    one_9 = fields.Boolean('19')
    one_0 = fields.Boolean('20')
    two_1 = fields.Boolean('21')
    two_2 = fields.Boolean('22')
    two_3 = fields.Boolean('23')
    two_4 = fields.Boolean('24')
    two_5 = fields.Boolean('25')
    two_6 = fields.Boolean('26')
    two_7 = fields.Boolean('27')
    two_8 = fields.Boolean('28')
    two_9 = fields.Boolean('29')
    two_0 = fields.Boolean('30')
    three_1 = fields.Boolean('31')
    percentage = fields.Float(compute="attendance_percentage", method=True,
                              string='Attendance (%)', store=False)


class daily_attendance(models.Model):

    ''' Defining Daily Attendance Information '''
    _description = 'Daily Attendance'
    _name = 'daily.attendance'

    @api.one
    @api.depends('student_ids')
    def _total(self):
        count = 0
        if self.student_ids:
            for att in self.student_ids:
                    count += 1
            self.total_student = count
        else:
            self.total_student = count

    @api.one
    @api.depends('student_ids')
    def _present(self):
        count = 0
        if self.student_ids:
            for att in self.student_ids:
                if att.is_present:
                    count += 1
            self.total_presence = count
        else:
            self.total_presence = count

    @api.one
    @api.depends('student_ids')
    def _absent(self):
        count_fail = 0
        if self.student_ids:
            for att in self.student_ids:
                if att.is_absent:
                    count_fail += 1
            self.total_absent = count_fail
        else:
            self.total_absent = count_fail

    date = fields.Date("Today's Date", default=lambda *a:
                       time.strftime('%Y-%m-%d'))
    standard_id = fields.Many2one('school.standard', 'Academic Class',
                                  required=True, states={'validate':
                                   [('readonly', True)]})
    student_ids = fields.One2many('daily.attendance.line', 'standard_id',
                                  'Students', states={'validate':
                                   [('readonly', True)],
                                   'draft': [('readonly', False)]})
    user_id = fields.Many2one('hr.employee', 'Faculty',
                              states={'validate': [('readonly', True)]})
    state = fields.Selection([('draft', 'Draft'), ('validate', 'Validate')],
                             'State', readonly=True, default='draft')
    total_student = fields.Integer(compute="_total", method=True, store=True,
                                   string='Total Students')
    total_presence = fields.Integer(compute="_present", method=True,
                                    store=True, string='Presenct Students')
    total_absent = fields.Integer(compute="_absent", method=True, store=True,
                                  string='Absent Students')

    @api.model
    def create(self, vals):
        child = ''
        if vals:
            if 'student_ids' in vals.keys():
                child = vals.pop('student_ids')
        ret_val = super(daily_attendance, self).create(vals)
        if child != '':
            ret_val.write({'student_ids': child})
        return ret_val

    @api.multi
    def onchange_standard_id(self, standard_id):
        res = {}
        student_list = []
        stud_obj = self.env['student.student']
        if standard_id:
            self._cr.execute("""select id from student_student where\
                                standard_id=%s""", (standard_id,))
            stud_ids = self._cr.fetchall()
            for stud_id in stud_ids:
                student_ids = stud_obj.browse(stud_id)
                student_list.append({'roll_no': student_ids.roll_no,
                                     'stud_id': stud_id})
            res.update({'value': {'student_ids': student_list}})
        return res

    @api.multi
    def attendance_draft(self):
        attendance_sheet_obj = self.env['attendance.sheet']
        academic_year_obj = self.env['academic.year']
        academic_month_obj = self.env['academic.month']

        for daily_attendance_data in self:
            if not daily_attendance_data.date:
                raise Warning(_('Please enter todays date.'))
            date = datetime.strptime(daily_attendance_data.date, "%Y-%m-%d")
            year_search_ids = academic_year_obj.search([('code', '=',
                                                         date.year)])
            month_search_ids = academic_month_obj.search([('code', '=',
                                                           date.month)])
            for line in daily_attendance_data.student_ids:
                line.write({'is_present': False, 'is_absent': False})

            attendance_sheet_domain = [('standard_id', '=',
                                        daily_attendance_data.standard_id.id),
                                       ('month_id', '=', month_search_ids.id),
                                       ('year_id', '=', year_search_ids.id)]
        search_attendance_sheet_ids = attendance_sheet_obj.search(attendance_sheet_domain)
        if search_attendance_sheet_ids:
            for attendance_sheet_datas in search_attendance_sheet_ids:
                for attendance_id in attendance_sheet_datas.attendance_ids:
                    date = datetime.strptime(daily_attendance_data.date,
                                             "%Y-%m-%d")
                    if date.day == 1:
                        dic = {'one': False}
                    elif date.day == 2:
                        dic = {'two': False}
                    elif date.day == 3:
                        dic = {'three': False}
                    elif date.day == 4:
                        dic = {'four': False}
                    elif date.day == 5:
                        dic = {'five': False}
                    elif date.day == 6:
                        dic = {'six': False}
                    elif date.day == 7:
                        dic = {'seven': False}
                    elif date.day == 8:
                        dic = {'eight': False}
                    elif date.day == 9:
                        dic = {'nine': False}
                    elif date.day == 10:
                        dic = {'ten': False}
                    elif date.day == 11:
                        dic = {'one_1': False}
                    elif date.day == 12:
                        dic = {'one_2': False}
                    elif date.day == 13:
                        dic = {'one_3': False}
                    elif date.day == 14:
                        dic = {'one_4': False}
                    elif date.day == 15:
                        dic = {'one_5': False}
                    elif date.day == 16:
                        dic = {'one_6': False}
                    elif date.day == 17:
                        dic = {'one_7': False}
                    elif date.day == 18:
                        dic = {'one_8': False}
                    elif date.day == 19:
                        dic = {'one_9': False}
                    elif date.day == 20:
                        dic = {'one_0': False}
                    elif date.day == 21:
                        dic = {'two_1': False}
                    elif date.day == 22:
                        dic = {'two_2': False}
                    elif date.day == 23:
                        dic = {'two_3': False}
                    elif date.day == 24:
                        dic = {'two_4': False}
                    elif date.day == 25:
                        dic = {'two_5': False}
                    elif date.day == 26:
                        dic = {'two_6': False}
                    elif date.day == 27:
                        dic = {'two_7': False}
                    elif date.day == 28:
                        dic = {'two_8': False}
                    elif date.day == 29:
                        dic = {'two_9': False}
                    elif date.day == 30:
                        dic = {'two_0': False}
                    elif date.day == 31:
                        dic = {'three_1': False}
                    attendance_id.write(dic)
        self.write({'state': 'draft'})
        return True

    @api.multi
    def attendance_validate(self):
        att_sheet_line_obj = self.env['attendance.sheet.line']
        acadmic_year_obj = self.env['academic.year']
        acadmic_month_obj = self.env['academic.month']
        attendance_sheet_obj = self.env['attendance.sheet']

        for line in self:
            date = datetime.strptime(line.date, "%Y-%m-%d")
            year = date.year
            year_ids= acadmic_year_obj.search([('date_start', '<=', date),
                                               ('date_stop', '>=' , date)])
            month_ids= acadmic_month_obj.search([('date_start', '<=' , date),
                                                ('date_stop', '>=', date),
                                                ('year_id', 'in',
                                                 year_ids.ids)])
            if month_ids:
                month_data = month_ids
                att_sheet_ids = attendance_sheet_obj.search([('month_id',
                                                              'in',
                                                              month_ids.ids),
                                                             ('year_id', 'in',
                                                              year_ids.ids)])
                attendance_sheet_id = att_sheet_ids and \
                                        att_sheet_ids[0] or False
                if not attendance_sheet_id:
                    attendance_sheet_id = attendance_sheet_obj.create({
                            'name': 'Month ' + month_data.name + "-Year " + str(year),
                            'standard_id': line.standard_id.id,
                            'user_id': line.user_id.id,
                            'month_id': month_data.id,
                            'year_id': year_ids and year_ids.id or False})
                    for student_id in line.student_ids:
                        att_sheet_line_obj.create({
                                       'roll_no': student_id.roll_no,
                                       'standard_id': attendance_sheet_id.id,
                                       'name': student_id.stud_id.student_name
                                                          })
                        for student_id in line.student_ids:
                            roll_no = student_id.roll_no
                            search_id = att_sheet_line_obj.search([('roll_no',
                                                                    '=',
                                                                    roll_no)])
                            if date.day == 1 and student_id.is_absent:
                                val = {'one': False}

                            elif date.day == 1 and not student_id.is_absent:
                                val = {'one':True}

                            elif date.day == 2 and student_id.is_absent:
                                val = {'two': False}

                            elif date.day == 2 and not student_id.is_absent:
                                val = {'two':True}

                            elif date.day == 3 and student_id.is_absent:
                                val = {'three': False}

                            elif date.day == 3 and not student_id.is_absent:
                                val = {'three': True}

                            elif date.day == 4 and student_id.is_absent:
                                val = {'four': False}

                            elif date.day == 4 and not student_id.is_absent:
                                val = {'four': True}

                            elif date.day == 5 and student_id.is_absent:
                                val = {'five': False}

                            elif date.day == 5 and not student_id.is_absent:
                                val = {'five': True}

                            elif date.day == 6 and student_id.is_absent:
                                val = {'six': False}

                            elif date.day == 6 and not student_id.is_absent:
                                val = {'six': True}

                            elif date.day == 7 and student_id.is_absent:
                                val = {'seven': False}

                            elif date.day == 7 and not student_id.is_absent:
                                val = {'seven': True}

                            elif date.day == 8 and student_id.is_absent:
                                val = {'eight': False}

                            elif date.day == 8 and not student_id.is_absent:
                                val = {'eight': True}

                            elif date.day == 9 and student_id.is_absent:
                                val = {'nine': False}

                            elif date.day == 9 and not student_id.is_absent:
                                val = {'nine': True}

                            elif date.day == 10 and student_id.is_absent:
                                val = {'ten': False}

                            elif date.day == 10 and not student_id.is_absent:
                                val = {'ten': True}

                            elif date.day == 11 and student_id.is_absent:
                                val = {'one_1': False}

                            elif date.day == 11 and not student_id.is_absent:
                                val = {'one_1': True}

                            elif date.day == 12 and student_id.is_absent:
                                val = {'one_2': False}

                            elif date.day == 12 and not student_id.is_absent:
                                val = {'one_2':True}

                            elif date.day == 13 and student_id.is_absent:
                                val = {'one_3': False}

                            elif date.day == 13 and not student_id.is_absent:
                                val = {'one_3': True}

                            elif date.day == 14 and student_id.is_absent:
                                val = {'one_4': False}

                            elif date.day == 14 and not student_id.is_absent:
                                val = {'one_4': True}

                            elif date.day == 15 and student_id.is_absent:
                                val = {'one_5':False}

                            elif date.day == 15 and not student_id.is_absent:
                                val = {'one_5': True}

                            elif date.day == 16 and student_id.is_absent:
                                val = {'one_6': False}

                            elif date.day == 16 and not student_id.is_absent:
                                val = {'one_6': True}

                            elif date.day == 17 and student_id.is_absent:
                                val = {'one_7': False}

                            elif date.day == 17 and not student_id.is_absent:
                                val = {'one_7': True}

                            elif date.day == 18 and student_id.is_absent:
                                val = {'one_8': False}

                            elif date.day == 18 and not student_id.is_absent:
                                val = {'one_8': True}

                            elif date.day == 19 and student_id.is_absent:
                                val = {'one_9': False}

                            elif date.day == 19 and not student_id.is_absent:
                                val = {'one_9':True}

                            elif date.day == 20 and student_id.is_absent:
                                val = {'one_0':False}

                            elif date.day == 20 and not student_id.is_absent:
                                val = {'one_0':True}

                            elif date.day == 21 and student_id.is_absent:
                                val = {'two_1': False}

                            elif date.day == 21 and not student_id.is_absent:
                                val = {'two_1': True}

                            elif date.day == 22 and student_id.is_absent:
                                val = {'two_2':False}

                            elif date.day == 22 and not student_id.is_absent:
                                val = {'two_2': True}

                            elif date.day == 23 and student_id.is_absent:
                                val = {'two_3': False}

                            elif date.day == 23 and not student_id.is_absent:
                                val = {'two_3':True}

                            elif date.day == 24 and student_id.is_absent:
                                val = {'two_4': False}

                            elif date.day == 24 and not student_id.is_absent:
                                val = {'two_4': True}

                            elif date.day == 25 and student_id.is_absent:
                                val = {'two_5': False}

                            elif date.day == 25 and not student_id.is_absent:
                                val = {'two_5': True}

                            elif date.day == 26 and student_id.is_absent:
                                val = {'two_6':False}

                            elif date.day == 26 and not student_id.is_absent:
                                val = {'two_6': True}

                            elif date.day == 27 and student_id.is_absent:
                                val = {'two_7': False}

                            elif date.day == 27 and not student_id.is_absent:
                                val = {'two_7': True}

                            elif date.day == 28 and student_id.is_absent:
                                val = {'two_8': False}

                            elif date.day == 28 and not student_id.is_absent:
                                val = {'two_8': True}

                            elif date.day == 29 and student_id.is_absent:
                                val = {'two_9': False}

                            elif date.day == 29 and not student_id.is_absent:
                                val = {'two_9': True}

                            elif date.day == 30 and student_id.is_absent:
                                val = {'two_0':False}

                            elif date.day == 30 and not student_id.is_absent:
                                val = {'two_0': True}

                            elif date.day == 31 and student_id.is_absent:
                                val = {'three_1': False}

                            elif date.day == 31 and not student_id.is_absent:
                                val = {'three_1': True}
                            else:
                                val = {}
                            if search_id:
                                search_id.write(val)

                if attendance_sheet_id:
                    for student_id in line.student_ids:
                        roll_no = student_id.roll_no
                        standard_id = attendance_sheet_id.id
                        search_id = att_sheet_line_obj.search([('roll_no',
                                                                '=', roll_no),
                                                               ('standard_id',
                                                                '=', 
                                                                standard_id)])
                        if date.day == 1 and student_id.is_absent:
                            val = {'one': False}

                        elif date.day == 1 and not student_id.is_absent:
                            val = {'one': True}

                        elif date.day == 2 and student_id.is_absent:
                            val = {'two': False}

                        elif date.day == 2 and not student_id.is_absent:
                            val = {'two': True}

                        elif date.day == 3 and student_id.is_absent:
                            val = {'three': False}

                        elif date.day == 3 and not student_id.is_absent:
                            val = {'three': True}

                        elif date.day == 4 and student_id.is_absent:
                            val = {'four': False}

                        elif date.day == 4 and not student_id.is_absent:
                            val = {'four': True}

                        elif date.day == 5 and student_id.is_absent:
                            val = {'five': False}

                        elif date.day == 5 and not student_id.is_absent:
                            val = {'five': True}

                        elif date.day == 6 and student_id.is_absent:
                            val = {'six': False}

                        elif date.day == 6 and not student_id.is_absent:
                            val = {'six': True}

                        elif date.day == 7 and student_id.is_absent:
                            val = {'seven': False}

                        elif date.day == 7 and not student_id.is_absent:
                            val = {'seven': True}

                        elif date.day == 8 and student_id.is_absent:
                            val = {'eight': False}

                        elif date.day == 8 and not student_id.is_absent:
                            val = {'eight': True}

                        elif date.day == 9 and student_id.is_absent:
                            val = {'nine': False}

                        elif date.day == 9 and not student_id.is_absent:
                            val = {'nine': True}

                        elif date.day == 10 and student_id.is_absent:
                            val = {'ten': False}

                        elif date.day == 10 and not student_id.is_absent:
                            val = {'ten': True}

                        elif date.day == 11 and student_id.is_absent:
                            val = {'one_1': False}

                        elif date.day == 11 and not student_id.is_absent:
                            val = {'one_1': True}

                        elif date.day == 12 and student_id.is_absent:
                            val = {'one_2': False}

                        elif date.day == 12 and not student_id.is_absent:
                            val = {'one_2': True}

                        elif date.day == 13 and student_id.is_absent:
                            val = {'one_3': False}

                        elif date.day == 13 and not student_id.is_absent:
                            val = {'one_3': True}

                        elif date.day == 14 and student_id.is_absent:
                            val = {'one_4': False}

                        elif date.day == 14 and not student_id.is_absent:
                            val = {'one_4': True}

                        elif date.day == 15 and student_id.is_absent:
                            val = {'one_5': False}

                        elif date.day == 15 and not student_id.is_absent:
                            val = {'one_5': True}

                        elif date.day == 16 and student_id.is_absent:
                            val = {'one_6': False}

                        elif date.day == 16 and not student_id.is_absent:
                            val = {'one_6': True}

                        elif date.day == 17 and student_id.is_absent:
                            val = {'one_7': False}

                        elif date.day == 17 and not student_id.is_absent:
                            val = {'one_7': True}

                        elif date.day == 18 and student_id.is_absent:
                            val = {'one_8': False}

                        elif date.day == 18 and not student_id.is_absent:
                            val = {'one_8': True}

                        elif date.day == 19 and student_id.is_absent:
                            val = {'one_9': False}

                        elif date.day == 19 and not student_id.is_absent:
                            val = {'one_9': True}

                        elif date.day == 20 and student_id.is_absent:
                            val = {'one_0': False}

                        elif date.day == 20 and not student_id.is_absent:
                            val = {'one_0': True}

                        elif date.day == 21 and student_id.is_absent:
                            val = {'two_1': False}

                        elif date.day == 21 and not student_id.is_absent:
                            val = {'two_1': True}

                        elif date.day == 22 and student_id.is_absent:
                            val = {'two_2': False}

                        elif date.day == 22 and not student_id.is_absent:
                            val = {'two_2': True}

                        elif date.day == 23 and student_id.is_absent:
                            val = {'two_3': False}

                        elif date.day == 23 and not student_id.is_absent:
                            val = {'two_3': True}

                        elif date.day == 24 and student_id.is_absent:
                            val = {'two_4': False}

                        elif date.day == 24 and not student_id.is_absent:
                            val = {'two_4': True}

                        elif date.day == 25 and student_id.is_absent:
                            val = {'two_5': False}

                        elif date.day == 25 and not student_id.is_absent:
                            val = {'two_5': True}

                        elif date.day == 26 and student_id.is_absent:
                            val = {'two_6': False}

                        elif date.day == 26 and not student_id.is_absent:
                            val = {'two_6': True}

                        elif date.day == 27 and student_id.is_absent:
                            val = {'two_7': False}

                        elif date.day == 27 and not student_id.is_absent:
                            val = {'two_7': True}

                        elif date.day == 28 and student_id.is_absent:
                            val = {'two_8': False}

                        elif date.day == 28 and not student_id.is_absent:
                            val = {'two_8': True}

                        elif date.day == 29 and student_id.is_absent:
                            val = {'two_9': False}

                        elif date.day == 29 and not student_id.is_absent:
                            val = {'two_9': True}

                        elif date.day == 30 and student_id.is_absent:
                            val = {'two_0': False}

                        elif date.day == 30 and not student_id.is_absent:
                            val = {'two_0': True}

                        elif date.day == 31 and student_id.is_absent:
                            val = {'three_1': False}

                        elif date.day == 31 and not student_id.is_absent:
                            val = {'three_1': True}
                        else:
                            val = {}
                        if search_id:
                            search_id.write(val)

        self.write({'state': 'validate'})
        return True


class daily_attendance_line(models.Model):

    ''' Defining Daily Attendance Sheet Line Information '''
    _description = 'Daily Attendance Line'
    _name = 'daily.attendance.line'
    _order = 'roll_no'
    _rec_name = 'roll_no'

    roll_no = fields.Integer('Roll No.', required=True, help='Roll Number')
    standard_id = fields.Many2one('daily.attendance', 'Standard')
    stud_id = fields.Many2one('student.student', 'Name', required=True)
    is_present = fields.Boolean('Present')
    is_absent = fields.Boolean('Absent')

# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4:
