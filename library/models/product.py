# See LICENSE file for full copyright and licensing details.

from odoo import _, api, fields, models
from odoo.exceptions import ValidationError


class ProductTemplate(models.Model):
    _inherit = "product.template"

    name = fields.Char("Name", required=True, help="Book Name")


class ProductCategory(models.Model):
    _inherit = "product.category"

    book_categ = fields.Boolean("Book Category", default=False,
        help="Book category")


class ProductLang(models.Model):
    """Book language"""

    _name = "product.lang"
    _description = "Book's Language"

    code = fields.Char("Code", required=True, help="Book code")
    name = fields.Char("Name", required=True, translate=True, help="Book name")

    _sql_constraints = [
        ("name_uniq", "unique(name)",
        "The name of the language must be unique !")]

    @api.constrains("code")
    def _check_code(self):
        for rec in self:
            if self.search([('id', '!=', rec.id),
                            ('code', '=', rec.code)]):
                raise ValidationError(_('The code of the language must be unique !'))


class ProductProduct(models.Model):
    """Book variant of product"""

    _inherit = "product.product"

    @api.model
    def default_get(self, fields):
        """Overide method to get default category books"""
        res = super(ProductProduct, self).default_get(fields)
        category = self.env["product.category"].search(
            [("name", "=", "Books")], limit=1)
        res.update({"categ_id": category.id})
        return res

    def _default_categ(self):
        """ This method put default category of product"""

        if self._context is None:
            self._context = {}
        if self._context.get("category_id", False):
            return self._context["category_id"]
        res = False
        try:
            res = self.env.ref("library.product_category_1").id
        except ValueError:
            res = False
        return res

    def _get_partner_code_name(self, product, parent_id):
        """ This method get the partner code name"""
        for supinfo in product.seller_ids:
            if supinfo.name.id == parent_id:
                return {
                    "code": supinfo.product_code or product.default_code,
                    "name": supinfo.product_name or product.name,
                }
        res = {"code": product.default_code, "name": product.name}
        return res

    def _product_code(self):
        """ This method get the product code"""
        res = {}
        parent_id = self._context.get("parent_id", None)
        for product in self:
            res[product.id] = self._get_partner_code_name(product, parent_id
                )["code"]
        return res

    @api.model
    def create(self, vals):
        """ This method is Create new student"""
        # add link from editor to supplier:
        if "editor" in vals:
            for supp in self.env["library.editor.supplier"].search(("name",
                                                    "=", vals.get("editor"))):
                supplier = [0, 0, {"pricelist_ids": [],
                                   "name": supp.supplier_id.id,
                                   "sequence": supp.sequence,
                                   "qty": 0,
                                   "delay": 1,
                                   "product_code": False,
                                   "product_name": False}]
                if "seller_ids" not in vals:
                    vals["seller_ids"] = [supplier]
                else:
                    vals["seller_ids"].append(supplier)
        return super(ProductProduct, self).create(vals)

    @api.depends("qty_available")
    def _compute_books_available(self):
        """Computes the available books"""
        book_issue_obj = self.env["library.book.issue"]
        for rec in self:
            issue_rec_no = book_issue_obj.sudo().search_count(
                [("name", "=", rec.id), ("state", "in", ("issue", "reissue"))]
            )
            # reduces the quantity when book is issued
            rec.books_available = rec.qty_available - issue_rec_no
        return True

    @api.depends("books_available", 'day_to_return_book')
    def _compute_books_availablity(self):
        """Method to compute availability of book"""
        for rec in self:
            rec.availability = "notavailable"
            if rec.books_available >= 1:
                rec.availability = "available"       

    isbn = fields.Char("ISBN Code", unique=True,
        help="Shows International Standard Book Number")
    catalog_num = fields.Char("Catalog number",
        help="Shows Identification number of books")
    lang = fields.Many2one("product.lang", "Language", help="Book language")
    editor_ids = fields.One2many("book.editor", "book_id", "Editor",
        help="Book editor")
    author = fields.Many2one("library.author", "Author",
        help="Library author")
    code = fields.Char(compute_="_product_code", string="Acronym",
        store=True, help="Book code")
    catalog_num = fields.Char("Catalog number",
        help="Reference number of book")
    creation_date = fields.Datetime("Creation date",
        readonly=True, help="Record creation date",
        default=lambda self: fields.Datetime.today())
    date_retour = fields.Datetime("Return Date", help="Book Return date")
    fine_lost = fields.Float("Fine Lost", help="Enter fine lost")
    fine_late_return = fields.Float("Late Return", help="Enter late return")
    tome = fields.Char("TOME",
        help="Stores information of work in several volume")
    nbpage = fields.Integer("Number of pages", help="Enter number of pages")
    rack = fields.Many2one("library.rack", "Rack",
        help="Shows position of book")
    books_available = fields.Float("Books Available",
        compute="_compute_books_available", help="Available books")
    availability = fields.Selection([("available", "Available"),
        ("notavailable", "Not Available")], "Book Availability",
        default="available", compute="_compute_books_availablity",
        help="Book availability", store=True)
    back = fields.Selection([("hard", "HardBack"), ("paper", "PaperBack")],
        "Binding Type", help="Shows books-binding type", default="paper")
    pocket = fields.Char("Pocket", help="Pocket")
    num_pocket = fields.Char("Collection No.",
        help="Shows collection number in which" "book resides")
    num_edition = fields.Integer("No. edition", help="Edition number of book")
    format = fields.Char("Format",
        help="The general physical appearance of a book")
    #    price_cat = fields.Many2one('library.price.category', "Price category")
    is_ebook = fields.Boolean("Is EBook",
        help="Activate/Deactivate as per the book is ebook or not")
    is_subscription = fields.Boolean("Is Subscription based",
        help="Activate/deactivate as per subscription")
    subscrption_amt = fields.Float("Subscription Amount",
        help="Subscription amount")
    attach_ebook = fields.Binary("Attach EBook", help="Attach book here")
    day_to_return_book = fields.Integer("Book Return Days",
        help="Enter book return days")
    attchment_ids = fields.One2many("book.attachment", "product_id",
        "Book Attachments", help="Book attachments")

    _sql_constraints = [("unique_barcode_code", "unique(barcode,code)",
                 "Barcode and Code must be unique across all the products!")]

    @api.onchange("is_ebook", "attach_ebook")
    def onchange_availablilty(self):
        """Onchange method to define book availability"""
        if self.is_ebook and self.attach_ebook:
            self.availability = "available"

    def action_purchase_order(self):
        """Method to redirect at book order"""
        purchase_line_obj = self.env["purchase.order.line"]
        purchase = purchase_line_obj.search([("product_id", "=", self.id)])
        action = self.env.ref("purchase.purchase_form_action")
        result = action.read()[0]
        if not purchase:
            raise ValidationError(_("There is no Books Purchase !"))
        order = []
        [order.append(order_rec.order_id.id) for order_rec in purchase]
        if len(order) != 1:
            result["domain"] = "[('id', 'in', " + str(order) + ")]"
        else:
            res = self.env.ref("purchase.purchase_order_form", False)
            result["views"] = [(res and res.id or False, "form")]
            result["res_id"] = purchase.order_id.id
        return result

    def action_book_req(self):
        """Method to request book"""
        book_req_obj = self.env["library.book.request"]
        for rec in self:
            book_req = book_req_obj.search([("name", "=", rec.id)])
            if not book_req:
                raise ValidationError(_("There is no Book requested"))
            action = self.env.ref("library.action_lib_book_req")
            result = action.read()[0]
            req = [request_rec.id for request_rec in book_req]
            if len(req) != 1:
                result["domain"] = "[('id', 'in', " + str(req) + ")]"
            else:
                res = self.env.ref("library.view_book_library_req_form", False)
                result["views"] = [(res and res.id or False, "form")]
                result["res_id"] = book_req.id
            return result


class BookAttachment(models.Model):
    """Defining Book Attachment."""

    _name = "book.attachment"
    _description = "Stores attachments of the book"

    name = fields.Char("Description", required=True, help="Enter Description")
    product_id = fields.Many2one("product.product", "Product",
        help="Select Book")
    date = fields.Date("Attachment Date", required=True,
        default=fields.Datetime.today())
    attachment = fields.Binary("Attachment", help="Attach attachment here")


class LibraryAuthor(models.Model):
    _inherit = "library.author"

    book_ids = fields.Many2many("product.product", "author_book_rel",
        "author_id", "product_id", "Books", help="Related books")


class BookEditor(models.Model):
    """Book Editor Information"""

    _name = "book.editor"
    _description = "Information of Editor of the Book"

    image = fields.Binary("Image", help="Book Image")
    name = fields.Char("Name", required=True, index=True, help="Book name")
    biography = fields.Text("Biography", help="Biography")
    note = fields.Text("Notes", help="Notes")
    phone = fields.Char("Phone", help="Phone Number")
    mobile = fields.Char("Mobile", help="Mobile Number")
    fax = fields.Char("Fax", help="Fax")
    title = fields.Many2one("res.partner.title", "Title", help="Book title")
    website = fields.Char("Website", help="Enter website here")
    street = fields.Char("Street", help="Enter Street")
    street2 = fields.Char("Street2", help="Enter secondary street")
    city = fields.Char("City", help="Enter City")
    state_id = fields.Many2one( "res.country.state", "State",
        help="Enter state")
    zip = fields.Char("Zip", help="ZIP")
    country_id = fields.Many2one("res.country", "Country",
        help="Select country")
    book_id = fields.Many2one("product.product", "Book Ref",
        help="Select book ref")
