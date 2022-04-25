# See LICENSE file for full copyright and licensing details.


from odoo import api, fields, models


class TerminateReasonHostel(models.TransientModel):
    _inherit = "terminate.reason"

    hostel_info = fields.Text("Hostel Info", help="Hostel information")

    @api.model
    def default_get(self, fields):
        """Override method to dispaly message if student is registered in.

        hostel while terminationg.
        """
        res = super(TerminateReasonHostel, self).default_get(fields)
        student = self._context.get("active_id")
        student_rec = self.env["student.student"].browse(student)
        student_hostel_rec = self.env["hostel.student"].search(
            [("student_id", "=", student_rec.id),
            ("status", "in", ["reservation", "pending", "paid"])])
        hostel_msg = ""
        if student_hostel_rec:
            hostel_msg += (
                "\nStudent is registered in the hostel"
                + " "
                + student_hostel_rec.hostel_info_id.name
                + " "
                + "the hostel id is"
                + " "
                + student_hostel_rec.hostel_id
                + " "
                + "and room number is "
                + student_hostel_rec.room_id.room_no
            )
        res.update({"hostel_info": hostel_msg})
        return res

    def save_terminate(self):
        student = self._context.get("active_id")
        student_rec = self.env["student.student"].browse(student)
        student_hostel_rec = self.env["hostel.student"].search(
            [("student_id", "=", student_rec.id),
            ("status", "in", ["reservation", "pending", "paid"])])
        if student_hostel_rec:
            student_hostel_rec.active = False
            student_hostel_rec.room_id._compute_check_availability()
        return super(TerminateReasonHostel, self).save_terminate()
