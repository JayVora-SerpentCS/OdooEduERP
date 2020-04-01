# See LICENSE file for full copyright and licensing details.

from odoo import models, api


class MoveStandards(models.TransientModel):
    _inherit = 'move.standards'

    def move_start(self):
        '''Method to change standard of student after he passes the exam'''
        academic_obj = self.env['academic.year']
        school_stand_obj = self.env['school.standard']
        standard_obj = self.env["standard.standard"]
        result_obj = self.env['exam.result']
        student_obj = self.env['student.student']
        stud_history_obj = self.env["student.history"]
        for rec in self:
            # search the done state students
            for stud in student_obj.search([('state', '=', 'done')]):
                # check the student history for same academic year
                stud_year_ids = stud_history_obj.\
                    search([('academice_year_id', '=',
                             rec.academic_year_id.id),
                            ('student_id', '=', stud.id)])
                year_id = academic_obj.next_year(stud.year.sequence)
                academic_year = academic_obj.search([('id', '=', year_id)],
                                                    limit=1)
                if stud_year_ids:
                    # search the student result
                    result_data = result_obj.\
                        search([('standard_id', '=', stud.standard_id.id),
                                ('standard_id.division_id',
                                 '=', stud.standard_id.division_id.id),
                                ('standard_id.medium_id',
                                 '=', stud.medium_id.id),
                                ('student_id', '=', stud.id)])
                    std_seq = stud.standard_id.standard_id.sequence
                    for results in result_data:
                        if results.result == "Pass":
                            next_class = standard_obj.next_standard(std_seq)
                            if next_class:
                                division = (stud.standard_id.division_id.id
                                            )
                                # find the school standard record
                                next_stand = school_stand_obj.\
                                    search([('standard_id', '=', next_class),
                                            ('division_id', '=', division),
                                            ('school_id', '=',
                                             stud.school_id.id),
                                            ('medium_id', '=',
                                             stud.medium_id.id)],
                                           limit=1)
                                # standard will change if student pass the exam
                                stud.write({'year': academic_year.id,
                                            'standard_id': next_stand.id
                                            })
                        else:
                            # If student is fail he will remain in same
                            # standard
                            stud.write({'year': academic_year.id,
                                        'standard_id': stud.standard_id.id
                                        })
        return True
