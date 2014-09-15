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
from openerp.osv import osv, fields
import time
from dateutil.relativedelta import relativedelta
from datetime import datetime
from openerp.tools.translate import _

class library_price_category(osv.Model):
    
    _name = 'library.price.category'
    _description = 'Book Price Category'

    _columns = {
        'name': fields.char('Category', size=64, required=True ),
        'price': fields.float('Price', required=True),
        'product_ids': fields.one2many('product.product', 'price_cat', 'Books')
    }

    _defaults = {
        'price': lambda *a: 0,
    }

class library_rack(osv.Model):
    
    _name = 'library.rack'
    _description = "Library Rack"

    _columns = {
        'name': fields.char('Name', size=64, required=True, help="it will be show the position of book"),
        'code': fields.char('Code', size=16),
        'active': fields.boolean('Active'),
    }
    _defaults = {
        'active': lambda *a: True
    }

class library_collection(osv.Model):
    
    _name = 'library.collection'
    _description = "Library Collection"
    _columns = {
        'name': fields.char('Name', size=64, required=True),
        'code': fields.char('Code', size=16),
    }

class library_book_returnday(osv.Model):
    
    _name = 'library.book.returnday'
    _description = "Library Collection"
    _rec_name = 'day'
    _columns = {
        'day': fields.integer('Days',required=True, help="It show the no of day/s for returning book"),
        'code': fields.char('Code', size=16),
        'fine_amt' : fields.float('Fine Amount',required=True,help="Fine amount to be paid after due of book return date"),
    }

class library_author(osv.Model):
    
    _name = 'library.author'
    _description = "Author"
    _columns = {
        'name': fields.char('Name', size=30, required=True, select=True),
        'born_date': fields.date('Date of Birth'),
        'death_date': fields.date('Date of Death'),
        'biography': fields.text('Biography'),
        'note': fields.text('Notes'),
        'editor_ids': fields.many2many('res.partner', 'author_editor_rel', 'author_id', 'parent_id', 'Editors', select=1),
    }
    
    _sql_constraints = [
                        ('name_uniq', 'unique (name)', 'The name of the author must be unique !')
        ]

class library_card(osv.Model):
    
    _name = "library.card"
    _description = "Library Card information"
    _rec_name = "code"

    def on_change_student(self, cr, uid, ids, student, context=None):
        '''  This method automatically fill up student roll number and standard field  on student_id field
        @param self : Object Pointer
        @param cr : Database Cursor
        @param uid : Current Logged in User
        @param ids : Current Records
        @student : Apply method on this Field name
        @param context : standard Dictionary
        @return : Dictionary having identifier of the record as key and the value of student roll number and standard
        '''
        if not student:
            return {'value':{}}
        student_data = self.pool.get('student.student').browse(cr, uid, student, context=context)
        val = {
                'standard_id' : student_data.standard_id.id, 
                'roll_no' : student_data.roll_no,
                }
        return {'value': val}
    
    def get_name(self, cr, uid, ids, name, args, context=None):
        user_dict = {}
        recs = self.browse(cr, uid, ids)
        for rec in recs:
            if rec.student_id:
                user = rec.student_id.name
            else:
                user = rec.teacher_id.name
            user_dict[rec.id] = user
        return user_dict
       
    _columns = {
        'code': fields.char('Card No', size=64, required=True), 
        'book_limit': fields.integer('No Of Book Limit On Card', required=True), 
        'student_id': fields.many2one('student.student', 'Student Name'), 
        'standard_id': fields.many2one('school.standard', 'Standard'), 
        'gt_name':fields.function(get_name, type='char', method=True, string = 'Name'), 
        'user': fields.selection([('student', 'Student'), ('teacher', 'Teacher')], "User"), 
        'roll_no': fields.integer('Roll No'), 
        'teacher_id': fields.many2one('hr.employee', 'Teacher Name')
    }
    _defaults = {
        'code' : lambda self, cr, uid, context: self.pool.get('ir.sequence').get(cr, uid, 'library.card') or '/'
                 
    }

class library_book_issue(osv.Model):
    
    """Book variant of product"""
    
    _name = "library.book.issue"
    
    _description = "Library information"
    
    _rec_name = "standard_id"

    def _calc_retunr_date(self, cr, uid, ids, name, arg, context=None):
        
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
        res = {}
        for line in self.browse(cr, uid, ids, context=context):
            ret_date = datetime.strptime(line.date_issue, "%Y-%m-%d %H:%M:%S") + relativedelta(days=line.day_to_return_book.day or 0.0)
            res[line.id] = ret_date
        return res
    
    def _calc_penalty(self, cr, uid, ids, name, arg, context=None):
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
        for line in self.browse(cr, uid, ids, context=context):
            res[line.id] = 0.0
            if line.date_return:
                start_day = datetime.now()
                end_day  = datetime.strptime(line.date_return, "%Y-%m-%d %H:%M:%S")
                if start_day > end_day:
                    diff = start_day - end_day
                    duration = float(diff.days)* 24 + (float(diff.seconds) / 3600)
                    day = duration/24
                    if line.day_to_return_book:
                        res[line.id] = day * line.day_to_return_book.fine_amt
        return res
    
    def _calc_lost_penalty(self, cr, uid, ids, name, arg, context=None):
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
        
        for line in self.browse(cr, uid, ids, context=context):
            if line.state.title() == 'Lost':
                fine = line.name.list_price
                res[line.id] = fine
        return res
                
    def _check_issue_book_limit(self, cr, uid, ids, context=None):
        ''' This method used how many book can issue as per user type  .
        @param self : Object Pointer
        @param cr : Database Cursor
        @param uid : Current Logged in User
        @param ids : Current Records
        @param context : standard Dictionary
        @return : True or False
                
        '''
        for issue in self.browse(cr, uid, ids, context = context):
            card_ids = self.search(cr, uid, [('card_id', '=', issue.card_id.id), ('state', 'in', ['issue', 'reissue'])], context=context)
            if issue.state == 'issue' or issue.state == 'reissue':
                if issue.card_id.book_limit > len(card_ids)-1:
                    return True
                else: 
                    return False 
            else:
                if issue.card_id.book_limit > len(card_ids):
                    return True
                else: 
                    return False
                
    _columns = {
        'name': fields.many2one('product.product', 'Book Name', required=True), 
        'issue_code' : fields.char('Issue No.', size=24, required=True), 
        'student_id': fields.many2one('student.student', 'Student Name'), 
        'teacher_id': fields.many2one('hr.employee', 'Teacher Name'), 
        'gt_name' : fields.char('Name', size=64),
        'standard_id': fields.many2one('standard.standard', 'Standard'), 
        'roll_no': fields.integer('Roll No'), 
        'invoice_id': fields.many2one('account.invoice', "User's Invoice"), 
        'date_issue': fields.datetime('Release Date', required=True, help="Release(Issue) date of the book"), 
        'date_return': fields.function(_calc_retunr_date, string ='Return Date', method=True, type='datetime', store=True, help="Book To Be Return On This Date"), 
        'actual_return_date': fields.datetime("Actual Return Date", readonly=True, help="Actual Return Date of Book"), 
        'penalty': fields.function(_calc_penalty, string ='Penalty', method=True, type='float',help='It show the late book return penalty'), 
        'lost_penalty': fields.function(_calc_lost_penalty, string= 'Fine', method=True, type='float', store=True, help='It show the penalty for lost book'), 
        'day_to_return_book': fields.many2one("library.book.returnday", "Book Return Days"), 
        'card_id': fields.many2one("library.card", "Card No", required=True), 
        'state': fields.selection([('draft', 'Draft'), ('issue', 'Issued'), ('reissue', 'Reissued'), ('cancel', 'Cancelled'), ('return', 'Returned'), ('lost', 'Lost'), ('fine', 'Fined')], "State"), 
        'user': fields.char("User", size=30), 
        'color': fields.integer("Color Index")
    }
    
    _constraints = [(_check_issue_book_limit, _('Book issue limit  is over on this card'), ['issue_code'])]
    

    _defaults = {
        'date_issue': lambda *a: time.strftime('%Y-%m-%d %H:%M:%S'), 
        'state': 'draft', 
        'issue_code' : lambda self, cr, uid, context: self.pool.get('ir.sequence').get(cr, uid, 'library.book.issue') or '/', 
    }
    def on_change_card_issue(self, cr, uid, ids, card, context=None):
        ''' This method automatically fill up values on card.
            @param self : Object Pointer
            @param cr : Database Cursor
            @param uid : Current Logged in User
            @param ids : Current Records
            @param card : applied change on this field
            @param context : standard Dictionary
            @return : Dictionary having identifier of the record as key and the user info as value 
        '''
        
        if context is None:
            context = {}
        if not card:
            return {'value':{}}
        card_data = self.pool.get('library.card').browse(cr, uid, card, context=context)
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

    def draft_book(self, cr, uid, ids, context=None):
        ''' This method for books in draft state.
        @param self : Object Pointer
        @param cr : Database Cursor
        @param uid : Current Logged in User
        @param ids : Current Records
        @param context : standard Dictionary
        @return : True 
        '''
        self.write(cr, uid, ids, {'state' : 'draft'}, context=context)
        return True

    def issue_book(self, cr, uid, ids, context=None):
        '''
        This method used for issue a books.
        @param self : Object Pointer
        @param cr : Database Cursor
        @param uid : Current Logged in User
        @param ids : Current Records
        @param context : standard Dictionary
        @return : True 
        '''
        product_obj = self.pool.get("product.product")
        for issue in self.browse(cr, uid, ids, context = context):
            card_ids = self.search(cr, uid, [('card_id', '=', issue.card_id.id), ('state', 'in', ['issue', 'reissue'])])
            if issue.card_id.book_limit > len(card_ids):
                self.write(cr, uid, ids, {'state' : 'issue'}, context=context)
                product_obj.write(cr, uid, issue.name.id, {'availability':'notavailable'}, context=context)
        return True
    
    def reissue_book(self,cr,uid,ids,context=None):
        '''
        This method used for reissue a books.
        @param self : Object Pointer
        @param cr : Database Cursor
        @param uid : Current Logged in User
        @param ids : Current Records
        @param context : standard Dictionary
        @return : True 
        '''
        self.write(cr, uid, ids, {'state' : 'reissue'}, context=context)
        self.write(cr, uid, ids, {'date_issue' : time.strftime('%Y-%m-%d %H:%M:%S')}, context=context)
        return True
    
    def return_book(self, cr, uid, ids, context=None):
        '''
        This method used for return a books.
        @param self : Object Pointer
        @param cr : Database Cursor
        @param uid : Current Logged in User
        @param ids : Current Records
        @param context : standard Dictionary
        @return : True 
        '''
        product_obj = self.pool.get("product.product")
        vals = {'actual_return_date' : time.strftime('%Y-%m-%d %H:%M:%S'), 'state' : 'return'}
        for issue in self.browse(cr, uid, ids, context = context):
            self.write(cr, uid, ids, vals, context=context)
            product_obj.write(cr, uid, issue.name.id, {'availability':'available'}, context=context)
        return True

    def lost_book(self, cr, uid, ids, context=None):
        '''
        This method used when book lost and change lost state.
        @param self : Object Pointer
        @param cr : Database Cursor
        @param uid : Current Logged in User
        @param ids : Current Records
        @param context : standard Dictionary
        @return : True 
        '''
        self.write(cr, uid, ids, {'state' : 'lost'}, context=context)
        return True
    
    def cancel_book(self, cr, uid, ids, context=None):
        '''
        This method used for cancel book issue.
        @param self : Object Pointer
        @param cr : Database Cursor
        @param uid : Current Logged in User
        @param ids : Current Records
        @param context : standard Dictionary
        @return : True 
        '''
        self.write(cr, uid, ids, {'state' : 'cancel'}, context=context)
        return True
    
    def user_fine(self, cr, uid, ids, context=None):
        '''
        This method used when penalty on book either late return or book lost.
        @param self : Object Pointer
        @param cr : Database Cursor
        @param uid : Current Logged in User
        @param ids : Current Records
        @param context : standard Dictionary
        @return : new form of account.invoice
        '''
        self.write(cr, uid, ids, {'state' : 'fine'}, context=context)
        invoice_obj = self.pool.get('account.invoice')
        obj_data = self.pool.get('ir.model.data')
        pen=0.0
        lost_pen=0.0
        for record in self.browse(cr, uid, ids):
            if record.user.title() == 'Student':
                usr = record.student_id.partner_id.id
                if not record.student_id.partner_id.contact_address:
                    raise osv.except_osv(_('Error !'), _('The Student must have a Home address.'))
                addr = record.student_id.partner_id.contact_address
            else:
                usr = record.teacher_id.id
                if not record.teacher_id.address_home_id:
                    raise osv.except_osv(_('Error !'), _('The Teacher must have a Home address.'))
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
        new_invoice_id =  invoice_obj.create(cr, uid, vals_invoice)
        
        data_id = obj_data._get_id(cr, uid, 'account', 'invoice_form')
        data = obj_data.browse(cr, uid, data_id, context=context)
        view_id = data.res_id
        return {
        'name':_("New Invoice"),
            'view_mode': 'form',
            'view_id': [view_id],
            'view_type': 'form',
            'res_model': 'account.invoice',
            'type': 'ir.actions.act_window',
            'nodestroy': True,
            'res_id' : new_invoice_id,
            'target': 'current',
            'context': {
            }
        }

class library_book_request(osv.Model):
    '''Request for Book'''
    _name = "library.book.request"
    
    _rec_name='req_id'
    
    def gt_bname(self, cr, uid, ids, name, args, context=None):
        book_dict = {}
        recs = self.browse(cr, uid, ids)
        for rec in recs:
            if rec.type.title() == 'Existing':
                book = rec.name.name
            else:
                book = rec.new1
            book_dict[rec.id] = book
        return book_dict
    
    _columns = {
        'req_id' : fields.char('Request ID', size=24, readonly=True), 
        'card_id': fields.many2one("library.card", "Card No", required=True), 
        'type' : fields.selection([('existing', 'Existing'), ('new', 'New')], 'Book Type'), 
        'name' : fields.many2one('product.product', 'Book Name'), 
        'new1' : fields.char('Book Name', size=32), 
        'bk_nm' : fields.function(gt_bname, type='char', method=True, string = 'Name', store=True)
    }
    
    _defaults = {
        'req_id' : lambda self, cr, uid, context: self.pool.get('ir.sequence').get(cr, uid, 'library.book.request') or '/'         
        
    }

# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4: