import time
import base64
from datetime import date, datetime
from odoo import models, fields, api, tools, _
from odoo.modules import get_module_resource
from odoo.exceptions import except_orm
from odoo.exceptions import ValidationError
from odoo.tools import DEFAULT_SERVER_DATE_FORMAT

class StudentStudent(models.Model):
    ''' Defining a student information '''
    _name = 'student.student'
    _inherit = "student.student"
    
    #fees_structure = fields.Many2one('student.fees.structure','Fees Structure')
    product_list_id = fields.Many2one('product.pricelist', string='Product List')

class StudentPromotion(models.Model):
    _name = "student.promotion"
    _inherit = "student.promotion"
    _description = "Student Promotion"
    
    fees_structure = fields.Many2one('student.fees.structure','Fees Structure', required=True)
    product_list_id = fields.Many2one('product.pricelist', string='Default Price List')
    journal_id = fields.Many2one('account.journal', 'Journal', help="Select Journal", required=True)
    
class StudentPromotionLine(models.Model):
    _name = "student.promotion.line"
    _inherit = "student.promotion.line"
    _description = "Student Promotion Line"
    
    #fees_structure = fields.Many2one('student.fees.structure','Fees Structure')
    #fees_structure_new = fields.Many2one('student.fees.structure','Fees Structure New')
    product_list_id = fields.Many2one('product.pricelist', string='Product List', readonly=True)
    product_list_id_new = fields.Many2one('product.pricelist', string='Product List New')
    