# -*- coding: utf-8 -*-
# Part of Odoo. See LICENSE file for full copyright and licensing details.

from openerp import http
from openerp.http import request
from datetime import date
import time


class SchoolDashboard(http.Controller):

    @http.route(['/get_school_dash_board_details'],
                type='json', auth='public')
    def get_school_dashboard_details(self, **kwargs):
        env = request.env

        groups_data = {'admin': False,
                       'student': False,
                       'teacher': False,
                       'parent': False,
                       'campus': False,
                       'faculty': False,
                       'department': False,
                       'accommo_mng': False,
                       'hostel_manager': False,
                       'canteen_manager': False,
                       'librarian': False,
                       'userian': False,
                       'placement_mng': False,
                       'Placement_mem': False,
                       'event_mng': False,
                       'fees_mng': False,
                       'admission_regi': False,
                       'student_inadmission': False,
                       'accommodation_userian': False
                       }

        user_rec = env['res.users'].browse(request.uid)
        groups = [grp.id for grp in user_rec.groups_id]
        ir_obj = env['ir.model.data']

        admin_group = ir_obj.get_object('school',
                                        'group_school_administration')
        student_group = ir_obj.get_object('school', 'group_school_student')
        teacher_group = ir_obj.get_object('school', 'group_school_teacher')
        parent_group = ir_obj.get_object('school', 'group_school_parent')
        campus_group = ir_obj.get_object('school',
                                         'group_university_campus_manager')
        faculty_group = ir_obj.get_object('school', 'group_university_faculty')
        department_group = ir_obj.get_object('school',
                                             'group_department_manager')
        admission_manager = 'group_school_student_inadmission'
        student_inadmission_group = ir_obj.get_object('school',
                                                      admission_manager)

        try:
            acco_mngr_group = ir_obj.get_object('accommodation',
                                                'group_accommodation_manager')
            hostel_mngr_group = ir_obj.get_object('accommodation',
                                                  'group_hostel_manager')
            acc_userian = 'group_accommodation_userian'
            accommo_user_group = ir_obj.get_object('accommodation',
                                                   acc_userian)
            if acco_mngr_group.id in groups:
                groups_data.update({'accommo_mng': True})
            if hostel_mngr_group.id in groups:
                groups_data.update({'hostel_manager': True})
            if accommo_user_group.id in groups:
                groups_data.update({'accommodation_userian': True})
        except Exception:
            groups_data.update({'accommo_mng': False, 'hostel_manager': False})

        try:
            canteen_mngr_group = ir_obj.get_object('school_canteen',
                                                   'group_canteen_manager')
            if canteen_mngr_group.id in groups:
                groups_data.update({'canteen_manager': True})
        except Exception:
            groups_data.update({'canteen_manager': False})

        try:
            librarian_group = ir_obj.get_object('library',
                                                'group_librarian')
            userian_group = ir_obj.get_object('library',
                                              'group_userian')
            if librarian_group.id in groups:
                groups_data.update({'librarian': True})
            if userian_group.id in groups:
                groups_data.update({'userian': True})
        except Exception:
            groups_data.update({'librarian': False, 'userian': False})

        try:
            placement_mng_group = ir_obj.get_object('placement',
                                                    'group_placement_manager')
            placement_responsible = 'group_placement_resposible_from_school'
            Placement_mem_group = ir_obj.get_object('placement',
                                                    placement_responsible)
            if placement_mng_group.id in groups:
                groups_data.update({'placement_mng': True})
            if Placement_mem_group.id in groups:
                groups_data.update({'Placement_mem': True})
        except Exception:
            groups_data.update({'placement_mng': False,
                                'Placement_mem': False})

        try:
            event_mng_group = ir_obj.get_object('school_event',
                                                'group_event_manager')
            if event_mng_group.id in groups:
                groups_data.update({'event_mng': True})
        except Exception:
            groups_data.update({'event_mng': False})

        try:
            fees_mng_group = ir_obj.get_object('school',
                                               'group_fees_manager')
            if fees_mng_group.id in groups:
                groups_data.update({'fees_mng': True})
        except Exception:
            groups_data.update({'fees_mng': False})

        try:
            addmission_registrar = 'group_admissions_registrar'
            admission_regi_group = ir_obj.get_object('school',
                                                     addmission_registrar)
            if admission_regi_group.id in groups:
                groups_data.update({'admission_regi': True})
        except Exception:
            groups_data.update({'admission_regi': False})

        teacher = []
        faculty = []
        campus = []
        department_mng = []
        student = []
        parent = []

        course = []

        if student_group.id in groups:
            groups_data.update({'student': True})
            student = env['student.student'].search([('user_id', '=',
                                                      user_rec.id)])

        if admin_group.id in groups:
            groups_data.update({'admin': True})

        if teacher_group.id in groups:
            groups_data.update({'teacher': True})
            teacher = env['school.teacher'].search([('user_id', '=',
                                                     user_rec.id)])
            if teacher:
                course = env['school.standard'].search([('user_id', '=',
                                                         teacher.id)])
        if parent_group.id in groups:
            groups_data.update({'parent': True})
            parent = env['school.parent'].search([('partner_id', '=',
                                                   user_rec.partner_id.id)])

        if campus_group.id in groups:
            groups_data.update({'campus': True})
            campus = env['school.school'].search([('campus_mng_id.user_id',
                                                   '=', user_rec.id)])
            if campus:
                course = env['school.standard'].search([('school_id', '=',
                                                         campus.id)])

        if faculty_group.id in groups:
            groups_data.update({'faculty': True})
            faculty = env['faculty.faculty'].search([('dean_id.user_id',
                                                      '=', user_rec.id)])
            if faculty:
                course = env['school.standard'].search([('faculty_id', '=',
                                                         faculty.id)])

        if department_group.id in groups:
            groups_data.update({'department': True})
            manager_user = 'department_manager_id.user_id'
            standard_obj = env['standard.standard']
            department_mng = standard_obj.search([(manager_user,
                                                   '=', user_rec.id)])
            if department_mng:
                course = env['school.standard'].search([('standard_id', '=',
                                                         department_mng.id)])

        if student_inadmission_group.id in groups:
            groups_data.update({'student_inadmission': True})

        student_ids = []
        course_ids = []
        if course:
            for c in course:
                course_ids.append(c.id)
                for s in c.student_ids:
                    student_ids.append(s.id)

        models_data = {'school_student_assignment': [],
                       'lec_assignment': [],
                       'exam_result': [], 'book_request': [],
                       'timetable': [], 'placement': [],
                       'post_lecture_notes': [],
                       'subject_syllabus': [],
                       'grade_master': [],
                       'exam_exam': []}

        try:
            stu_assignmnt_obj = env['school.student.assignment']
            student_assign = False
            if groups_data['admin']:
                student_assign = stu_assignmnt_obj.search([('state', 'in',
                                                            ('active', 'draft')
                                                            )])
            elif groups_data['student']:
                student_assign = stu_assignmnt_obj.search([('student_id',
                                                            '=', student.id),
                                                           ('state', 'in',
                                                            ('active', 'draft')
                                                            )])
            elif groups_data['teacher']:
                student_assign = stu_assignmnt_obj.search([('teacher_id',
                                                            '=', teacher.id),
                                                           ('state', 'in',
                                                            ('active', 'draft')
                                                            )])
            elif (groups_data['faculty'] or groups_data['campus'] or
                  groups_data['department']):
                    student_assign = env['school.student.assignment'
                                         ].search([('student_id',
                                                    'in',
                                                    student_ids),
                                                   ('state', 'in',
                                                    ('active', 'draft'))])
            elif groups_data['parent']:
                student_parent = 'student_id.student_parent_id'
                student_assign = stu_assignmnt_obj.search([(student_parent,
                                                            '=', parent.id),
                                                           ('state', 'in',
                                                            ('active',
                                                             'draft'))])
            for assign in student_assign:
                vals = {'Tree_Tital': 'Student Assignment',
                        'columns': ['Model',
                                    'ID',
                                    'Student',
                                    'Assignment Name',
                                    'Course Subject',
                                    'Course',
                                    'Assign Date',
                                    'Due Date',
                                    'Status'],
                        'Model': 'school.student.assignment',
                        'ID': assign.id,
                        'Assignment Name': assign.name,
                        'Course Subject': assign.subject_id.name,
                        'Course': assign.standard_id.stan_name,
                        'Assign Date': assign.assign_date,
                        'Due Date': assign.due_date,
                        'Status': assign.state}
                models_data['school_student_assignment'].append(vals)
        except Exception:
            models_data.update({'school_student_assignment': []})

        try:
            tea_assignment = env['school.teacher.assignment']
            lec_assign = False
            if groups_data['admin']:
                lec_assign = tea_assignment.search([('state', 'in',
                                                     ('active', 'draft'))])
            elif groups_data['teacher']:
                lec_assign = tea_assignment.search([('teacher_id', '=',
                                                     teacher.id),
                                                    ('state', 'in',
                                                     ('active', 'draft'))])
            elif (groups_data['faculty'] or groups_data['campus'] or
                  groups_data['department']):
                    lec_assign = tea_assignment.search([('standard_id',
                                                         'in',
                                                         course_ids),
                                                        ('state', 'in',
                                                         ('active', 'draft'))])
            for assign in lec_assign:
                vals = {'Tree_Tital': 'Lecturer Assign Assignment',
                        'columns': ['Model',
                                    'ID',
                                    'Assignment Name',
                                    'Course Subject',
                                    'Course',
                                    'Assign Date',
                                    'Due Date',
                                    'Status'],
                        'Model': 'school.teacher.assignment',
                        'ID': assign.id,
                        'Assignment Name': assign.name,
                        'Course Subject': assign.subject_id.name,
                        'Course': assign.standard_id.stan_name,
                        'Assign Date': assign.assign_date,
                        'Due Date': assign.due_date,
                        'Status': assign.state}
                models_data['lec_assignment'].append(vals)
        except Exception:
            models_data.update({'lec_assignment': []})

        try:
            exam_resu = False
            if groups_data['admin']:
                exam_resu = env['exam.exam'].search([('state', '=', 'draft')])
            elif groups_data['student']:
                exam_resu = env['exam.exam'].search([('standard_id', '=',
                                                      student.standard_id.id),
                                                     ('state', '=', 'draft')])
            elif groups_data['teacher']:
                exam_resu = env['exam.exam'].search([('standard_id', '=',
                                                      teacher.standard_id.id),
                                                     ('state', '=', 'draft')])
            elif (groups_data['faculty'] or groups_data['campus'] or
                  groups_data['department']):
                exam_resu = env['exam.exam'].search([('standard_id', '=',
                                                      course_ids),
                                                     ('state', '=', 'draft')])
            elif groups_data['parent']:
                stad_rec = parent.student_id.standard_id
                exam_resu = env['exam.exam'].search([('standard_id', '=',
                                                      stad_rec.id),
                                                     ('state', '=', 'draft')])
            for result in exam_resu:
                vals = {'Tree_Tital': 'Exam',
                        'columns': ['Model',
                                    'ID',
                                    'Exam Name',
                                    'Exam Start Date',
                                    'Exam End Date',
                                    'Exam Update Date',
                                    'Status'],
                        'Model': 'exam.exam',
                        'ID': result.id,
                        'Exam Name': result.name,
                        'Exam Start Date': result.start_date,
                        'Exam End Date': result.end_date,
                        'Exam Update Date': result.write_date,
                        'Status': result.state}
                models_data['exam_exam'].append(vals)
        except Exception:
            models_data.update({'exam_exam': []})

        try:
            grade = False
            if groups_data['admin'] or groups_data['teacher']:
                grade = env['grade.master'].search([])
            for gra in grade:
                models_data['grade_master'].append({'Tree_Tital': 'Grade',
                                                    'columns': ['Model',
                                                                'ID',
                                                                'Grade Name',
                                                                'Grade Type'],
                                                    'Model': 'grade.master',
                                                    'ID': gra.id,
                                                    'Grade Name': gra.name,
                                                    'Grade Type': gra.type})
        except Exception:
            models_data.update({'grade_master': []})

        try:
            exam_res_obj = env['exam.result']
            exam_resu = False
            if groups_data['admin']:
                exam_resu = exam_res_obj.search([('state', 'in',
                                                  ('done', 'confirm')),
                                                 ('cgpa', '<=', 2)])
            elif groups_data['student']:
                exam_resu = exam_res_obj.search([('student_id', '=',
                                                  student.id),
                                                 ('state', 'in', ('done',
                                                                  'confirm')),
                                                 ('cgpa', '<=', 2)])
            elif groups_data['teacher']:
                exam_resu = exam_res_obj.search([('standard_id', '=',
                                                  teacher.standard_id.id),
                                                 ('state', 'in', ('done',
                                                                  'confirm')),
                                                 ('cgpa', '<=', 2)])
            elif (groups_data['faculty'] or groups_data['campus'] or
                  groups_data['department']):
                exam_resu = exam_res_obj.search([('standard_id', '=',
                                                  course_ids),
                                                 ('state', 'in', ('done',
                                                                  'confirm')),
                                                 ('cgpa', '<=', 2)])
            elif groups_data['parent']:
                exam_resu = exam_res_obj.search([('student_id', '=',
                                                  parent.student_id.id),
                                                 ('state', 'in', ('done',
                                                                  'confirm')),
                                                 ('cgpa', '<=', 2)])
            for result in exam_resu:
                vals = {'Tree_Tital': 'Struggling Student',
                        'columns': ['Model',
                                    'ID',
                                    'Student Name',
                                    'Course',
                                    'Semester',
                                    'Examination',
                                    'Percentage',
                                    'CGPA',
                                    'Status'],
                        'Model': 'exam.result',
                        'ID': result.id,
                        'Student Name': result.student_id.name,
                        'Course': result.standard_id.stan_name,
                        'Semester': result.semester_id.name,
                        'Examination': result.s_exam_id.name,
                        'Percentage': result.per,
                        'CGPA': result.cgpa,
                        'Status': result.state}
                models_data['exam_result'].append(vals)
        except Exception:
            models_data.update({'exam_result': []})

        try:
            book_req = env['library.book.request']
            book_req = False
            if groups_data['admin']:
                book_req = book_req.search([('state', '=', 'draft')])
            if groups_data['librarian']:
                book_req = book_req.search([('state', '=', 'draft')])
            if groups_data['student']:
                if groups_data['userian']:
                    book_req = book_req.search([('student_id', '=',
                                                 student.id),
                                                ('state', '=', 'draft')])
            if groups_data['teacher']:
                if groups_data['userian']:
                    book_req = env['library.book.request'
                                   ].search([('teacher_id',
                                              '=',
                                              teacher.id),
                                             ('state', '=', 'draft')])
            for req in book_req:
                models_data['book_request'
                            ].append({'Tree_Tital': 'Book Requests',
                                      'columns': ['Model',
                                                  'ID',
                                                  'Request ID',
                                                  'Card No',
                                                  'Book Type',
                                                  'Status'],
                                      'Model': 'library.book.request',
                                      'ID': req.id,
                                      'Request ID': req.req_id,
                                      'Card No': req.card_id.code,
                                      'Book Type': req.type,
                                      'Status': req.state
                                      })
        except Exception:
            models_data.update({'book_request': []})

        try:
            time_table = env['time.table']
            time_table = False
            if groups_data['admin']:
                time_table = time_table.search([])
            elif groups_data['student']:
                time_table = time_table.search([('standard_id', '=',
                                                 student.standard_id.id)])
            elif groups_data['teacher']:
                time_table = time_table.search([('timetable_ids.teacher_id',
                                                 '=',
                                                 teacher.id)])
            elif (groups_data['faculty'] or groups_data['campus'] or
                  groups_data['department']):
                    time_table = time_table.search([('standard_id', 'in',
                                                     course_ids)])
            elif groups_data['parent']:
                time_table = time_table.search([('standard_id.student_ids',
                                                 'in', parent.student_id.id)])
            for table in time_table:
                class_name = table.standard_id.stan_name
                sem_name = table.semester_id.name
                models_data['timetable'].append({'Tree_Tital': 'TimeTable',
                                                 'columns': ['Model',
                                                             'ID',
                                                             'Description',
                                                             'Class',
                                                             'Semester',
                                                             'Year'],
                                                 'Model': 'time.table',
                                                 'ID': table.id,
                                                 'Description': table.name,
                                                 'Class': class_name,
                                                 'Semester': sem_name,
                                                 'Year': table.year_id.name})
        except Exception:
            models_data.update({'timetable': []})

        try:
            post_lecture = env['post.lecture.notes']
            lecture_notes = False
            if groups_data['admin']:
                lecture_notes = post_lecture.search([])
            elif groups_data['student']:
                lecture_notes = post_lecture.search([('class_id',
                                                      '=',
                                                      student.standard_id.id)])
            elif groups_data['teacher']:
                lecture_notes = post_lecture.search([('lecturer_id', '=',
                                                      teacher.id)])
            elif (groups_data['faculty'] or groups_data['campus'] or
                  groups_data['department']):
                    lecture_notes = post_lecture.search([('class_id',
                                                          'in', course_ids)])
            for lect_not in lecture_notes:
                vals = {'Tree_Tital': 'Post Lecture Notes',
                        'columns': ['Model',
                                    'ID',
                                    'Notes Name',
                                    'Lecturer',
                                    'Class',
                                    'Subject'],
                        'Model': 'post.lecture.notes',
                        'ID': lect_not.id,
                        'Notes Name': lect_not.name,
                        'Lecturer': lect_not.lecturer_id.name,
                        'Class': lect_not.class_id.stan_name,
                        'Subject': lect_not.subject_id.name}
                models_data['post_lecture_notes'].append(vals)
        except Exception:
            models_data.update({'post_lecture_notes': []})

        try:
            syllabus = False
            syllabus_obj = env['subject.syllabus']
            if groups_data['admin']:
                syllabus = syllabus_obj.search([('due_date', '>=',
                                                 date.today())])
            elif groups_data['student']:
                syllabus = syllabus_obj.search([('course_id',
                                                 '=',
                                                 student.stand_id.id),
                                                ('due_date', '>=',
                                                 date.today())])
            elif groups_data['teacher']:
                syllabus = syllabus_obj.search([('subject_id',
                                                 '=',
                                                 teacher.subject_id.id),
                                                ('due_date', '>=',
                                                 date.today())])
            elif (groups_data['faculty'] or groups_data['campus'] or
                  groups_data['department']):
                    stand_rec = course_ids.standard_id
                    syllabus = syllabus_obj.search([('course_id',
                                                     'in',
                                                     stand_rec.id),
                                                    ('due_date', '>=',
                                                     date.today())])
            for syll in syllabus:
                vals = {'Tree_Tital': 'Subject Syllabus',
                        'columns': ['Model',
                                    'ID',
                                    'Subject',
                                    'Course',
                                    'Level',
                                    'Due Date'],
                        'Model': 'subject.syllabus',
                        'ID': syll.id,
                        'Subject': syll.subject_id.name,
                        'Course': syll.course_id.name,
                        'Level': syll.level_id.name,
                        'Due Date': syll.due_date}
                models_data['subject_syllabus'].append(vals)
        except Exception:
            models_data.update({'subject_syllabus': []})

        try:
            placement = env['school.placement']
            placements = False
            if (groups_data['admin'] or groups_data['placement_mng']):
                placements = placement.search([('state', '=', 'valid')])
            elif groups_data['Placement_mem']:
                placements = placement.search([('res_school_mem_ids',
                                                'in',
                                                user_rec.partner_id.id),
                                               ('state', '=', 'valid')])
            elif groups_data['department']:
                dept_id = 'standard_id.department_manager_id'
                placements = placement.search([(dept_id,
                                                '=',
                                                user_rec.employee_ids.id),
                                               ('state', '=', 'valid')])

            for pla in placements:
                vals = {'Tree_Tital': 'Placement',
                        'columns': ['Model',
                                    'ID',
                                    'Placement Name',
                                    'Placement Member',
                                    'Recommended Position'],
                        'Model': 'school.placement',
                        'ID': pla.id,
                        'Placement Name': pla.name,
                        'Placement Member': pla.placement_partner_id.name,
                        'Recommended Position': pla.recommend_position_id.name}
                models_data['placement'].append(vals)
        except Exception:
            models_data.update({'placement': []})

        res = {'invoice_total': False,
               'invoice_outstanding_total': False,
               'invoice_paid_total': False,
               'fees_total': False,
               'fees_outstanding_total': False,
               'fees_paid_total': False,
               'canteen_total': False,
               'canteen_outstanding_total': False,
               'canteen_paid_total': False,
               'transport_total': False,
               'transport_outstanding_total': False,
               'transport_paid_total': False,
               'accomm_total': False,
               'accomm_outstanding_total': False,
               'accomm_paid_total': False,
               'issue_total': False,
               'issue_outstanding_total': False,
               'issue_paid_total': False}

        try:
            canteen_obj = env['canteen.canteen']
            invoice_details = []
            inv_obj = env['account.invoice']
            canteen_details = canteen_obj.search([('order_id.invoice_ids',
                                                   '!=',
                                                   False)])
            if (groups_data['admin'] or groups_data['fees_mng']):
                if 'accommodation_invo_id' in dir(inv_obj):
                    invoice_details = inv_obj.search([('accommodation_invo_id',
                                                       '!=', False)])
                if 'transport_id' in dir(inv_obj):
                    invoice_details += inv_obj.search([('transport_id',
                                                        '!=', False)])
                if 'payslip_bank_line_id' in dir(inv_obj):
                    invoice_details += inv_obj.search([('payslip_bank_line_id',
                                                        '!=', False)])
                if 'payslip_phy_line_id' in dir(inv_obj):
                    invoice_details += inv_obj.search([('payslip_phy_line_id',
                                                        '!=', False)])
                if 'payslip_id' in dir(inv_obj):
                    invoice_details += inv_obj.search([('payslip_id',
                                                        '!=', False)])
                if 'penalty_id' in dir(inv_obj):
                    invoice_details += inv_obj.search([('penalty_id', '!=',
                                                      False)])
                    partner_rec = user_rec.partner_id
                invoice_details += inv_obj.search([('partner_id', '=',
                                                    partner_rec.id)])
                for canteen in canteen_details:
                    if canteen.order_id.invoice_ids:
                        inv_id = canteen.order_id.invoice_ids.id
                        invoice_details += inv_obj.sudo().search([('id', '=',
                                                                   inv_id)])
            elif groups_data['student']:
                partner_rec = user_rec.partner_id
                invoice_details = inv_obj.sudo().search([('partner_id', '=',
                                                          partner_rec.id)])
            elif groups_data['accommo_mng']:
                invoice_details = inv_obj.sudo().search([('name', '=',
                                                          'Accommodation')])
            elif groups_data['hostel_manager']:
                temp = 'Accommodation For Room'
                invoice_details = inv_obj.sudo().search([('name', '=',
                                                          temp)])
            elif groups_data['canteen_manager']:
                for canteen in canteen_details:
                    if canteen.order_id.invoice_ids:
                        inv_id = canteen.order_id.invoice_ids.id
                        invoice_details += inv_obj.sudo().search([('id', '=',
                                                                   inv_id)])
            elif (groups_data['teacher'] or groups_data['faculty'] or
                  groups_data['campus'] or groups_data['department']):
                    partner = []
                    for c in course:
                        for s in c.student_ids:
                            partner.append(s.partner_id.id)
                    partner.append(user_rec.partner_id.id)
                    invoice_details = inv_obj.sudo().search([('partner_id',
                                                              'in',
                                                              partner)])
            elif groups_data['parent']:
                part_rec = parent.student_id.partner_id
                invoice_details = inv_obj.sudo().search([('partner_id',
                                                          'in',
                                                          part_rec.id)])
            elif groups_data['admission_regi']:
                partner_rec = user_rec.partner_id
                invoice_details = inv_obj.sudo().search([('partner_id',
                                                          '=',
                                                          partner_rec.id)])

            if invoice_details:
                inv_total = 0.0
                inv_os_total = 0.0
                inv_paid_total = 0.0
                for invoice in invoice_details:
                    if invoice.state in ('draft', 'paid', 'open'):
                        inv_total += invoice.amount_total
                    if invoice.state in ('open', 'draft'):
                        inv_os_total += invoice.amount_total
                    if invoice.state in ('paid'):
                        inv_paid_total += invoice.amount_total
                res.update({'invoice_total': round(inv_total, 2),
                            'invoice_outstanding_total': round(inv_os_total,
                                                               2),
                            'invoice_paid_total': round(inv_paid_total, 2)})
        except Exception:
            res.update({'invoice_total': False,
                        'invoice_outstanding_total': False,
                        'invoice_paid_total': False})

        try:
            fees = []
            payslip = env['student.payslip']
            if groups_data['admin'] or groups_data['fees_mng']:
                fees = payslip.search([('state', 'in',
                                        ('paid', 'confirm', 'submit'))])
            elif groups_data['student']:
                fees = payslip.search([('student_id', '=', student.id),
                                       ('state', 'in',
                                        ('paid', 'confirm', 'submit'))])
            elif (groups_data['teacher'] or groups_data['faculty'] or
                  groups_data['campus'] or groups_data['department']):
                    for s in course.student_ids:
                        fees = payslip.search([('student_id',
                                                '=', s.id),
                                               ('state', 'in',
                                                ('paid', 'confirm', 'submit'))
                                               ])
            elif groups_data['parent']:
                fees = payslip.search([('student_id.student_parent_id',
                                        '=', parent.id),
                                       ('state', 'in',
                                        ('paid', 'confirm', 'submit'))])
            fees_total = 0.0
            fees_os_total = 0.0
            fees_paid_total = 0.0
            if fees:
                for fee_total in fees:
                    if fee_total.state in ('confirm'):
                        for fee in fee_total.line_ids:
                            if fee.invoice_id:
                                if fee.invoice_id.state in ('paid', 'draft',
                                                            'open'):
                                    fees_total = fees_total + fee.amount
                                if fee.invoice_id.state in ('draft', 'open'):
                                    fees_os_total += fee.amount
                                if fee.invoice_id.state in ('paid'):
                                    fees_paid_total += fee.amount
                    if fee_total.state in ('paid', 'submit'):
                        fees_total = fees_total + fee_total.total
                    if fee_total.state in ('submit'):
                        fees_os_total += fee_total.total
                    if fee_total.state in ('paid'):
                        fees_paid_total = fees_paid_total + fee_total.total
                res.update({'fees_total': round(fees_total, 2),
                            'fees_outstanding_total': round(fees_os_total,
                                                            2),
                            'fees_paid_total': round(fees_paid_total, 2)})
        except Exception:
            res.update({'fees_total': False,
                        'fees_outstanding_total': False,
                        'fees_paid_total': False})

        try:
            canteen = env['canteen.canteen']
            canteen_details = []
            temp_condision = groups_data['canteen_manager']
            temp_fees = groups_data['fees_mng']
            if (groups_data['admin'] or temp_fees or temp_condision):
                canteen_details = canteen.search([('order_id.invoice_ids',
                                                   '!=', False)])
            elif groups_data['student']:
                canteen_details = canteen.search([('student_id', '=',
                                                   student.id),
                                                  ('order_id.invoice_ids',
                                                   '!=', False)])
            elif (groups_data['teacher'] or groups_data['faculty'] or
                  groups_data['campus'] or groups_data['department']):
                part_rec = user_rec.partner_id
                canteen_details = canteen.search(['|', ('partner_id', '=',
                                                        part_rec.id),
                                                  ('student_id', 'in',
                                                   student_ids),
                                                  ('order_id.invoice_ids',
                                                   '!=',
                                                   False)])
            elif groups_data['parent']:
                parent = 'student_id.student_parent_id'
                inv_ids = 'order_id.invoice_ids'
                canteen_details = canteen.search([(parent, '=', parent.id),
                                                  (inv_ids, '!=', False)])

            canteen_total = 0.0
            cantn_os_total = 0.0
            cantn_paid_total = 0.0
            if canteen_details:
                for canteen in canteen_details:
                    if canteen.order_id.invoice_ids:
                        if canteen.order_id.invoice_ids.state in ('draft',
                                                                  'open',
                                                                  'paid'):
                            canteen_total += canteen.amount_total
                        if canteen.order_id.invoice_ids.state in ('open',
                                                                  'draft'):
                            cantn_os_total += canteen.amount_total
                        if canteen.order_id.invoice_ids.state in ('paid'):
                            cantn_paid_total += canteen.amount_total
                res.update({'canteen_total': round(canteen_total, 2),
                            'canteen_outstanding_total': round(cantn_os_total,
                                                               2),
                            'canteen_paid_total': round(cantn_paid_total, 2)})
        except Exception:
            res.update({'canteen_total': False,
                        'canteen_outstanding_total': False,
                        'canteen_paid_total': False})

        try:
            trans = env['transport.registration']
            trans_details = False
            if groups_data['admin'] or groups_data['fees_mng']:
                trans_details = trans.search([('state', 'in',
                                               ('paid', 'validate')),
                                              ('invoice_id', '!=', False)])
            elif groups_data['student']:
                trans_details = trans.search([('part_name', '=',
                                               student.id),
                                              ('state', 'in',
                                               ('paid', 'validate')),
                                              ('invoice_id', '!=', False)])
            elif (groups_data['teacher'] or groups_data['faculty'] or
                  groups_data['campus'] or groups_data['department']):
                trans_details = trans.search([('part_name', '=',
                                               student_ids),
                                              ('state', 'in',
                                               ('paid', 'validate')),
                                              ('invoice_id', '!=', False)])
            elif groups_data['parent']:
                trans_details = trans.search([('part_name.student_parent_id',
                                               '=', parent.id),
                                              ('state', 'in',
                                               ('paid', 'validate')),
                                              ('invoice_id', '!=', False)])

            if trans_details:
                trans_os_total = 0.0
                transport_total = 0.0
                transport_paid_total = 0.0
                for transport in trans_details:
                    if transport.invoice_id:
                        if transport.state in ('paid', 'validate'):
                            transport_total += transport.amount
                        if transport.state in ('validate'):
                            trans_os_total += transport.amount
                        if transport.state in ('paid'):
                            transport_paid_total += transport.amount
                t_os_total = round(trans_os_total, 2)
                res.update({'transport_total': round(transport_total, 2),
                            'transport_outstanding_total': t_os_total,
                            'transport_paid_total': round(transport_paid_total,
                                                          2)})
        except Exception:
            res.update({'transport_total': False,
                        'transport_outstanding_total': False,
                        'transport_paid_total': False})

        try:
            accomm_details = False
            acc_obj = env['accommodation.accommodation']
            temp_admin = groups_data['admin']
            temp_acc = groups_data['accommo_mng']
            if (temp_admin or temp_acc or groups_data['fees_mng']):
                accomm_details = acc_obj.search([('state', 'in',
                                                  ('paid', 'invoice'))])
            elif groups_data['student']:
                accomm_details = acc_obj.search([('student_id', '=',
                                                  student.id),
                                                 ('state', 'in',
                                                  ('paid', 'invoice'))])
            elif groups_data['hostel_manager']:
                accomm_details = acc_obj.search(['|', ('accommodation_user',
                                                       '=', 'student'),
                                                 ('employee_id.user_id', '=',
                                                  user_rec.id),
                                                 ('state', 'in',
                                                  ('paid', 'invoice'))])
            elif (groups_data['teacher'] or groups_data['faculty'] or
                  groups_data['campus'] or groups_data['department']):
                accomm_details = acc_obj.search(['|',
                                                 ('student_id', 'in',
                                                  student_ids),
                                                 ('employee_id.user_id', '=',
                                                  user_rec.id),
                                                 ('state', 'in',
                                                  ('paid', 'invoice'))])
            elif groups_data['parent']:
                parent = 'student_id.student_parent_id'
                accomm_details = acc_obj.search([(parent, '=',
                                                  parent.id),
                                                 ('state', 'in',
                                                  ('paid', 'invoice'))])
            elif groups_data['admission_regi']:
                accomm_details = acc_obj.search([('employee_id.user_id',
                                                  '=', user_rec.id),
                                                 ('state', 'in',
                                                  ('paid', 'invoice'))])
            accomm_total = 0.0
            accomm_os_total = 0.0
            accomm_paid_total = 0.0
            if accomm_details:
                for accomm in accomm_details:
                    if accomm.state in ('paid', 'invoice'):
                        accomm_total = accomm_total + accomm.rent
                    if accomm.state in ('invoice'):
                        accomm_os_total += accomm.rent
                    if accomm.state in ('paid'):
                        accomm_paid_total += accomm.rent
                res.update({'accomm_total': round(accomm_total, 2),
                            'accomm_outstanding_total': round(accomm_os_total,
                                                              2),
                            'accomm_paid_total': round(accomm_paid_total, 2)})
        except Exception:
            res.update({'accomm_total': False,
                        'accomm_outstanding_total': False,
                        'accomm_paid_total': False})

        try:
            issue_details = False
            issue = env['library.book.issue']
            librarian = groups_data['librarian']
            if (groups_data['admin'] or librarian or groups_data['fees_mng']):
                issue_details = issue.search([('invoice_id', '!=', False)])
            elif groups_data['student']:
                if groups_data['userian']:
                    issue_details = issue.search([('student_id',
                                                   '=', student.id),
                                                  ('invoice_id', '!=', False)])
            elif groups_data['teacher']:
                if groups_data['userian']:
                    book_req = issue.search([('teacher_id',
                                              '=',
                                              teacher.id),
                                             ('invoice_id', '!=', False)])

            issue_os_total = 0.0
            issue_total = 0.0
            issue_paid_total = 0.0
            if issue_details:
                for issue in issue_details:
                    if issue.invoice_id:
                        if issue.state in ('done', 'pay_fine', 'fine'):
                            issue_total += issue.penalty
                        if issue.state in ('pay_fine', 'fine'):
                            issue_os_total += issue.penalty
                        if issue.state in ('done'):
                            issue_paid_total += issue.penalty
                res.update({'issue_total': round(issue_total, 2),
                            'issue_outstanding_total': round(issue_os_total,
                                                             2),
                            'issue_paid_total': round(issue_paid_total,
                                                      2)})
        except Exception:
            res.update({'issue_total': False,
                        'issue_outstanding_total': False,
                        'issue_paid_total': False})

# NEWS #
        news = env['student.news']
        news_details = news.search([('date', '>=',
                                     time.strftime('%Y-%m-%d'))])
        news_data = {'news': []}
        if news_details:
            for new in news_details:
                news_data['news'].append({'columns': ['ID',
                                                      'Subject'],
                                          'ID': new.id,
                                          'Subject': new.subject})

        reminder_details = []
        if groups_data['admin']:
            reminder_details = news.search([('date', '>=',
                                             date.today())])
        elif groups_data['student']:
            reminder_details = news.search([('date', '>=',
                                             date.today()),
                                            ('stu_id', '=',
                                             student.id)])
        elif (groups_data['teacher'] or groups_data['faculty'] or
              groups_data['campus'] or groups_data['department']):
            reminder_details = news.search([('date', '>=',
                                             date.today()),
                                            ('stu_id', 'in',
                                             student_ids)])
        elif groups_data['parent']:
            reminder_details = news.search([('date', '>=',
                                             date.today()),
                                            ('stu_id.student_parent_id',
                                             '=', parent.id)])
        elif groups_data['fees_mng']:
            reminder = env['student.reminder']
            reminder_details = reminder.search([('date', '>=', date.today())])

        reminders_data = {'reminder': []}
        for remi in reminder_details:
            reminders_data['reminder'].append({'columns': ['ID',
                                                           'Name'],
                                               'ID': remi.id,
                                               'Name': remi.name})

        return [res, models_data, groups_data, news_data, reminders_data]
