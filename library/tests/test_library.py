# See LICENSE file for full copyright and licensing details.

from odoo.tests import common
import time
from datetime import datetime
from dateutil.relativedelta import relativedelta as rd


class TestLibrary(common.TransactionCase):

    def setUp(self):
        super(TestLibrary, self).setUp()
        self.product_product_obj = self.env['product.product']
        self.library_rack_obj = self.env['library.rack']
        self.product_lang_obj = self.env['product.lang']
        self.library_author_obj = self.env['library.author']
        self.book_editor_obj = self.env['book.editor']
        self.library_card_obj = self.env['library.card']
        self.purchase_order_obj = self.env['purchase.order']
        self.purchase_order_line_obj = self.env['purchase.order.line']
        self.library_book_request_obj = self.env['library.book.request']
        self.library_book_issue_obj = self.env['library.book.issue']
        self.stock_picking_obj = self.env['stock.picking']
        self.immideate_transfer = self.env['stock.immediate.transfer']
        self.student_id = self.env.ref('school.demo_student_student_9')
        self.school_standard = self.env.ref('school.demo_school_standard_3')
        self.standard = self.env.ref('school.demo_standard_standard_3')
        self.product = self.env.ref('library.library_product_b2')
        self.res_partner = self.env.ref('base.res_partner_1')
        self.category = self.env.ref('product.product_category_1')
        self.company_id = self.env.ref('school.demo_school_1')
        self.product_book = self.env.ref('library.product_product_b1')
        self.prd_uom = self.env.ref('product.product_uom_unit')
        currdt = datetime.now()
        return_date = currdt + rd(days=4)
        ret_date = datetime.strftime(return_date, '%Y-%m-%d %H:%M:%S')
        curent_date = datetime.strftime(currdt, '%Y-%m-%d %H:%M:%S')
        st_date = currdt - rd(months=4)
        start_dt = datetime.strftime(st_date, '%m/%d/%Y')
        end_dt = currdt + rd(months=14)
        end_date = datetime.strftime(end_dt, '%m/%d/%Y')
        # Create library rack
        self.library_rack = self.library_rack_obj.\
            create({'name': 'Rack34',
                    'code': 'rack34',
                    'active': True
                    })
        # Create product language
        self.product_lang = self.product_lang_obj.\
            create({'code': 'LG4',
                    'name': 'Hindi',
                    })
        # Create library author
        self.library_author = self.library_author_obj.\
            create({'name': 'NCERT'
                    })
        # Create product
        categ = self.env['product.category'].search([('name', '=', 'Books')])
        self.product_product2 = self.product_product_obj.\
            create({'name': 'Java',
                    'categ_id': categ.id,
                    'type': 'product',
                    'day_to_return_book': 3,
                    'weight': 1.23,
                    'fine_lost': 100,
                    'fine_late_return': 100,
                    'nbpage': 344,
                    'availability': 'notavailable',
                    'num_edition': 3
                    })
        # Create editior
        self.book_editor = self.book_editor_obj.\
            create({'name': 'S.S Prasad',
                    'book_id': self.product_product2.id
                    })
        # Create library card
        self.library_card2 = self.library_card_obj.\
            create({'code': 'c4579877687',
                    'user': 'student',
                    'book_limit': 20,
                    'student_id': self.student_id.id,
                    'roll_no': 7,
                    'standard_id': self.school_standard.id,
                    'start_date': start_dt,
                    'end_date': end_date,
                    })
        self.library_card2._compute_name()
        self.library_card2.running_state()
        # Create purchase order
        self.purchase_order = self.purchase_order_obj.\
            create({'partner_id': self.res_partner.id,
                    'date_order': curent_date,
                    'date_planned': curent_date,
                    })
        # Create purchase order line
        self.purchase_order_line = self.purchase_order_line_obj.\
            create({'product_id': self.product_product2.id,
                    'name': 'Java',
                    'date_planned': curent_date,
                    'company_id': self.company_id.id,
                    'product_qty': 100.0,
                    'price_unit': 2500,
                    'product_uom': self.prd_uom.id,
                    'order_id': self.purchase_order.id
                    })
        self.purchase_order.button_confirm()
        self.purchase_order.action_view_picking()
        self.purchase_order_line.onchange_product_id()
        self.stock_picking = self.stock_picking_obj.\
            search([('origin', '=', self.purchase_order.name)])
        self.stock_picking.do_new_transfer()
        self.imm = self.immideate_transfer.\
            create({'pick_id': self.stock_picking.id})
        for rec in self.imm:
            rec.process()
        # Book request created
        self.library_book_request = self.library_book_request_obj.\
            create({'req_id': 'New',
                    'type': 'existing',
                    'card_id': self.library_card2.id,
                    'name': self.product_product2.id,
                    'book_return_days': 3
                    })
        self.library_book_request._compute_bname()
        self.library_book_request.draft_book_request()
        self.library_book_request.confirm_book_request()
        self.library_book_request.cancle_book_request()

        self.library_book_issue2 = self.library_book_issue_obj.\
            create({'issue_code': 'L0976789878',
                    'name': self.product_product2.id,
                    'card_id': self.library_card2.id,
                    'user': 'Student',
                    'state': 'draft',
                    'student_id': self.student_id.id,
                    'standard_id': self.standard.id,
                    'roll_no': 7,
                    'actual_return_date': ret_date,
                    })
        self.library_book_issue2.onchange_day_to_return_book()
        self.library_book_issue2._compute_return_date()
        self.library_book_issue2._compute_penalty()
        self.library_book_issue2._compute_lost_penalty()
        self.library_book_issue2._check_issue_book_limit()
        self.library_book_issue2.onchange_card_issue()
        self.library_book_issue2.issue_book()
        self.library_book_issue2.reissue_book()
        self.library_book_issue2.return_book()
        self.library_book_issue2.cancel_book()

    def test_exam(self):
        self.assertEqual(self.library_card2.student_id.state, 'done')
        self.assertEqual(self.library_book_issue2.student_id.state, 'done')
