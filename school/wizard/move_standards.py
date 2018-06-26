# -*- coding: utf-8 -*-
# See LICENSE file for full copyright and licensing details.

from odoo import models, fields, api


class MoveStandards(models.TransientModel):
    _name = 'move.standards'

    academic_year_id = fields.Many2one('academic.year', 'Academic Year',
                                       required=True)

    @api.multi
    def move_start(self):
        '''Code for moving student to next standard'''
        academic_obj = self.env['academic.year']
        school_stand_obj = self.env['school.standard']
        standard_obj = self.env["standard.standard"]
        student_obj = self.env['student.student']
        for stud in student_obj.search([('state', '=', 'done')]):
            year_id = academic_obj.next_year(stud.year.sequence)
            academic_year = academic_obj.search([('id', '=', year_id)],
                                                limit=1)
            standard_seq = stud.standard_id.standard_id.sequence
            next_class_id = standard_obj.next_standard(standard_seq)

            # Assign the academic year
            if next_class_id:
                division = (stud.standard_id.division_id.id or False)
                domain = [('standard_id', '=', next_class_id),
                          ('division_id', '=', division),
                          ('school_id', '=', stud.school_id.id),
                          ('medium_id', '=', stud.medium_id.id)]
                next_stand = school_stand_obj.search(domain)
                if next_stand:
                    std_vals = {'year': academic_year.id,
                                'standard_id': next_stand.id}
                    # Move student to next standard
                    stud.write(std_vals)
        return True
