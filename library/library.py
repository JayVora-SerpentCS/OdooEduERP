# -*- encoding: utf-8 -*-
##############################################################################
#
#    OpenERP, Open Source Management Solution
#    Copyright (C) 2004-2009 Tiny SPRL (<http://tiny.be>).
#    Copyright (C) 2011-2012 Serpent Consulting Services (<http://www.serpentcs.com>)
#    Copyright (C) 2013-2014 Serpent Consulting Services (<http://www.serpentcs.com>)
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
import time
from openerp.exceptions import except_orm, Warning, RedirectWarning
from dateutil.relativedelta import relativedelta
from datetime import datetime
# from openerp.tools.translate import _

class library_price_category(models.Model):
    
    _name = 'library.price.category'
    _description = 'Book Price Category'

    name = fields.Char('Category', required=True )
    price = fields.Float('Price', required=True, default=0)
    product_ids = fields.One2many('product.product', 'price_cat', 'Books')

class library_rack(models.Model):
    
    _name = 'library.rack'
    _description = "Library Rack"

    name = fields.Char('Name', required=True, help="it will be show the position of book")
    code = fields.Char('Code')
    active = fields.Boolean('Active', default='True')

class library_collection(models.Model):
    
    _name = 'library.collection'
    _description = "Library Collection"
    
    name = fields.Char('Name', required=True)
    code = fields.Char('Code')

class library_book_returnday(models.Model):
    
    _name = 'library.book.returnday'
    _description = "Library Collection"
    _rec_name = 'day'
    
    day = fields.Integer('Days',required=True, help="It show the no of day/s for returning book")
    code = fields.Char('Code')
    fine_amt = fields.Float('Fine Amount',required=True,help="Fine amount to be paid after due of book return date")

class library_author(models.Model):
    
    _name = 'library.author'
    _description = "Author"
    
    name = fields.Char('Name', required=True, select=True)
    born_date = fields.Date('Date of Birth')
    death_date = fields.Date('Date of Death')
    biography = fields.Text('Biography')
    note = fields.Text('Notes')
    editor_ids = fields.Many2many('res.partner', 'author_editor_rel', 'author_id', 'parent_id', 'Editors', select=1)
    
    _sql_constraints = [('name_uniq', 'unique (name)', 'The name of the author must be unique !')]
    
class library_card(models.Model):
    
    _name = "library.card"
    _description = "Library Card information"
    _rec_name = "code"

    @api.multi
    def on_change_student(self, student_id):
        '''  This method automatically fill up student roll number and standard field  on student_id field
        @param self : Object Pointer
        @param cr : Database Cursor
        @param uid : Current Logged in User
        @param ids : Current Records
        @student : Apply method on this Field name
        @param context : standard Dictionary
        @return : Dictionary having identifier of the record as key and the value of student roll number and standard
        '''
        if not student_id:
            return {'value':{}}
        student_data = self.env['student.student'].browse(student_id)
        val = {
                'standard_id' : student_data.standard_id.id, 
                'roll_no' : student_data.roll_no,
                }
        return {'value': val}
    
    @api.one
    @api.depends('student_id')
    def get_name(self):
        for rec in self:
            if rec.student_id:
                user = rec.student_id.name
            else:
                user = rec.teacher_id.name
            self.gt_name = user
            
    code = fields.Char('Card No', required=True, default=lambda self: self.env['ir.sequence'].get('library.card') or '/')
    book_limit = fields.Integer('No Of Book Limit On Card', required=True) 
    student_id = fields.Many2one('student.student', 'Student Name') 
    standard_id = fields.Many2one('school.standard', 'Standard')
    gt_name = fields.Char(compute="get_name", method=True, string = 'Name')
    user = fields.Selection([('student', 'Student'), ('teacher', 'Teacher')], "User") 
    roll_no = fields.Integer('Roll No')
    teacher_id = fields.Many2one('hr.employee', 'Teacher Name')

class library_book_issue(models.Model):
    
    """Book variant of product"""
    
    _name = "library.book.issue"
    
    _description = "Library information"
    
    _rec_name = "standard_id"

    @api.one
    @api.depends('date_issue','day_to_return_book')
    def _calc_retunr_date(self):
        
        ''' This method calculate a book return date.
        @param self : Object Pointer
        @param cr : Database Cursor
        @param uid : Current Logged in User
        @param ids : Current Records
        @param name : Functional field's name
        @param args : Other arguments
        @param context : standard Dictionary
        @return : Dictionary having identifier of the record as key and the book return date as value 
                
        '''
        if self.date_issue and self.day_to_return_book:
            ret_date = datetime.strptime(self.date_issue, "%Y-%m-%d %H:%M:%S") + relativedelta(days=self.day_to_return_book.day or 0.0)
            self.date_return = ret_date
    
    @api.one
    @api.depends('date_return','day_to_return_book')
    def _calc_penalty(self):
        ''' This method calculate a penalty on book .
        @param self : Object Pointer
        @param cr : Database Cursor
        @param uid : Current Logged in User
        @param ids : Current Records
        @param name : Functional field's name
        @param args : Other arguments
        @param context : standard Dictionary
        @return : Dictionary having identifier of the record as key and penalty as value 
                
        '''
        res= {}
        for line in self:
            if line.date_return:
                start_day = datetime.now()
                end_day  = datetime.strptime(line.date_return, "%Y-%m-%d %H:%M:%S")
                if start_day > end_day:
                    diff = start_day - end_day
                    duration = float(diff.days)* 24 + (float(diff.seconds) / 3600)
                    day = duration/24
                    if line.day_to_return_book:
                        line.penalty = day * line.day_to_return_book.fine_amt

    
    @api.one
    @api.depends('state')
    def _calc_lost_penalty(self):
        ''' This method calculate a penalty on book lost .
        @param self : Object Pointer
        @param cr : Database Cursor
        @param uid : Current Logged in User
        @param ids : Current Records
        @param name : Functional field's name
        @param args : Other arguments
        @param context : standard Dictionary
        @return : Dictionary having identifier of the record as key and book lost penalty as value 
        '''  
              
        res={}
        
#         for line in self:
        if self.state:
            if self.state.title() == 'Lost':
                fine = self.name.list_price
                self.lost_penalty = fine
    
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
#         for issue in self.browse(cr, uid, ids, context = context):
        if self.card_id:
            card_ids = self.search([('card_id', '=', self.card_id.id), ('state', 'in', ['issue', 'reissue'])])
            if self.state == 'issue' or self.state == 'reissue':
                if self.card_id.book_limit > len(card_ids)-1:
                    return True
                else:  
                    raise Warning(_('Book issue limit  is over on this card'))
            else:
                if self.card_id.book_limit > len(card_ids):
                    return True
                else: 
                    raise Warning(_('Book issue limit  is over on this card'))
        
    
    @api.onchange('student_id')
    def onchange_student(self):
        for student_obj in self:
            student_obj.standard_id = student_obj.student_id.standard_id
            student_obj.roll_no = student_obj.student_id.roll_no
    
    name = fields.Many2one('product.product', 'Book Name', required=True) 
    issue_code = fields.Char('Issue No.', required=True, default=lambda self: self.env['ir.sequence'].get('library.book.issue') or '/') 
    student_id = fields.Many2one('student.student', 'Student Name') 
    teacher_id = fields.Many2one('hr.employee', 'Teacher Name') 
    gt_name = fields.Char('Name')
    standard_id = fields.Many2one('standard.standard', 'Standard') 
    roll_no = fields.Integer('Roll No')
    invoice_id = fields.Many2one('account.invoice', "User's Invoice")
    date_issue = fields.Datetime('Issue Date', required=True, help="Release(Issue) date of the book", default=lambda *a: time.strftime('%Y-%m-%d %H:%M:%S'))
    date_return = fields.Datetime(compute="_calc_retunr_date", string ='Return Date', method=True, store=True, help="Book To Be Return On This Date") 
    actual_return_date = fields.Datetime("Actual Return Date", readonly=True, help="Actual Return Date of Book")
    penalty = fields.Float(compute="_calc_penalty", string ='Penalty', method=True, help='It show the late book return penalty')
    lost_penalty = fields.Float(compute="_calc_lost_penalty", string= 'Fine', method=True, store=True, help='It show the penalty for lost book') 
    day_to_return_book = fields.Many2one("library.book.returnday", "Book Return Days") 
    card_id = fields.Many2one("library.card", "Card No", required=True)
    state = fields.Selection([('draft', 'Draft'), ('issue', 'Issued'), ('reissue', 'Reissued'), ('cancel', 'Cancelled'), ('return', 'Returned'), ('lost', 'Lost'), ('fine', 'Fined')], "State", default='draft') 
    user = fields.Char("User")
    color = fields.Integer("Color Index")

    @api.multi
    def on_change_card_issue(self,card_id):
        ''' This method automatically fill up values on card.
            @param self : Object Pointer
            @param cr : Database Cursor
            @param uid : Current Logged in User
            @param ids : Current Records
            @param card : applied change on this field
            @param context : standard Dictionary
            @return : Dictionary having identifier of the record as key and the user info as value 
        '''

        if not card_id:
            return {'value':{}}
        card_data = self.env['library.card'].browse(card_id)
        val = {'user': str(card_data.user.title())}
        if card_data.user.title() == 'Student':
            val.update({
                    'student_id' : card_data.student_id.id, 
                    'standard_id' : card_data.standard_id.id, 
                    'roll_no' : card_data.roll_no, 
                    'gt_name': card_data.gt_name
                })
        else:
            val.update({'teacher_id' : card_data.teacher_id.id, 
                        'gt_name': card_data.gt_name
                })
        return {'value': val}

#methode for the workflow#
    @api.multi
    def draft_book(self):
        ''' This method for books in draft state.
        @param self : Object Pointer
        @param cr : Database Cursor
        @param uid : Current Logged in User
        @param ids : Current Records
        @param context : standard Dictionary
        @return : True 
        '''
        self.write({'state' : 'draft'})
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
#         product_obj = self.env["product.product"]
#         for issue in self.browse(cr, uid, ids, context = context):
        if self.card_id:
            card_ids = self.search([('card_id', '=', self.card_id.id), ('state', 'in', ['issue', 'reissue'])])
            if self.card_id.book_limit > len(card_ids):
                self.write({'state' : 'issue'})
                product_id = self.name
                product_id.write({'availability':'notavailable'})
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
        self.write({'state' : 'reissue'})
        self.write({'date_issue' : time.strftime('%Y-%m-%d %H:%M:%S')})
        return True
    
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
#         product_obj = self.env("product.product")
        vals = {'actual_return_date' : time.strftime('%Y-%m-%d %H:%M:%S'), 'state' : 'return'}
#         for issue in self.browse(cr, uid, ids, context = context):
        self.write(vals)
        product_id = self.name
        product_id.write({'availability':'available'})
        return True

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
        self.write({'state' : 'lost'})
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
        self.write({'state' : 'cancel'})
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
        self.write({'state' : 'fine'})
        invoice_obj = self.env['account.invoice']
        obj_data = self.env['ir.model.data']
        pen=0.0
        lost_pen=0.0
        for record in self:
            if record.user.title() == 'Student':
                usr = record.student_id.partner_id.id
                if not record.student_id.partner_id.contact_address:
                    raise Warning(_("Error ! The Student must have a Home address."))
                addr = record.student_id.partner_id.contact_address
            else:
                usr = record.teacher_id.id
                if not record.teacher_id.address_home_id:
                    raise Warning(_('Error ! The Teacher must have a Home address.'))
                addr = record.teacher_id.address_home_id and record.teacher_id.address_home_id.id 
            vals_invoice = {
                'partner_id': usr, 
                'address_invoice_id' : addr, 
                'account_id': 12, 
            }
            invoice_lines = []
            if record.lost_penalty:
                lost_pen = record.lost_penalty    
                invoice_line2 = {
                    'name' : 'Book Lost Fine', 
                    'price_unit': lost_pen, 
                    'account_id': 12 
                }
                invoice_lines.append((0, 0, invoice_line2))
            if record.penalty:
                pen = record.penalty
                invoice_line1 = {
                    'name' : 'Late Return Penalty', 
                    'price_unit': pen, 
                    'account_id': 12 
                }
                invoice_lines.append((0, 0, invoice_line1))
        vals_invoice.update({'invoice_line':invoice_lines})
        new_invoice_id =  invoice_obj.create(vals_invoice)
        data_id = obj_data._get_id('account', 'invoice_form')
        data = obj_data.browse(data_id)
        view_id = data.res_id
        return {
            'name':_("New Invoice"),
            'view_mode': 'form',
            'view_id': [view_id],
            'view_type': 'form',
            'res_model': 'account.invoice',
            'type': 'ir.actions.act_window',
            'nodestroy': True,
            'res_id' : new_invoice_id.id,
            'target': 'current',
            'context': {
            }
        }
        
class library_book_request(models.Model):
    '''Request for Book'''
    _name = "library.book.request"
    
    _rec_name='req_id'
    
    @api.one
    @api.depends('type')
    def gt_bname(self):
        if self.type:
            if self.type.title() == 'Existing':
                book = self.name.name
            else:
                book = self.new1
            self.bk_nm = book
    
    req_id = fields.Char('Request ID', readonly=True, default=lambda self: self.env['ir.sequence'].get('library.book.request') or '/')
    card_id = fields.Many2one("library.card", "Card No", required=True)
    type = fields.Selection([('existing', 'Existing'), ('new', 'New')], 'Book Type') 
    name = fields.Many2one('product.product', 'Book Name') 
    new1 = fields.Char('Book Name',)
    bk_nm = fields.Char(compute="gt_bname", method=True, string = 'Name', store=True)

# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4:
