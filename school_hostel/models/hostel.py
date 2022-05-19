# See LICENSE file for full copyright and licensing details.

from datetime import datetime

from dateutil.relativedelta import relativedelta as rd

from odoo import _, api, fields, models
from odoo.exceptions import ValidationError
from odoo.tools import DEFAULT_SERVER_DATETIME_FORMAT


class ResPartner(models.Model):
    _inherit = "res.partner"

    is_hostel_rector = fields.Boolean("Hostel Rector",
        help="Activate if the following person is hostel rector")


class HostelType(models.Model):
    _name = "hostel.type"
    _description = "Information of type of Hostel"

    name = fields.Char("HOSTEL Name", required=True, help="Name of Hostel")
    type = fields.Selection([("male", "Boys"), ("female", "Girls"),
        ("common", "Common")], "HOSTEL Type", help="Type of Hostel",
        required=True, default="common")
    other_info = fields.Text("Other Information",
        help="Enter more information")
    rector = fields.Many2one("res.partner", "Rector",
        help="Select hostel rector")
    room_ids = fields.One2many("hostel.room", "name", "Room",
        help="Enter hostel rooms")
    student_ids = fields.One2many("hostel.student", "hostel_info_id",
        string="Students", help="Enter students")

    @api.model
    def _search(self, args, offset=0, limit=None, order=None,
        count=False, access_rights_uid=None,):
        """Override method to get hostel of student selected"""
        if self._context.get("student_id"):
            stud_obj = self.env["student.student"]
            stud = stud_obj.browse(self._context["student_id"])
            datas = []
            if stud.gender:
                self._cr.execute(
"""select id from hostel_type where type=%s or type='common' """,
                    (stud.gender,),)
                data = self._cr.fetchall()
                for d in data:
                    datas.append(d[0])
            args.append(("id", "in", datas))
        return super(HostelType, self)._search(args=args,
            offset=offset, limit=limit, order=order,
            count=count, access_rights_uid=access_rights_uid,)


class HostelRoom(models.Model):

    _name = "hostel.room"
    _description = "Hostel Room Information"
    _rec_name = "room_no"

    @api.depends("student_per_room", "student_ids")
    def _compute_check_availability(self):
        """Method to check room availability"""
        for rec in self:
            rec.availability = rec.student_per_room - len(rec.student_ids.ids)

    name = fields.Many2one("hostel.type", "HOSTEL", help="Name of hostel")
    floor_no = fields.Integer("Floor No.", default=1, help="Floor Number")
    room_no = fields.Char("Room No.", required=True)
    student_per_room = fields.Integer("Student Per Room", required=True,
        help="Students allocated per room")
    availability = fields.Float(compute="_compute_check_availability",
        store=True, string="Availability", help="Room availability in hostel")
    rent_amount = fields.Float("Rent Amount Per Month",
        help="Enter rent amount per month")
    hostel_amenities_ids = fields.Many2many("hostel.amenities",
        "hostel_room_amenities_rel", "account_id", "tax_id",
        string="Hostel Amenities", domain="[('active', '=', True)]",
        help="Select hostel roon amenities")
    student_ids = fields.One2many("hostel.student", "room_id",
        string="Students", help="Enter students")

    _sql_constraints = [
        ("room_no_unique", "unique(room_no)", "Room number must be unique!"),
        ("floor_per_hostel", "check(floor_no < 99)",
            "Error ! Floor per HOSTEL should be less than 99."),
        ("student_per_room_greater", "check(student_per_room < 10)",
            "Error ! Student per room should be less than 10.")]

    @api.constrains("rent_amount")
    def _check_rent_amount(self):
        """Constraint on negative rent amount"""
        if self.rent_amount < 0:
            raise ValidationError(_(
"Rent Amount Per Month should not be a negative value!"))


class HostelStudent(models.Model):
    _name = "hostel.student"
    _description = "Hostel Student Information"
    _rec_name = "student_id"

    @api.depends("room_rent", "paid_amount")
    def _compute_remaining_fee_amt(self):
        """Method to compute hostel amount"""
        for rec in self:
            rec.remaining_amount = rec.room_rent - (rec.paid_amount or 0.0)

    def _compute_invoices(self):
        """Method to compute number of invoice of student"""
        inv_obj = self.env["account.move"]
        for rec in self:
            rec.compute_inv = inv_obj.search_count(
                [("hostel_student_id", "=", rec.id)])

    @api.depends("duration")
    def _compute_rent(self):
        """Method to compute hostel room rent"""
        for rec in self:
            rec.room_rent = rec.duration * rec.room_id.rent_amount

    @api.depends("status")
    def _get_hostel_user(self):
        user_group = self.env.ref("school_hostel.group_hostel_user")
        if user_group.id in [group.id for group in self.env.user.groups_id]:
            self.hostel_user = True

    hostel_id = fields.Char("HOSTEL ID", readonly=True,
        help="Enter Hostel ID", default=lambda self: _("New"))
    compute_inv = fields.Integer("Number of invoice",
        compute="_compute_invoices", help="No of invoice of related student")
    student_id = fields.Many2one("student.student", "Student",
        help="Select student")
    school_id = fields.Many2one("school.school", "School",
        help="Select school")
    room_rent = fields.Float("Total Room Rent", compute="_compute_rent",
        required=True, help="Rent of room")
    admission_date = fields.Datetime("Admission Date",
        help="Date of admission in hostel",
        default=fields.Datetime.now)
    discharge_date = fields.Datetime("Discharge Date",
        help="Date on which student discharge")
    paid_amount = fields.Float("Paid Amount", help="Amount Paid")
    hostel_info_id = fields.Many2one(
        "hostel.type", "Hostel", help="Select hostel type"
    )
    room_id = fields.Many2one("hostel.room", "Room",
        help="Select hostel room")
    duration = fields.Integer("Duration", help="Enter duration of living")
    rent_pay = fields.Float("Rent", help="Enter rent pay of the hostel")
    acutal_discharge_date = fields.Datetime("Actual Discharge Date",
        help="Date on which student discharge")
    remaining_amount = fields.Float(compute="_compute_remaining_fee_amt",
        string="Remaining Amount")
    status = fields.Selection([("draft", "Draft"),
        ("reservation", "Reservation"), ("pending", "Pending"),
        ("paid", "Done"),("discharge", "Discharge"), ("cancel", "Cancel")],
        string="Status", copy=False, default="draft",
        help="State of the student hostel")
    hostel_types = fields.Char("Type", help="Enter hostel type")
    stud_gender = fields.Char("Gender", help="Student gender")
    active = fields.Boolean("Active", default=True,
        help="Activate/Deactivate hostel record")

    _sql_constraints = [("admission_date_greater",
        "check(discharge_date >= admission_date)",
        "Error ! Discharge Date cannot be set" "before Admission Date!")]

    @api.constrains("duration")
    def check_duration(self):
        """Method to check duration should be greater than zero"""
        if self.duration <= 0:
            raise ValidationError(_("Duration should be greater than 0!"))

    @api.constrains("room_id")
    def check_room_avaliable(self):
        """Check Room Availability"""
        if self.room_id.availability <= 0:
            raise ValidationError(_(
                "There is no availability in the room!"))

    @api.onchange("hostel_info_id")
    def onchange_hostel_types(self):
        """Onchange method for hostel type"""
        self.hostel_types = self.hostel_info_id.type

    @api.onchange("student_id")
    def onchange_student_gender(self):
        """Method to get gender of student"""
        self.stud_gender = self.student_id.gender

    @api.onchange("hostel_info_id")
    def onchange_hostel(self):
        """Method to make room false when hostel changes"""
        self.room_id = False

    def cancel_state(self):
        """Method to change state to cancel"""
        for rec in self:
            rec.status = "cancel"
            # increase room availability
            rec.room_id.availability += 1

    def reservation_state(self):
        """Method to change state to reservation"""
        sequence_obj = self.env["ir.sequence"]
        for rec in self:
            if rec.hostel_id == "New":
                rec.hostel_id = sequence_obj.next_by_code(
                    "hostel.student") or _("New")
            rec.status = "reservation"

    @api.onchange("admission_date", "duration")
    def onchnage_discharge_date(self):
        """To calculate discharge date based on current date and duration"""
        if self.admission_date:
            self.discharge_date = self.admission_date + rd(months=self.duration
                )

    @api.model
    def create(self, vals):
        """This method is to set Discharge Date according to values added in
        admission date or duration fields."""
        res = super(HostelStudent, self).create(vals)
        res.discharge_date = res.admission_date + rd(months=res.duration)
        return res

    def write(self, vals):
        """This method is to set Discharge Date according to changes in.

        admission date or duration fields.
        """
        addmissiondate = self.admission_date
        if vals.get("admission_date"):
            addmissiondate = datetime.strptime(
                vals.get("admission_date"), DEFAULT_SERVER_DATETIME_FORMAT)
        if vals.get("admission_date") or vals.get("duration"):
            duration_months = vals.get("duration") or self.duration
            discharge_date = addmissiondate + rd(months=duration_months)
            vals.update({"discharge_date": discharge_date})
        return super(HostelStudent, self).write(vals)

    def unlink(self):
        """Inherited unlink method to make check state at record deletion"""
        status_list = ["reservation", "pending", "paid"]
        for rec in self:
            if rec.status in status_list:
                raise ValidationError(_(
                    "You can delete record in unconfirmed state!"))
        return super(HostelStudent, self).unlink()

    @api.constrains("student_id")
    def check_student_registration(self):
        """Constraint to check student record duplication in hostel"""
        if self.search([
                ("student_id", "=", self.student_id.id),
                ("status", "not in", ["cancel", "discharge"]),
                ("id", "not in", self.ids)]):
            raise ValidationError(_(
                "Selected student is already registered!"))

    def discharge_state(self):
        """Method to change state to discharge"""
        for rec in self:
            rec.status = "discharge"
            rec.room_id.availability += 1
            # set discharge date equal to current date
            rec.acutal_discharge_date = fields.datetime.today()

    def student_expire(self):
        """ Schedular to discharge student from hostel"""
        current_date = fields.datetime.today()
        for student in self.env["hostel.student"].search(
                [("discharge_date", "<", current_date),
                ("status", "!=", "draft")]):
            student.discharge_state()

    def invoice_view(self):
        """Method to view number of invoice of student"""
        invoice_obj = self.env["account.move"]
        for rec in self:
            invoices_rec = invoice_obj.search([("hostel_student_id", "=",
                                                rec.id)])
            action = rec.env.ref("account.action_move_out_invoice_type"
                ).read()[0]
            if len(invoices_rec) > 1:
                action["domain"] = [("id", "in", invoices_rec.ids)]
            elif len(invoices_rec) == 1:
                action["views"] = [
                    (rec.env.ref("account.view_move_form").id, "form")]
                action["res_id"] = invoices_rec.ids[0]
            else:
                action = {"type": "ir.actions.act_window_close"}
        return action

    def pay_fees(self):
        """Method generate invoice of hostel fees of student"""
        invoice_obj = self.env["account.move"]
        for rec in self:
            rec.write({"status": "pending"})
            partner = rec.student_id and rec.student_id.partner_id
            vals = {"partner_id": partner.id,
                    "move_type": "out_invoice",
                    "hostel_student_id": rec.id,
                    "hostel_ref": rec.hostel_id}
            account_inv_id = invoice_obj.create(vals)
            acc_id = account_inv_id.journal_id.default_account_id.id
            account_view_id = rec.env.ref("account.view_move_form")
            for _move_line in account_inv_id:
                account_inv_id.write({"invoice_line_ids": [(0, 0, {
                    "name": rec.hostel_info_id.name,
                    "account_id": acc_id,
                    "quantity": rec.duration,
                    "price_unit": rec.room_id.rent_amount,
                })]})
            return {
                "name": _("Pay Hostel Fees"),
                "view_mode": "form",
                "res_model": "account.move",
                "view_id": account_view_id.id,
                "type": "ir.actions.act_window",
                "nodestroy": True,
                "target": "current",
                "res_id": account_inv_id.id,
                "context": {},
            }

    def print_fee_receipt(self):
        """Method to print fee reciept"""
        return self.env.ref("school_hostel.report_hostel_fee_reciept_qweb"
            ).report_action(self)


class HostelAmenities(models.Model):
    _name = "hostel.amenities"

    name = fields.Char("Name", help="Provided Hostel Amenity")
    active = fields.Boolean("Active",
        help="Activate/Deactivate whether the amenity should be given or not")


class AccountMove(models.Model):

    _inherit = "account.move"

    hostel_student_id = fields.Many2one("hostel.student",
        string="Hostel Student", help="Select hostel student")
    hostel_ref = fields.Char("Hostel Fees Reference",
        help="Hostel Fee Reference")


class AccountPaymentRegister(models.TransientModel):
    _inherit = "account.payment.register"

    def action_create_payments(self):
        """
            Override method to write paid amount in hostel student
        """
        res = super(AccountPaymentRegister, self).action_create_payments()
        inv = False
        for rec in self:
            if self._context.get('active_model') == 'account.move':
                inv = self.env['account.move'].browse(self._context.get('active_ids', []))
            vals = {}
            if inv.hostel_student_id and inv.payment_state == "paid":
                fees_payment = inv.hostel_student_id.paid_amount + rec.amount
                vals.update({"status": "paid", "paid_amount": fees_payment})
                inv.hostel_student_id.write(vals)
            elif inv.hostel_student_id and inv.payment_state == "partial":
                fees_payment = inv.hostel_student_id.paid_amount + rec.amount
                vals.update({
                    "status": "pending",
                    "paid_amount": fees_payment,
                    "remaining_amount": inv.amount_residual})
            inv.hostel_student_id.write(vals)
        return res


class Student(models.Model):
    _inherit = "student.student"

    def set_alumni(self):
        """Override method to make record of hostel student active false when.

        student is set to alumni.
        """
        student_hostel_obj = self.env["hostel.student"]
        for rec in self:
            student_hostel_rec = student_hostel_obj.search(
                [("student_id", "=", rec.id),
                ("status", "in", ["reservation", "pending", "paid"])])
            if student_hostel_rec:
                student_hostel_rec.active = False
                student_hostel_rec.room_id._compute_check_availability()
        return super(Student, self).set_alumni()
