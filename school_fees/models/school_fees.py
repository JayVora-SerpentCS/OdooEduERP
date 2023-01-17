# See LICENSE file for full copyright and licensing details.

from odoo import _, api, fields, models
from odoo.exceptions import ValidationError


class StudentFeesRegister(models.Model):
    """Student fees Register"""

    _name = "student.fees.register"
    _description = "Student fees Register"

    @api.depends("line_ids")
    def _compute_total_amount(self):
        """Method to compute total amount"""
        for rec in self:
            total_amt = sum(line.total for line in rec.line_ids)
            rec.total_amount = total_amt

    name = fields.Char("Name", required=True, help="Enter Name")
    date = fields.Date(
        "Date",
        required=True,
        help="Date of register",
        default=fields.Date.context_today,
    )
    number = fields.Char(
        "Number",
        readonly=True,
        default=lambda self: _("New"),
        help="Sequence number of fee registration form",
    )
    line_ids = fields.One2many(
        "student.payslip", "register_id", "PaySlips", help="Student payslips"
    )
    total_amount = fields.Float(
        "Total", compute="_compute_total_amount", help="Fee total amounts"
    )
    state = fields.Selection(
        [("draft", "Draft"), ("confirm", "Confirm")],
        "State",
        readonly=True,
        default="draft",
        help="State of student fee registration form",
    )
    journal_id = fields.Many2one(
        "account.journal",
        "Journal",
        help="Select Journal",
        required=False,
        default=lambda self: self.env["account.journal"].search(
            [("type", "=", "sale")], limit=1
        ),
    )
    company_id = fields.Many2one(
        "res.company",
        "Company",
        required=True,
        change_default=True,
        readonly=True,
        default=lambda self: self.env.user.company_id,
        help="Select related company",
    )
    fees_structure = fields.Many2one(
        "student.fees.structure", "Fees Structure", help="Fee structure"
    )
    standard_id = fields.Many2one(
        "standard.standard", "Class", help="Enter student standard"
    )

    def fees_register_draft(self):
        """Changes the state to draft"""
        self.state = "draft"

    def fees_register_confirm(self):
        """Method to confirm payslip"""
        stud_obj = self.env["student.student"]
        slip_obj = self.env["student.payslip"]
        school_std_obj = self.env["school.standard"]
        for rec in self:
            if not rec.journal_id:
                raise ValidationError(_("Kindly, Select Account Journal!"))
            if not rec.fees_structure:
                raise ValidationError(_("Kindly, Select Fees Structure!"))
            school_std_rec = school_std_obj.search(
                [("standard_id", "=", rec.standard_id.id)]
            )
            for stu in stud_obj.search(
                [
                    ("standard_id", "in", school_std_rec.ids),
                    ("state", "=", "done"),
                ]
            ):
                # Check if payslip exist of student
                if slip_obj.search(
                    [("student_id", "=", stu.id), ("date", "=", rec.date)]
                ):
                    raise ValidationError(
                        _(
                            "There exists a Fees record for: %s for same "
                            "date.!"
                        )
                        % stu.name
                    )
                else:
                    rec.number = self.env["ir.sequence"].next_by_code(
                        "student.fees.register"
                    ) or _("New")
                    res = {
                        "student_id": stu.id,
                        "register_id": rec.id,
                        "name": rec.name,
                        "date": rec.date,
                        "company_id": rec.company_id.id,
                        "currency_id": rec.company_id.currency_id.id or False,
                        "journal_id": rec.journal_id.id,
                        "fees_structure_id": rec.fees_structure.id or False,
                    }
                    slip_rec = slip_obj.create(res)
                    slip_rec.onchange_student()
            # Calculate the amount
            amount = sum([data.total for data in rec.line_ids])
            rec.write({"total_amount": amount, "state": "confirm"})


class StudentPayslipLine(models.Model):
    """Student PaySlip Line"""

    _name = "student.payslip.line"
    _description = "Student PaySlip Line"

    name = fields.Char("Name", required=True, help="Payslip")
    code = fields.Char("Code", required=True, help="Payslip code")
    type = fields.Selection(
        [("month", "Monthly"), ("year", "Yearly"), ("range", "Range")],
        "Duration",
        required=True,
        help="Select payslip type",
    )
    amount = fields.Float("Amount", digits=(16, 2), help="Fee amount")
    line_ids = fields.One2many(
        "student.payslip.line.line",
        "slipline_id",
        "Calculations",
        help="Payslip line",
    )
    slip_id = fields.Many2one(
        "student.payslip", "Pay Slip", help="Select student payslip"
    )
    description = fields.Text("Description", help="Description")
    company_id = fields.Many2one(
        "res.company",
        "Company",
        change_default=True,
        default=lambda self: self.env.user.company_id,
        help="Related company",
    )
    currency_id = fields.Many2one(
        "res.currency", "Currency", help="Select currency"
    )
    currency_symbol = fields.Char(
        related="currency_id.symbol", string="Symbol", help="Currency Symbol"
    )
    account_id = fields.Many2one(
        "account.account", "Account", help="Related account"
    )
    product_id = fields.Many2one("product.product", "Product", required=True)

    @api.onchange("company_id")
    def set_currency_onchange(self):
        """Onchange method to assign currency on change company"""
        for rec in self:
            rec.currency_id = rec.company_id.currency_id.id


class StudentFeesStructureLine(models.Model):
    """Student Fees Structure Line"""

    _name = "student.fees.structure.line"
    _description = "Student Fees Structure Line"
    _order = "sequence"

    name = fields.Char("Name", required=True, help="Enter fee structure name")
    code = fields.Char("Code", required=True, help="Fee structure code")
    type = fields.Selection(
        [("month", "Monthly"), ("year", "Yearly"), ("range", "Range")],
        "Duration",
        required=True,
        help="Fee structure type",
    )
    product_id = fields.Many2one("product.product", "Product", required=True)
    amount = fields.Float("Amount", digits=(16, 2), help="Fee amount")
    sequence = fields.Integer(
        "Sequence", help="Sequence of fee structure form"
    )
    line_ids = fields.One2many(
        "student.payslip.line.line",
        "slipline1_id",
        "Calculations",
        help="Student payslip line",
    )
    account_id = fields.Many2one("account.account", string="Account")
    company_id = fields.Many2one(
        "res.company",
        "Company",
        change_default=True,
        default=lambda self: self.env.user.company_id,
        help="Related company",
    )
    currency_id = fields.Many2one(
        "res.currency", "Currency", help="Select currency"
    )
    currency_symbol = fields.Char(
        related="currency_id.symbol",
        string="Symbol",
        help="Select currency symbol",
    )

    @api.onchange("company_id")
    def set_currency_company(self):
        for rec in self:
            rec.currency_id = rec.company_id.currency_id.id

    @api.onchange("product_id")
    def onchange_product_id(self):
        for rec in self:
            rec.amount = rec.product_id and rec.product_id.list_price or 0


class StudentFeesStructure(models.Model):
    """Fees structure"""

    _name = "student.fees.structure"
    _description = "Student Fees Structure"

    name = fields.Char("Name", required=True, help="Fee structure name")
    code = fields.Char("Code", required=True, help="Fee structure code")
    line_ids = fields.Many2many(
        "student.fees.structure.line",
        "fees_structure_payslip_rel",
        "fees_id",
        "slip_id",
        "Fees Structure",
        help="Fee structure line",
    )

    _sql_constraints = [
        (
            "code_uniq",
            "unique(code)",
            "The code of the Fees Structure must be unique !",
        )
    ]


class StudentPayslip(models.Model):
    _name = "student.payslip"
    _description = "Student PaySlip"

    fees_structure_id = fields.Many2one(
        "student.fees.structure",
        "Fees Structure",
        states={"paid": [("readonly", True)]},
        help="Select fee structure",
    )
    standard_id = fields.Many2one(
        "school.standard", "Class", help="Select school standard"
    )
    division_id = fields.Many2one(
        "standard.division", "Division", help="Select standard division"
    )
    medium_id = fields.Many2one(
        "standard.medium", "Medium", help="Select standard medium"
    )
    register_id = fields.Many2one(
        "student.fees.register", "Register", help="Select student fee register"
    )
    name = fields.Char("Description", help="Payslip name")
    number = fields.Char(
        "Number",
        readonly=True,
        default=lambda self: _("/"),
        copy=False,
        help="Payslip number",
    )
    student_id = fields.Many2one(
        "student.student", "Student", required=True, help="Select student"
    )
    date = fields.Date(
        "Date",
        readonly=True,
        help="Current Date of payslip",
        default=fields.Date.context_today,
    )
    line_ids = fields.One2many(
        "student.payslip.line",
        "slip_id",
        "PaySlip Line",
        copy=False,
        help="Payslips",
    )
    total = fields.Monetary("Total", readonly=True, help="Total Amount")
    state = fields.Selection(
        [
            ("draft", "Draft"),
            ("confirm", "Confirm"),
            ("pending", "Pending"),
            ("paid", "Paid"),
        ],
        "State",
        readonly=True,
        default="draft",
        help="State of the student payslip",
    )
    journal_id = fields.Many2one(
        "account.journal",
        "Journal",
        required=False,
        help="Select journal for account",
    )
    paid_amount = fields.Monetary("Paid Amount", help="Amount Paid")
    due_amount = fields.Monetary("Due Amount", help="Amount Remaining")
    currency_id = fields.Many2one(
        "res.currency", "Currency", help="Selelct currency"
    )
    currency_symbol = fields.Char(
        related="currency_id.symbol", string="Symbol", help="Currency symbol"
    )
    move_id = fields.Many2one(
        "account.move",
        "Journal Entry",
        readonly=True,
        ondelete="restrict",
        copy=False,
        help="Link to the automatically generated Journal Items.",
    )
    payment_date = fields.Date(
        "Payment Date",
        readonly=True,
        states={"draft": [("readonly", False)]},
        help="Keep empty to use the current date",
    )
    type = fields.Selection(
        [
            ("out_invoice", "Customer Invoice"),
            ("in_invoice", "Supplier Invoice"),
            ("out_refund", "Customer Refund"),
            ("in_refund", "Supplier Refund"),
        ],
        "Type",
        required=True,
        change_default=True,
        default="out_invoice",
        help="Payslip type",
    )
    company_id = fields.Many2one(
        "res.company",
        "Company",
        required=True,
        change_default=True,
        readonly=True,
        default=lambda self: self.env.user.company_id,
        help="Related company",
    )

    _sql_constraints = [
        (
            "code_uniq",
            "unique(student_id,date,state)",
            "The code of the Fees Structure must be unique !",
        )
    ]

    @api.onchange("student_id")
    def onchange_student(self):
        """Method to get standard , division , medium of student selected"""
        if self.student_id and self.student_id.standard_id:
            standard = self.student_id.standard_id
            self.standard_id = standard.id
            self.division_id = standard.division_id.id or False
            self.medium_id = self.student_id.medium_id or False

    def unlink(self):
        """Inherited unlink method to check state at the record deletion"""
        for rec in self:
            if rec.state != "draft":
                raise ValidationError(
                    _("You can delete record in unconfirm state only!")
                )
        return super(StudentPayslip, self).unlink()

    @api.onchange("journal_id")
    def onchange_journal_id(self):
        """Method to get currency from journal"""
        for rec in self:
            journal = rec.journal_id
            currency_id = (
                journal
                and journal.currency_id
                and journal.currency_id.id
                or journal.company_id.currency_id.id
            )
            rec.currency_id = currency_id

    def _update_student_vals(self, vals):
        student_rec = self.env["student.student"].browse(
            vals.get("student_id")
        )
        vals.update(
            {
                "standard_id": student_rec.standard_id.id,
                "division_id": student_rec.standard_id.division_id.id,
                "medium_id": student_rec.medium_id.id,
            }
        )

    @api.model
    def create(self, vals):
        """Inherited create method to assign values from student model"""
        if vals.get("student_id"):
            self._update_student_vals(vals)
        return super(StudentPayslip, self).create(vals)

    def write(self, vals):
        """Inherited write method to update values from student model"""
        if vals.get("student_id"):
            self._update_student_vals(vals)
        return super(StudentPayslip, self).write(vals)

    def payslip_draft(self):
        """Change state to draft"""
        self.state = "draft"

    def payslip_paid(self):
        """Change state to paid"""
        self.state = "paid"

    def payslip_confirm(self):
        """Method to confirm payslip"""
        for rec in self:
            if not rec.journal_id:
                raise ValidationError(_("Kindly, Select Account Journal!"))
            if not rec.fees_structure_id:
                raise ValidationError(_("Kindly, Select Fees Structure!"))
            lines = []
            for data in rec.fees_structure_id.line_ids or []:
                line_vals = {
                    "slip_id": rec.id,
                    "product_id": data.product_id.id,
                    "name": data.name,
                    "code": data.code,
                    "type": data.type,
                    "account_id": data.account_id.id,
                    "amount": data.amount,
                    "currency_id": data.currency_id.id or False,
                    "currency_symbol": data.currency_symbol or False,
                }
                lines.append((0, 0, line_vals))
            rec.write({"line_ids": lines})
            # Compute amount
            amount = 0
            amount = sum(data.amount for data in rec.line_ids)
            rec.register_id.write({"total_amount": rec.total})
            rec.write(
                {
                    "total": amount,
                    "state": "confirm",
                    "due_amount": amount,
                    "currency_id": rec.company_id.currency_id.id or False,
                }
            )
            template = (
                self.env["mail.template"]
                .sudo()
                .search([("name", "ilike", "Fees Reminder")], limit=1)
            )
            if template:
                for user in rec.student_id.parent_id:
                    subject = _("Fees Reminder")
                    if user.email:
                        body = _(
                            """
                        <div>
                            <p>Dear """
                            + str(user.display_name)
                            + """,
                            <br/><br/>
                            We are getting in touch as school fees due on """
                            + str(rec.date)
                            + """ remain unpaid for """
                            + str(rec.student_id.display_name)
                            + """.
                            <br/><br/>
                            We kindly ask that you arrange to pay the """
                            + str(rec.due_amount)
                            + """ balance as soon as possible.
                            <br/><br/>
                            Thank You.
                        </div>"""
                        )
                        template.send_mail(
                            rec.id,
                            email_values={
                                "email_from": self.env.user.email or "",
                                "email_to": user.email,
                                "subject": subject,
                                "body_html": body,
                            },
                            force_send=True,
                        )

    def invoice_view(self):
        """View number of invoice of student"""
        invoice_obj = self.env["account.move"]
        for rec in self:
            invoices_rec = invoice_obj.search(
                [("student_payslip_id", "=", rec.id)]
            )
            action = rec.env.ref(
                "account.action_move_out_invoice_type"
            ).read()[0]
            if len(invoices_rec) > 1:
                action["domain"] = [("id", "in", invoices_rec.ids)]
            elif len(invoices_rec) == 1:
                action["views"] = [
                    (rec.env.ref("account.view_move_form").id, "form")
                ]
                action["res_id"] = invoices_rec.ids[0]
            else:
                action = {"type": "ir.actions.act_window_close"}
        return action

    def action_move_create(self):
        cur_obj = self.env["res.currency"]
        move_obj = self.env["account.move"]
        move_line_obj = self.env["account.move.line"]
        for fees in self:
            if not fees.journal_id.sequence_id:
                raise ValidationError(
                    _(
                        "Please define sequence on the journal related to "
                        "this invoice."
                    )
                )
            # field 'centralisation' from account.journal
            #  is deprecated field since v9
            if fees.move_id:
                continue
            ctx = self._context.copy()
            ctx.update({"lang": fees.student_id.lang})
            if not fees.payment_date:
                self.write([fees.id], {"payment_date": fields.Date.today()})
            company_currency = fees.company_id.currency_id.id
            diff_currency_p = fees.currency_id.id != company_currency
            current_currency = (
                fees.currency_id and fees.currency_id.id or company_currency
            )
            account_id = False
            comapny_ac_id = False
            if fees.type in ("in_invoice", "out_refund"):
                account_id = fees.student_id.property_account_payable.id
                cmpy_id = fees.company_id.partner_id
                comapny_ac_id = cmpy_id.property_account_receivable.id
            elif fees.type in ("out_invoice", "in_refund"):
                account_id = fees.student_id.property_account_receivable.id
                cmp_id = fees.company_id.partner_id
                comapny_ac_id = cmp_id.property_account_payable.id
            move = {
                "ref": fees.name,
                "journal_id": fees.journal_id.id,
                "date": fees.payment_date or fields.Date.today(),
            }
            ctx.update({"company_id": fees.company_id.id})
            move_id = move_obj.create(move)
            context_multi_currency = self._context.copy()
            context_multi_currency.update({"date": fields.Date.today()})
            debit = 0.0
            credit = 0.0
            if fees.type in ("in_invoice", "out_refund"):
                # compute method from res.currency is deprecated
                #    since v12 and replaced with _convert
                credit = cur_obj._convert(
                    fees.total, company_currency, fees.company_id, self.date
                )
            elif fees.type in ("out_invoice", "in_refund"):
                debit = cur_obj._convert(
                    fees.total, company_currency, fees.company_id, self.date
                )
            if debit < 0:
                credit = -debit
                debit = 0.0
            if credit < 0:
                debit = -credit
                credit = 0.0
            sign = debit - credit < 0 and -1 or 1
            cr_id = diff_currency_p and current_currency or False
            am_cr = diff_currency_p and sign * fees.total or 0.0
            date = fees.payment_date or fields.Date.today()
            move_line = {
                "name": fees.name or "/",
                "move_id": move_id,
                "debit": debit,
                "credit": credit,
                "account_id": account_id,
                "journal_id": fees.journal_id.id,
                "parent_id": fees.student_id.parent_id.id,
                "currency_id": cr_id,
                "amount_currency": am_cr,
                "date": date,
            }
            move_line_obj.create(move_line)
            cr_id = diff_currency_p and current_currency or False
            move_line = {
                "name": fees.name or "/",
                "move_id": move_id,
                "debit": credit,
                "credit": debit,
                "account_id": comapny_ac_id,
                "journal_id": fees.journal_id.id,
                "parent_id": fees.student_id.parent_id.id,
                "currency_id": cr_id,
                "amount_currency": am_cr,
                "date": date,
            }
            move_line_obj.create(move_line)
            fees.write({"move_id": move_id})
            move_obj.action_post([move_id])

    def student_pay_fees(self):
        """Generate invoice of student fee"""
        sequence_obj = self.env["ir.sequence"]
        for rec in self:
            if rec.number == "/":
                rec.number = sequence_obj.next_by_code("student.payslip") or _(
                    "New"
                )
            rec.state = "pending"
            partner = rec.student_id and rec.student_id.partner_id
            vals = {
                "partner_id": partner.id,
                "invoice_date": rec.date,
                "journal_id": rec.journal_id.id,
                "name": rec.number,
                "student_payslip_id": rec.id,
                "move_type": "out_invoice",
            }
            invoice_line = []
            for line in rec.line_ids:
                #     replaced / deprecated fields of v13:
                #     default_debit_account_id,
                #     default_credit_account_id from account.journal
                acc_id = rec.journal_id.default_account_id.id
                if line.account_id.id:
                    acc_id = line.account_id.id
                invoice_line_vals = {
                    "name": line.name,
                    "product_id": line.product_id.id,
                    "account_id": acc_id,
                    "quantity": 1.000,
                    "price_unit": line.amount,
                }
                invoice_line.append((0, 0, invoice_line_vals))
            vals.update({"invoice_line_ids": invoice_line})
            # creates invoice
            account_invoice_id = self.env["account.move"].create(vals)
            invoice_obj = self.env.ref("account.view_move_form")
            return {
                "name": _("Pay Fees"),
                "view_mode": "form",
                "res_model": "account.move",
                "view_id": invoice_obj.id,
                "type": "ir.actions.act_window",
                "nodestroy": True,
                "target": "current",
                "res_id": account_invoice_id.id,
                "context": {},
            }


class StudentPayslipLineLine(models.Model):
    """Function Line."""

    _name = "student.payslip.line.line"
    _description = "Function Line"
    _order = "sequence"

    slipline_id = fields.Many2one(
        "student.payslip.line", "Slip Line Ref", help="Student payslip line"
    )
    slipline1_id = fields.Many2one(
        "student.fees.structure.line", "Slip Line", help="Student payslip line"
    )
    sequence = fields.Integer("Sequence", help="Sequence of payslip")
    from_month = fields.Many2one(
        "academic.month", "From Month", help="Academic starting month"
    )
    to_month = fields.Many2one(
        "academic.month", "To Month", help="Academic end month"
    )


class AccountMove(models.Model):
    _inherit = "account.move"

    student_payslip_id = fields.Many2one(
        "student.payslip",
        string="Student Payslip",
        help="Select student payslip",
    )


class AccountPaymentRegister(models.TransientModel):
    _inherit = "account.payment.register"

    def action_create_payments(self):
        """
            Override method to write paid amount in hostel student
        """
        res = super(AccountPaymentRegister, self).action_create_payments()
        invoice = False
        curr_date = fields.Date.today()
        for rec in self:
            if self._context.get("active_model") == "account.move":
                invoice = self.env["account.move"].browse(
                    self._context.get("active_ids", [])
                )
            vals = {}
            #        'invoice_ids' deprecated field instead of this
            #                             used delegation with account_move
            vals.update({"due_amount": invoice.amount_residual})
            if invoice.student_payslip_id and invoice.payment_state == "paid":
                # Calculate paid amount and changes state to paid
                fees_payment = (
                    invoice.student_payslip_id.paid_amount + rec.amount
                )
                vals.update(
                    {
                        "state": "paid",
                        "payment_date": curr_date,
                        "move_id": invoice.id or False,
                        "paid_amount": fees_payment,
                        "due_amount": invoice.amount_residual,
                    }
                )
            if (
                invoice.student_payslip_id
                and invoice.payment_state == "not_paid"
            ):
                # Calculate paid amount and due amount and changes state
                # to pending
                fees_payment = (
                    invoice.student_payslip_id.paid_amount + rec.amount
                )
                vals.update(
                    {
                        "state": "pending",
                        "due_amount": invoice.amount_residual,
                        "paid_amount": fees_payment,
                    }
                )
            invoice.student_payslip_id.write(vals)
        return res


class StudentFees(models.Model):
    _inherit = "student.student"

    def set_alumni(self):
        """Override method to raise warning when fees payment of student is
        remaining when student set to alumni state"""
        student_payslip_obj = self.env["student.payslip"]
        for rec in self:
            if student_payslip_obj.search(
                [
                    ("student_id", "=", rec.id),
                    ("state", "in", ["confirm", "pending"]),
                ]
            ):
                raise ValidationError(
                    _(
                        "You cannot alumni student because payment of fees "
                        "of student is remaining!"
                    )
                )
            return super(StudentFees, self).set_alumni()
