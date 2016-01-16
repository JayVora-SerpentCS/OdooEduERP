# -*- coding: utf-8 -*-
# Part of Odoo. See LICENSE file for full copyright and licensing details.

import time
from dateutil.relativedelta import relativedelta
from datetime import datetime
from openerp import models, fields, api, _
from openerp.exceptions import Warning as UserError


class LibraryPriceCategory(models.Model):
    _name = 'library.price.category'
    _description = 'Book Price Category'

    name = fields.Char('Category', required=True)
    price = fields.Float('Price', required=True, default=0)
    product_ids = fields.One2many('product.product', 'price_cat', 'Books')


class LibraryCase(models.Model):
    _name = 'library.case'
    _description = 'Library Case'

    name = fields.Char('Name', required=True,
                       help="Case Name")
    code = fields.Char('Code')
    rack_ids = fields.Many2many('library.case', 'rack_case_rel',
                                'case_id', 'rack_id',
                                'Rack(s)')


class LibraryRack(models.Model):
    _name = 'library.rack'
    _description = "Library Rack"

    name = fields.Char('Name', required=True,
                       help="it will be show the position of book")
    code = fields.Char('Code')
    active = fields.Boolean('Active', default='True')
    case_ids = fields.Many2many('library.case', 'rack_case_rel',
                                'rack_id', 'case_id',
                                'Case(s)')


class LibraryCollection(models.Model):
    _name = 'library.collection'
    _description = "Library Collection"

    name = fields.Char('Name', required=True)
    code = fields.Char('Code')


class LibraryBookReturnday(models.Model):
    _name = 'library.book.returnday'
    _description = "Library Collection"
    _rec_name = 'day'

    day = fields.Integer('Days', required=True,
                         help="It show the no of day/s for returning book")
    fine_amt = fields.Float('Fine Amount', required=True,
                            help="Fine amount after due of book return date")


class LibraryAuthor(models.Model):
    _name = 'library.author'
    _description = "Author"

    name = fields.Char('Name', required=True, select=True)
    born_date = fields.Date('Date of Birth')
    death_date = fields.Date('Date of Death')
    biography = fields.Text('Biography')
    note = fields.Text('Notes')

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
        if self.student_id:
            self.standard_id = self.student_id.standard_id and \
                        self.student_id.standard_id.id,
            self.roll_no = self.student_id.roll_no

    @api.one
    @api.depends('student_id')
    def get_name(self):
        self.gt_name = ''
        if self.user_title == 'student':
            self.gt_name = self.student_id.name
        else:
            self.gt_name = self.teacher_id and self.teacher_id.name

    code = fields.Char('Card No', required=True, default=lambda self:
                       self.env['ir.sequence'].get('library.card') or '/')
    book_limit = fields.Integer('No Of Book Limit On Card', required=True)
    student_id = fields.Many2one('student.student', 'Student Name')
    standard_id = fields.Many2one('school.standard', 'Standard', readonly=True)
    gt_name = fields.Char(compute="get_name", method=True, string='Name')
    user_title = fields.Selection([('student', 'Student'), ('teacher', 'Teacher')],
                            'User')
    roll_no = fields.Integer('Roll No', readonly=True)
    teacher_id = fields.Many2one('hr.employee', 'Teacher Name')


class LibraryBookIssue(models.Model):
    '''Book variant of product'''
    _name = "library.book.issue"
    _description = "Library information"
    _rec_name = "standard_id"

    @api.one
    @api.depends('date_issue', 'day_to_return_book')
    def _calc_retunr_date(self):
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
        if self.date_issue and self.day_to_return_book:
            ret_date = datetime.strptime(self.date_issue, "%Y-%m-%d %H:%M:%S")\
                       + relativedelta(days=self.day_to_return_book.day or 0.0)
            self.date_return = ret_date

    @api.one
    @api.depends('date_return', 'day_to_return_book', 'actual_return_date')
    def _calc_penalty(self):
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
        self.penalty = 0.0
        if self.date_return and self.actual_return_date:
            start_day = datetime.strptime(self.actual_return_date,
                                        "%Y-%m-%d %H:%M:%S")
            end_day = datetime.strptime(self.date_return,
                                        "%Y-%m-%d %H:%M:%S")
            if start_day > end_day:
                diff = start_day - end_day
                if self.day_to_return_book:
                    self.penalty = diff.days * self.day_to_return_book.fine_amt

    @api.one
    @api.depends('state', 'name.list_price')
    def _calc_lost_penalty(self):
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
        self.lost_penalty = 0.0
        if self.state:
            if self.state == 'lost':
                self.lost_penalty = self.name.list_price

    @api.one
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
        if self.card_id:
            card_ids = self.search([('card_id', '=', self.card_id.id),
                                    ('state', 'in', ['issue', 'reissue'])])
            if self.state == 'issue' or self.state == 'reissue':
                if self.card_id.book_limit > len(card_ids) - 1:
                    return True
                else:
                    raise UserError(_('Book issue limit is over on this card'))
            else:
                if self.card_id.book_limit > len(card_ids):
                    return True
                else:
                    raise UserError(_('Book issue limit is over on this card'))

    name = fields.Many2one('product.product', 'Book Name', required=True)
    issue_code = fields.Char('Issue No.', required=True, default=lambda self:
                             self.env['ir.sequence'].get('library.book.issue')\
                             or '/')
    student_id = fields.Many2one(relation='student.student', string='Student Name', related="card_id.student_id")
    teacher_id = fields.Many2one(relation='hr.employee', string='Teacher Name', related="card_id.teacher_id")
    gt_name = fields.Char('Name', related="card_id.gt_name")
    standard_id = fields.Many2one(reation='standard.standard', string='Standard', related="card_id.standard_id")
    roll_no = fields.Integer('Roll No', related="card_id.roll_no")
    invoice_id = fields.Many2one('account.invoice', "User's Invoice")
    date_issue = fields.Datetime('Release Date', required=True,
                                 help="Release(Issue) date of the book",
                                 default=lambda *a:
                                    time.strftime('%Y-%m-%d %H:%M:%S'))
    date_return = fields.Datetime(compute="_calc_retunr_date",
                                  string='Return Date', method=True,
                                  store=True,
                                  help="Book To Be Return On This Date")
    actual_return_date = fields.Datetime("Actual Return Date", readonly=True,
                                         help="Actual Return Date of Book")
    penalty = fields.Float(compute="_calc_penalty",
                           string='Penalty',
                           help='It show the late book return penalty')
    lost_penalty = fields.Float(compute="_calc_lost_penalty", string='Fine',
                                help='It show the penalty for lost book')
    day_to_return_book = fields.Many2one('library.book.returnday',
                                         'Book Return Days')
    card_id = fields.Many2one("library.card", "Card No", required=True)
    state = fields.Selection([('draft', 'Draft'), ('issue', 'Issued'),
                              ('reissue', 'Reissued'), ('cancel', 'Cancelled'),
                              ('return', 'Returned'), ('lost', 'Lost'),
                              ('fine', 'Fined')], "State", default='draft')
    user_title = fields.Selection([('student', 'Student'), ('teacher', 'Teacher')],
                                  'User', related="card_id.user_title")
    color = fields.Integer("Color Index")
    
#    @api.one
#    @api.depends('card_id', 'card_id.user_title')
#    def on_change_card_issue(self):
#        ''' This method automatically fill up values on card.
#            @param self : Object Pointer
#            @param cr : Database Cursor
#            @param uid : Current Logged in User
#            @param ids : Current Records
#            @param card : applied change on this field
#            @param context : standard Dictionary
#            @return : Dictionary having identifier of the record as key
#                      and the user info as value
#        '''
#        if self.card_id and self.card_id.user_title:
#            self.user_title = str(self.card_id.user_title.title())
#            if self.card_id.user_title == 'student':
#                self.student_id = self.card_id.student_id and \
#                                self.card_id.student_id.id
#                self.standard_id =  self.card_id.standard_id and \
#                                self.card_id.standard_id.id
#                self.roll_no = self.card_id.roll_no
#            else:
#                self.teacher_id = self.card_id.teacher_id and \
#                                self.card_id.teacher_id.id

    @api.multi
    def draft_book(self):
#         '''method for WorkFlow'''
#         ''' This method for books in draft state.
#         @param self : Object Pointer
#         @param cr : Database Cursor
#         @param uid : Current Logged in User
#         @param ids : Current Records
#         @param context : standard Dictionary
#         @return : True'''

        self.write({'state': 'draft'})
        return True

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
        ir_model_data = self.env['ir.model.data']
        move_obj = self.env['stock.move']
        picking_obj = self.env['stock.picking']
        src_location_id = ir_model_data.get_object_reference(
                                             'stock', \
                                             'stock_location_stock')[1]
        dest_location_id = ir_model_data.get_object_reference(
                                             'stock', \
                                             'stock_location_customers')[1]
        picking_type_id = ir_model_data.get_object_reference('stock',
                                            'picking_type_out')[1]
        for rec in self:
            partner_id = False
            if rec.user_title == 'student':
                partner_id = rec.student_id and rec.student_id.partner_id
            else:
                partner_id = rec.teacher_id and rec.teacher_id.user_id\
                    and rec.teacher_id.user_id.partner_id\
                            
            picking_data = {
                'partner_id' : partner_id and partner_id.id or False,
                'location_id' : src_location_id,
                'location_dest_id' : dest_location_id,
                'origin' : rec.issue_code,
                'picking_type_id' : picking_type_id
            }
            pick_id = picking_obj.create(picking_data)
            data = {
                'name' : rec.issue_code,
                'date': datetime.today(),
                'product_id': rec.name.id,
                'product_uom': rec.name.uom_id.id,
                'product_uom_qty': 1,
                'location_id': src_location_id,
                'location_dest_id': dest_location_id,
                'procure_method' : 'make_to_order',
                'picking_id' : pick_id.id
            }
            move_obj.create(data)
            pick_id.action_assign()
            pick_id.force_assign()
            pick_id.do_transfer()
        return self.write({'state': 'issue'})

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
        return self.write({'state': 'reissue', 
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
        ir_model_data = self.env['ir.model.data']
        move_obj = self.env['stock.move']
        picking_obj = self.env['stock.picking']
        dest_location_id = ir_model_data.get_object_reference(
                                             'stock', \
                                             'stock_location_stock')[1]
        src_location_id = ir_model_data.get_object_reference(
                                             'stock', \
                                             'stock_location_customers')[1]
        picking_type_id = ir_model_data.get_object_reference('stock',
                                            'picking_type_in')[1]
        for rec in self:
            partner_id = False
            if rec.user_title == 'student':
                partner_id = rec.student_id and rec.student_id.partner_id
            else:
                partner_id = rec.teacher_id and rec.teacher_id.user_id\
                    and rec.teacher_id.user_id.partner_id\
                            
            picking_data = {
                'partner_id' : partner_id and partner_id.id or False,
                'location_id' : src_location_id,
                'location_dest_id' : dest_location_id,
                'origin' : rec.issue_code,
                'picking_type_id' : picking_type_id
            }
            pick_id = picking_obj.create(picking_data)
            data = {
                'name' : rec.issue_code,
                'date': datetime.today(),
                'product_id': rec.name.id,
                'product_uom': rec.name.uom_id.id,
                'product_uom_qty': 1,
                'location_id': src_location_id,
                'location_dest_id': dest_location_id,
                'procure_method' : 'make_to_order',
                'picking_id' : pick_id.id
            }
            move_obj.create(data)
            pick_id.action_assign()
            pick_id.force_assign()
            pick_id.do_transfer()
        return self.write({'actual_return_date': \
                           time.strftime('%Y-%m-%d %H:%M:%S'),
                           'state': 'return'})

    @api.multi
    def lost_book(self):
        '''
        This method used when book lost and change lost state.
        @param self : Object Pointer
        @param cr : Database Cursor
        @param uid : Current Logged in User
        @param ids : Current Records
        @param context : standard Dictionary
        @return : True
        '''
        ir_model_data = self.env['ir.model.data']
        move_obj = self.env['stock.move']
        picking_obj = self.env['stock.picking']
        src_location_id = ir_model_data.get_object_reference(
                                             'stock', \
                                             'stock_location_stock')[1]
        dest_location_id = ir_model_data.get_object_reference(
                                             'stock', \
                                             'location_inventory')[1]
        picking_type_id = ir_model_data.get_object_reference('stock',
                                            'picking_type_out')[1]
        for rec in self:
            partner_id = False
            if rec.user_title == 'student':
                partner_id = rec.student_id and rec.student_id.partner_id
            else:
                partner_id = rec.teacher_id and rec.teacher_id.user_id\
                    and rec.teacher_id.user_id.partner_id\
                            
            picking_data = {
                'partner_id' : partner_id and partner_id.id or False,
                'location_id' : src_location_id,
                'location_dest_id' : dest_location_id,
                'origin' : rec.issue_code,
                'picking_type_id' : picking_type_id
            }
            pick_id = picking_obj.create(picking_data)
            data = {
                'name' : rec.issue_code,
                'date': datetime.today(),
                'product_id': rec.name.id,
                'product_uom': rec.name.uom_id.id,
                'product_uom_qty': 1,
                'location_id': src_location_id,
                'location_dest_id': dest_location_id,
                'procure_method' : 'make_to_order',
                'picking_id' : pick_id.id
            }
            move_obj.create(data)
            pick_id.action_assign()
            pick_id.force_assign()
            pick_id.do_transfer()
        return self.write({'state': 'lost'})

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
        return True

    @api.multi
    def user_fine(self):
        '''
        This method used when penalty on book either late return or book lost.
        @param self : Object Pointer
        @param cr : Database Cursor
        @param uid : Current Logged in User
        @param ids : Current Records
        @param context : standard Dictionary
        @return : new form of account.invoice
        '''
        invoice_obj = self.env['account.invoice']
        obj_data = self.env['ir.model.data']
        pen = 0.0
        lost_pen = 0.0
        for record in self:
            if record.user_title == 'student':
                usr = record.student_id.partner_id.id
                if not record.student_id.partner_id.contact_address:
                    raise UserError(_('Error !'
                                    'The Student must have a Home address.'))
                addr = record.student_id.partner_id.contact_address
            else:
                usr = record.teacher_id and record.teacher_id.user_id\
                    and record.teacher_id.user_id.partner_id\
                    and record.teacher_id.user_id.partner_id.id
                if not record.teacher_id.address_home_id:
                    raise UserError(_('Error !'
                                    'The Teacher must have a Home address.'))
                if not usr:
                    raise UserError(_('Error !'
                                    'Provide related user in Teacher.'))
                addr = record.teacher_id.address_home_id\
                        and record.teacher_id.address_home_id.id
            vals_invoice = {'partner_id': usr,
                            'address_invoice_id': addr,
                            'account_id': 12}
            invoice_lines = []
            if record.lost_penalty:
                lost_pen = record.lost_penalty
                invoice_line2 = {'name': 'Book Lost Fine',
                                 'price_unit': lost_pen,
                                 'account_id': 12}
                invoice_lines.append((0, 0, invoice_line2))
            if record.penalty:
                pen = record.penalty
                invoice_line1 = {'name': 'Late Return Penalty',
                                 'price_unit': pen,
                                 'account_id': 12}
                invoice_lines.append((0, 0, invoice_line1))
        vals_invoice.update({'invoice_line_ids': invoice_lines})
        new_invoice_id = invoice_obj.create(vals_invoice)
        self.write({'state': 'fine'})
        data_id = obj_data._get_id('account', 'invoice_form')
        data = obj_data.browse(data_id)
        view_id = data.res_id
        return {'name': _("New Invoice"),
                'view_mode': 'form',
                'view_id': [view_id],
                'view_type': 'form',
                'res_model': 'account.invoice',
                'type': 'ir.actions.act_window',
                'nodestroy': True,
                'res_id': new_invoice_id.id,
                'target': 'current',
                'context': {}}


class LibraryBookRequest(models.Model):
    '''Request for Book'''
    _name = "library.book.request"
    _rec_name = 'req_id'

    @api.one
    @api.depends('type', 'name.name', 'new1')
    def gt_bname(self):
        if self.type:
            if self.type == 'existing':
                book = self.name.name
            else:
                book = self.new1
            self.bk_nm = book

    req_id = fields.Char('Request ID', readonly=True, default=lambda self:
                         self.env['ir.sequence'].get('library.book.request')
                         or '/')
    card_id = fields.Many2one("library.card", "Card No", required=True)
    type = fields.Selection([('existing', 'Existing'), ('new', 'New')],
                            'Book Type')
    name = fields.Many2one('product.product', 'Book Name')
    new1 = fields.Char('Book Name')
    bk_nm = fields.Char('Name', compute="gt_bname", method=True, store=True)
