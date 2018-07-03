# -*- coding: utf-8 -*-
# See LICENSE file for full copyright and licensing details.

from odoo import models, fields, api


class TerminateReasonLibrary(models.TransientModel):
    _inherit = 'terminate.reason'

    info = fields.Text('Message')

    @api.model
    def default_get(self, fields):
        '''Override method to display message if student has issued book
        while terminate student'''
        res = super(TerminateReasonLibrary, self).default_get(fields)
        student = self._context.get('active_id')
        student_obj = self.env['student.student'].browse(student)
        library_card = self.env['library.card'].\
            search([('student_id', '=', student_obj.id),
                    ('state', '=', 'running')])
        book_issue = self.env['library.book.issue'].\
            search([('state', 'in', ['issue', 'reissue']),
                    ('student_id', '=', student_obj.id)])
        card_info = ''
        if library_card:
            card_info += 'The student has library card assigned with number' +\
                ' ' + library_card.code or ''
        if book_issue:
            for data in book_issue:
                card_info += '\nStudent has issued the book ' + ' ' +\
                    data.name.name + ' ' + 'issue number is' +\
                    ' ' + data.issue_code + ' ' +\
                    'and library card number is' + ' ' + data.card_id.code
        res.update({'info': card_info})
        return res
