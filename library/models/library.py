# -*- coding: utf-8 -*-
# See LICENSE file for full copyright and licensing details.

import time
from datetime import datetime
from odoo import models, fields, api, _
from odoo.exceptions import ValidationError, Warning as UserError
from odoo.tools import DEFAULT_SERVER_DATE_FORMAT
from dateutil.relativedelta import relativedelta as rd


class LibraryRack(models.Model):
    _name = 'library.rack'
    _description = "Library Rack"

    name = fields.Char('Name', required=True,
                       help="it will be show the position of book")
    code = fields.Char('Code')
    active = fields.Boolean('Active', default='True')


class LibraryAuthor(models.Model):
    _name = 'library.author'
    _description = "Author"

    name = fields.Char('Name', required=True)
    born_date = fields.Date('Date of Birth')
    death_date = fields.Date('Date of Death')
    biography = fields.Text('Biography')
    note = fields.Text('Notes')
    editor_ids = fields.Many2many('res.partner', 'author_editor_rel',
                                  'author_id', 'parent_id', 'Editors')

    _sql_constraints = [('name_uniq', 'unique (name)',
                         'The name of the author must be unique !')]


class LibraryCard(models.Model):
    _name = "library.card"
    _description = "Library Card information"
    _rec_name = "code"

    @api.onchange('student_id')
    def on_change_student(self):
        '''  This method automatically fill up student roll number
             and standard field  on student_id field
        @param self : Object Pointer
        @param cr : Database Cursor
        @param uid : Current Logged in User
        @param ids : Current Records
        @student : Apply method on this Field name
        @param context : standard Dictionary
        @return : Dictionary having identifier of the record as key
            and the value of student roll number and standard'''
        student_data = self.env['student.student'].browse(self.student_id.id)
        self.standard_id = student_data.standard_id.id
        self.roll_no = student_data.roll_no

    @api.multi
    @api.depends('student_id')
    def _compute_name(self):
        for rec in self:
            if rec.student_id:
                user = rec.student_id.name
            else:
                user = rec.teacher_id.name
            rec.gt_name = user

    @api.model
    def create(self, vals):
        if vals.get('student_id'):
            student = self.env['student.student'].browse(vals.get('student_id'
                                                                  ))
            vals.update({'standard_id': student.standard_id.id,
                         'roll_no': student.roll_no})
        return super(LibraryCard, self).create(vals)

    @api.multi
    def write(self, vals):
        if vals.get('student_id'):
            student = self.env['student.student'].browse(vals.get('student_id'
                                                                  ))
            vals.update({'standard_id': student.standard_id.id,
                         'roll_no': student.roll_no})
        return super(LibraryCard, self).write(vals)

    @api.multi
    @api.depends('start_date', 'duration')
    def _compute_end_date(self):
        for rec in self:
            if rec.start_date:
                date_diff = datetime.strptime(rec.start_date,
                                              DEFAULT_SERVER_DATE_FORMAT)
                rec.end_date = date_diff + rd(months=rec.duration)

    code = fields.Char('Card No', required=True, default=lambda self: _('New'))
    book_limit = fields.Integer('No Of Book Limit On Card', required=True)
    student_id = fields.Many2one('student.student', 'Student Name')
    standard_id = fields.Many2one('school.standard', 'Standard')
    gt_name = fields.Char(compute="_compute_name", method=True, string='Name')
    user = fields.Selection([('student', 'Student'), ('teacher', 'Teacher')],
                            'User')
    state = fields.Selection([('draft', 'Draft'),
                              ('running', 'Confirm'),
                              ('expire', 'Expire'),
                              ],
                             "State", default='draft')
    roll_no = fields.Integer('Roll No')
    teacher_id = fields.Many2one('school.teacher', 'Teacher Name')
    start_date = fields.Date('Start Date', default=fields.Date.context_today)
    duration = fields.Integer('Duration',
                              help="Duration in months")
    end_date = fields.Date('End Date', compute="_compute_end_date", store=True)

    @api.constrains('student_id', 'teacher_id')
    def check_member_card(self):
        if self.user == 'student':
            student_lib_card = self.search([('student_id', '=',
                                             self.student_id.id),
                                            ('id', 'not in', self.ids),
                                            ('state', '!=', 'expire')])
            if student_lib_card:
                raise ValidationError(_('''You cannot assign library card to
                same student more than once!'''))
        if self.user == 'teacher':
            teacher_lib_card = self.search([('teacher_id', '=',
                                             self.teacher_id.id),
                                            ('id', 'not in', self.ids),
                                            ('state', '!=', 'expire')])
            if teacher_lib_card:
                raise ValidationError(_('''You cannot assign library card to
                same teacher more than once!'''))

    @api.multi
    def running_state(self):
        self.code = self.env['ir.sequence'].next_by_code('library.card'
                                                         ) or _('New')
        self.state = 'running'

    @api.multi
    def draft_state(self):
        self.write({'state': 'draft'})

    @api.multi
    def unlink(self):
        for rec in self:
            if rec.state == 'running':
                raise ValidationError(_('''You cannot delete a confirmed
                library card!'''))
        return super(LibraryCard, self).unlink()

    @api.multi
    def librarycard_expire(self):
        '''Schedular to change in librarycard state when end date
            is over'''
        current_date = datetime.now()
        new_date = datetime.strftime(current_date, '%m/%d/%Y')
        lib_card = self.env['library.card']
        lib_card_search = lib_card.search([('end_date', '<',
                                            new_date)])
        if lib_card_search:
            for rec in lib_card_search:
                rec.state = 'expire'


class LibraryBookIssue(models.Model):
    '''Book variant of product'''
    _name = "library.book.issue"
    _description = "Library information"
    _rec_name = "standard_id"

    @api.onchange('date_issue', 'day_to_return_book')
    def onchange_day_to_return_book(self):
        ''' This method calculate a book return date.
        @param self : Object Pointer
        @param cr : Database Cursor
        @param uid : Current Logged in User
        @param ids : Current Records
        @param name : Functional field's name
        @param args : Other arguments
        @param context : standard Dictionary
        @return : Dictionary having identifier of the record as key
                  and the book return date as value'''
        t = "%Y-%m-%d %H:%M:%S"
        diff = rd(days=self.day_to_return_book or 0.0)
        if self.date_issue and diff:
            ret_date = datetime.strptime(self.date_issue, t) + diff
            self.date_return = ret_date

    @api.multi
    @api.depends('date_issue', 'day_to_return_book')
    def _compute_return_date(self):
        ''' This method calculate a book return date.
        @param self : Object Pointer
        @param cr : Database Cursor
        @param uid : Current Logged in User
        @param ids : Current Records
        @param name : Functional field's name
        @param args : Other arguments
        @param context : standard Dictionary
        @return : Dictionary having identifier of the record as key
                  and the book return date as value'''
        t = "%Y-%m-%d %H:%M:%S"
        for rec in self:
            diff = rd(days=rec.day_to_return_book or 0.0)
            if rec.date_issue and diff:
                ret_date = datetime.strptime(rec.date_issue, t) + diff
                rec.date_return = ret_date

    @api.multi
    @api.depends('actual_return_date', 'day_to_return_book')
    def _compute_penalty(self):
        ''' This method calculate a penalty on book .
        @param self : Object Pointer
        @param cr : Database Cursor
        @param uid : Current Logged in User
        @param ids : Current Records
        @param name : Functional field's name
        @param args : Other arguments
        @param context : standard Dictionary
        @return : Dictionary having identifier of the record as key
                  and penalty as value
        '''
        for line in self:
            if line.date_return:
                start_day = datetime.strptime(line.actual_return_date,
                                              "%Y-%m-%d %H:%M:%S")
                end_day = datetime.strptime(line.date_return,
                                            "%Y-%m-%d %H:%M:%S")
                if start_day > end_day:
                    diff = rd(start_day.date(), end_day.date())
                    day = float(diff.days) or 0.0
                    if line.day_to_return_book:
                        line.penalty = day * line.name.fine_late_return or 0.0

    @api.multi
    @api.depends('state')
    def _compute_lost_penalty(self):
        ''' This method calculate a penalty on book lost .
        @param self : Object Pointer
        @param cr : Database Cursor
        @param uid : Current Logged in User
        @param ids : Current Records
        @param name : Functional field's name
        @param args : Other arguments
        @param context : standard Dictionary
        @return : Dictionary having identifier of the record as key
                  and book lost penalty as value
        '''

        for rec in self:
            if rec.state and rec.state == 'lost':
                rec.lost_penalty = rec.name.fine_lost or 0.0

    @api.multi
    @api.constrains('card_id', 'state')
    def _check_issue_book_limit(self):
        ''' This method used how many book can issue as per user type  .
        @param self : Object Pointer
        @param cr : Database Cursor
        @param uid : Current Logged in User
        @param ids : Current Records
        @param context : standard Dictionary
        @return : True or False
        '''
        for rec in self:
            if rec.card_id:
                card_ids = rec.search([('card_id', '=', rec.card_id.id),
                                       ('state', 'in', ['issue', 'reissue'])])
                if rec.state == 'issue' or rec.state == 'reissue':
                    if rec.card_id.book_limit > len(card_ids) - 1:
                        return True
                    else:
                        # Check the book issue limit on card if it is over it
                        # give warning
                        raise ValidationError(_('''Book issue limit is over on
                        this card!'''))
                else:
                    if rec.card_id.book_limit > len(card_ids):
                        return True
                    else:
                        raise ValidationError(_('''Book issue limit is over on
                        this card!'''))

    @api.depends('name')
    def _compute_check_ebook(self):
        for rec in self:
            if rec.name.is_ebook:
                rec.ebook_check = True

    name = fields.Many2one('product.product', 'Book Name', required=True)
    issue_code = fields.Char('Issue No.', required=True,
                             default=lambda self: _('New'))
    student_id = fields.Many2one('student.student', 'Student Name')
    teacher_id = fields.Many2one('school.teacher', 'Teacher Name')
    gt_name = fields.Char('Name')
    standard_id = fields.Many2one('school.standard', 'Standard')
    roll_no = fields.Integer('Roll No')
    invoice_id = fields.Many2one('account.invoice', "User's Invoice")
    date_issue = fields.Datetime('Release Date', required=True,
                                 help="Release(Issue) date of the book",
                                 default=lambda *a:
                                 time.strftime('%Y-%m-%d %H:%M:%S'))
    date_return = fields.Datetime(compute="_compute_return_date",
                                  string='Return Date',
                                  store=True,
                                  help="Book To Be Return On This Date")
    actual_return_date = fields.Datetime("Actual Return Date",
                                         help="Actual Return Date of Book",
                                         default=lambda *
                                         a: time.strftime('%Y-%m-%d %H:%M:%S'))
    penalty = fields.Float(compute="_compute_penalty",
                           string='Penalty', store=True,
                           help='It show the late book return penalty')
    lost_penalty = fields.Float(compute="_compute_lost_penalty",
                                string='Fine', store=True,
                                help='It show the penalty for lost book')
#    return_days = fields.Integer('Return Days')
    day_to_return_book = fields.Integer('Book Return Days')
    card_id = fields.Many2one("library.card", "Card No", required=True)
    state = fields.Selection([('draft', 'Draft'), ('issue', 'Issued'),
                              ('reissue', 'Reissued'), ('cancel', 'Cancelled'),
                              ('return', 'Returned'), ('lost', 'Lost'),
                              ('fine', 'Fined'),
                              ('paid', 'Done'),
                              ('subscribe', 'Subscribe'),
                              ('pending', 'Pending'),
                              ],
                             "State", default='draft')
    user = fields.Char("User")
    compute_inv = fields.Integer('Number of invoice',
                                 compute="_compute_invoices")
    color = fields.Integer("Color Index")
    payment_mode = fields.Selection([('pay_physically', 'Pay Cash'),
                                     ('by_bank', 'Pay By Bank')],
                                    "Payment Mode")
    subscription_amt = fields.Float("Subscription Amount")
    bank_teller_no = fields.Char("Bank Teller No.")
    bank_teller_amt = fields.Float("Bank Teller Amount")
    ebook_download = fields.Binary('Download Book')
    ebook_check = fields.Boolean("Check Ebbok", compute="_compute_check_ebook")

    @api.onchange('card_id')
    def onchange_card_issue(self):
        ''' This method automatically fill up values on card.
            @param self : Object Pointer
            @param cr : Database Cursor
            @param uid : Current Logged in User
            @param ids : Current Records
            @param card : applied change on this field
            @param context : standard Dictionary
            @return : Dictionary having identifier of the record as key
                      and the user info as value
        '''
        if self.card_id:
            self.user = str(self.card_id.user.title()) or ''
            if self.card_id.user.title() == 'Student':
                self.student_id = self.card_id.student_id.id or False
                self.standard_id = self.card_id.standard_id.id or False
                self.roll_no = int(self.card_id.roll_no) or False
                self.gt_name = self.card_id.gt_name or ''

            else:
                self.teacher_id = self.card_id.teacher_id.id
                self.gt_name = self.card_id.gt_name

    @api.constrains('card_id', 'name')
    def check_book_issue(self):
        book_issue = self.search([('name', '=', self.name.id),
                                  ('id', 'not in', self.ids),
                                  ('card_id', '=', self.card_id.id),
                                  ('state', 'not in', ['draft', 'cancel',
                                                       'return', 'paid'])])
        if book_issue:
            raise ValidationError(_('''You cannot issue same book on
                                    same card more than once at same time!'''))

    @api.model
    def create(self, vals):
        '''Override create method'''
        if vals.get('card_id'):
            # fetch the record of user type student
            card = self.env['library.card'].browse(vals.get('card_id'))
            vals.update({'student_id': card.student_id.id,
                         'card_id': card.id,
                         'user': str(card.user.title()),
                         'standard_id': card.standard_id.id,
                         'roll_no': int(card.roll_no),
                         'gt_name': card.gt_name
                         })
        if vals.get('card_id') and vals.get('user') == 'Teacher':
            # fetch the record of user type teacher
            card = self.env['library.card'].browse(vals.get('card_id'))
            vals.update({'teacher_id': card.teacher_id.id,
                         'gt_name': card.gt_name,
                         'user': str(card.user.title()),
                         })
        return super(LibraryBookIssue, self).create(vals)

    @api.multi
    def write(self, vals):
        '''Override write method'''
        # update the details of user type student
        if vals.get('card_id'):
            card = self.env['library.card'].browse(vals.get('card_id'))
            vals.update({'student_id': card.student_id.id,
                         'card_id': card.id,
                         'user': str(card.user.title()),
                         'standard_id': card.standard_id.id,
                         'roll_no': int(card.roll_no),
                         'gt_name': card.gt_name
                         })
        if vals.get('card_id') and vals.get('user') == 'Teacher':
            # upate the details of user type Teacher
            card = self.env['library.card'].browse(vals.get('card_id'))
            vals.update({'teacher_id': card.teacher_id.id,
                         'gt_name': card.gt_name,
                         'user': str(card.user.title()),
                         })
        return super(LibraryBookIssue, self).write(vals)

    @api.multi
    def draft_book(self):
        '''
        This method for books in draft state.
        @param self : Object Pointer
        @param cr : Database Cursor
        @param uid : Current Logged in User
        @param ids : Current Records
        @param context : standard Dictionary
        @return : True
        '''
        self.write({'state': 'draft'})

    @api.multi
    def issue_book(self):
        '''
        This method used for issue a books.
        @param self : Object Pointer
        @param cr : Database Cursor
        @param uid : Current Logged in User
        @param ids : Current Records
        @param context : standard Dictionary
        @return : True
        '''

        curr_dt = datetime.now()
        new_date = datetime.strftime(curr_dt,
                                     '%m/%d/%Y')
        if (self.card_id.end_date < new_date and
                self.card_id.end_date > new_date):
                raise ValidationError(_('''The Membership of library
                card is over!'''))
#        if self.issue_code == 'New':
        code_issue = self.env['ir.sequence'
                              ].next_by_code('library.book.issue'
                                             ) or _('New')
        for rec in self:
            if (rec.name and rec.name.availability == 'notavailable' and
                    not rec.name.is_ebook):
                    raise ValidationError(_('''The book you have selected is
                    not available now. Please try after sometime!'''))
            if rec.student_id:
                issue_str = ''
                book_fines = rec.search([('card_id', '=', rec.card_id.id),
                                         ('state', '=', 'fine')])
                if book_fines:
                    for book in book_fines:
                        issue_str += str(book.issue_code) + ', '
                        # check if fine on book is paid until then user
                        # cannot issue new book
                    raise UserError(_('You can not request for a book until'
                                      ' the fine is not paid for book issues'
                                      ' %s!') % issue_str)
            if rec.card_id:
                card_ids = rec.search([('card_id', '=', rec.card_id.id),
                                       ('state', 'in', ['issue', 'reissue'])])
                if rec.card_id.book_limit > len(card_ids):
                    return_day = rec.name.day_to_return_book
                    rec.write({'state': 'issue',
                               'day_to_return_book': return_day,
                               'issue_code': code_issue
                               })
            return True

    @api.multi
    def reissue_book(self):
        '''
        This method used for reissue a books.
        @param self : Object Pointer
        @param cr : Database Cursor
        @param uid : Current Logged in User
        @param ids : Current Records
        @param context : standard Dictionary
        @return : True
        '''
        self.write({'state': 'reissue',
                    'date_issue': time.strftime('%Y-%m-%d %H:%M:%S')})

    @api.multi
    def return_book(self):
        '''
        This method used for return a books.
        @param self : Object Pointer
        @param cr : Database Cursor
        @param uid : Current Logged in User
        @param ids : Current Records
        @param context : standard Dictionary
        @return : True
        '''
        self.write({'state': 'return'})

    @api.multi
    def lost_book(self):
        stock_scrap_obj = self.env['stock.scrap']
        for rec in self:
            scrap_fields = list(stock_scrap_obj._fields)
            scrap_vals = stock_scrap_obj.default_get(scrap_fields)
            origin_str = 'Book lost : '
            if rec.issue_code:
                origin_str += rec.issue_code
            if rec.student_id:
                origin_str += "(" + rec.student_id.name + ")" or ''
            scrap_vals.update({'product_id': rec.name.id,
                               'product_uom_id': rec.name.uom_id.id,
                               'origin': origin_str})
            stock_scrap_obj.with_context({'book_lost': True}
                                         ).create(scrap_vals)
            rec.state = 'lost'
            rec.lost_penalty = self.name.fine_lost
        return True

    @api.multi
    def cancel_book(self):
        '''
        This method used for cancel book issue.
        @param self : Object Pointer
        @param cr : Database Cursor
        @param uid : Current Logged in User
        @param ids : Current Records
        @param context : standard Dictionary
        @return : True
        '''
        self.write({'state': 'cancel'})

    @api.multi
    def user_fine(self):
        '''
        This method used when penalty on book either late return or book lost
        and generate invoice of fine.
        @param self : Object Pointer
        @param cr : Database Cursor
        @param uid : Current Logged in User
        @param ids : Current Records
        @param context : standard Dictionary
        @return : new form of account.invoice
        '''
#
        invoice_obj = self.env['account.invoice']
        for record in self:
            if record.user == 'Student':
                usr = record.student_id.partner_id.id
                if not record.student_id.partner_id.contact_address:
                    raise UserError(_('Error!'
                                    'The Student must have a Home address!'))
            else:
                usr = record.teacher_id.employee_id.user_id.partner_id.id
                if not record.teacher_id.employee_id.address_home_id:
                    raise UserError(_('Error ! Teacher must have a Home'
                                      'address.'))
            vals_invoice = {'type': 'out_invoice',
                            'partner_id': usr,
                            'book_issue': record.id,
                            'book_issue_reference': record.issue_code or ''}
            new_invoice_id = invoice_obj.create(vals_invoice)
            acc_id = new_invoice_id.journal_id.default_credit_account_id.id
            invoice_line_ids = []
            if record.lost_penalty:
                lost_pen = record.lost_penalty
                invoice_line2 = {'name': 'Book Lost Fine',
                                 'price_unit': lost_pen,
                                 'invoice_id': new_invoice_id.id,
                                 'account_id': acc_id}
                invoice_line_ids.append((0, 0, invoice_line2))
            if record.penalty:
                pen = record.penalty
                invoice_line1 = {'name': 'Late Return Penalty',
                                 'price_unit': pen,
                                 'invoice_id': new_invoice_id.id,
                                 'account_id': acc_id}
                invoice_line_ids.append((0, 0, invoice_line1))
            new_invoice_id.write({'invoice_line_ids': invoice_line_ids})
        self.write({'state': 'fine'})
        view_id = self.env.ref('account.invoice_form')
        return {'name': _("New Invoice"),
                'view_mode': 'form',
                'view_id': view_id.ids,
                'view_type': 'form',
                'res_model': 'account.invoice',
                'type': 'ir.actions.act_window',
                'nodestroy': True,
                'res_id': new_invoice_id.id,
                'target': 'current',
                'context': {'default_type': 'out_invoice'}}

    @api.multi
    def subscription_pay(self):
        invoice_obj = self.env['account.invoice']
        for record in self:
            if record.user == 'Student':
                usr = record.student_id.partner_id.id
                if not record.student_id.partner_id.contact_address:
                    raise UserError(_('Error !'
                                    'The Student must have a Home address.'))
            else:
                usr = record.teacher_id.employee_id.user_id.partner_id.id
                if not record.teacher_id.employee_id.address_home_id:
                    raise UserError(_('Error ! Teacher must have a Home'
                                      'address!.'))
            vals_invoice = {'type': 'out_invoice',
                            'partner_id': usr,
                            'book_issue': record.id,
                            'book_issue_reference': record.issue_code or ''}
            new_invoice_id = invoice_obj.create(vals_invoice)
            acc_id = new_invoice_id.journal_id.default_credit_account_id.id
            invoice_line_ids = []
            if record.subscription_amt:
                subcription_amount = record.subscription_amt
                invoice_line3 = {'name': 'Book Subscription Amount',
                                 'price_unit': subcription_amount,
                                 'invoice_id': new_invoice_id.id,
                                 'account_id': acc_id}
                invoice_line_ids.append((0, 0, invoice_line3))
            new_invoice_id.write({'invoice_line_ids': invoice_line_ids})
        self.write({'state': 'pending'})
        view_id = self.env.ref('account.invoice_form')
        return {'name': _("New Invoice"),
                'view_mode': 'form',
                'view_id': view_id.ids,
                'view_type': 'form',
                'res_model': 'account.invoice',
                'type': 'ir.actions.act_window',
                'nodestroy': True,
                'res_id': new_invoice_id.id,
                'target': 'current',
                'context': {'default_type': 'out_invoice'}}

    @api.multi
    def view_invoice(self):
        '''this method is use for the view invoice of penalty'''
        invoice_obj = self.env['account.invoice']
        for rec in self:
            invoices = invoice_obj.search([('book_issue', '=', rec.id)])
            action = self.env.ref('account.action_invoice_tree1').read()[0]
            if len(invoices) > 1:
                action['domain'] = [('id', 'in', invoices.ids)]
            elif len(invoices) == 1:
                action['views'] = [(self.env.ref('account.invoice_form').id,
                                    'form')]
                action['res_id'] = invoices.ids[0]
            else:
                action = {'type': 'ir.actions.act_window_close'}
        return action

    @api.multi
    def _compute_invoices(self):
        inv_obj = self.env['account.invoice']
        for rec in self:
            count_invoice = inv_obj.search_count([('book_issue', '=', rec.id)
                                                  ])
            rec.compute_inv = count_invoice


class LibraryBookRequest(models.Model):
    '''Request for Book'''
    _name = "library.book.request"
    _rec_name = 'req_id'

    @api.multi
    @api.depends('type')
    def _compute_bname(self):
        if self.type:
            if self.type == 'existing':
                book = self.name.name
            else:
                book = self.new_book
            self.bk_nm = book

    req_id = fields.Char('Request ID', readonly=True, default='New')
    card_id = fields.Many2one("library.card", "Card No", required=True)
    type = fields.Selection([('existing', 'HardCopy'), ('ebook', 'E Book')],
                            'Book Type')
    name = fields.Many2one('product.product', 'Book Name')
    new_book = fields.Char('Book Name')
    bk_nm = fields.Char('Name', compute="_compute_bname", store=True)
    state = fields.Selection([('draft', 'Draft'),
                              ('confirm', 'Confirm'),
                              ('cancel', 'Cancelled'),
                              ], "State", default='draft')
    book_return_days = fields.Integer(related='name.day_to_return_book',
                                      string="Return Days")
    ebook_name = fields.Many2one('product.product', 'E book Name')
    active = fields.Boolean(default=True, help='''Set active to false to hide
    the category without removing it.''')

    @api.constrains('card_id', 'name')
    def check_book_request(self):
        book_request = self.search([('card_id', '=', self.card_id.id),
                                    ('name', '=', self.name.id),
                                    ('id', 'not in', self.ids),
                                    ('type', '=', 'existing')])
        if book_request:
            raise ValidationError(_('''You cannot request same book on same
                                    card number more than once at same time!'''
                                    ))

    @api.model
    def create(self, vals):
        res = super(LibraryBookRequest, self).create(vals)
        seq_obj = self.env['ir.sequence']
        res.write({'req_id': (seq_obj.next_by_code('library.book.request'
                                                   ) or 'New')})
        return res

    @api.multi
    def draft_book_request(self):
        self.write({'state': 'draft'})

    @api.multi
    def confirm_book_request(self):
        '''Method to confirm book request'''
        book_issue_obj = self.env['library.book.issue']
        curr_dt = datetime.now()
        new_date = datetime.strftime(curr_dt,
                                     '%m/%d/%Y')
        vals = {}
        if (new_date >= self.card_id.start_date and
                new_date <= self.card_id.end_date):
                raise ValidationError(_('''The Membership of library card is
                over!'''))
        if self.type == 'existing':
            vals.update({'card_id': self.card_id.id,
                         'name': self.name.id})

        elif self.type == 'ebook':
            vals.update({'name': self.ebook_name.id,
                         'card_id': self.card_id.id,
                         'subscription_amt': self.ebook_name.subscrption_amt,
                         })
        issue_id = book_issue_obj.create(vals)
        if self.type == 'ebook':
            if not self.ebook_name.is_subscription:
                issue_id.write({'state': 'paid',
                                'ebook_download': self.ebook_name.attach_ebook
                                })
            else:
                issue_id.write({'state': 'subscribe',
                                'ebook_download': self.ebook_name.attach_ebook
                                })
        else:
            issue_id.write({'state': 'draft'})
        self.write({'state': 'confirm'})
        # changes state to confirm
        if issue_id:
            issue_id.onchange_card_issue()
        return {'name': ('Book Issue'),
                'view_mode': 'form',
                'view_type': 'form',
                'res_id': issue_id.id,
                'res_model': 'library.book.issue',
                'type': 'ir.actions.act_window',
                'target': 'current'}

    @api.multi
    def unlink(self):
        for rec in self:
            if rec.state == 'confirm':
                raise ValidationError(_('''You cannot delete a confirmed
                record of library book request!'''))
        return super(LibraryBookRequest, self).unlink()

    @api.multi
    def cancle_book_request(self):
        self.write({'state': 'cancel'})
