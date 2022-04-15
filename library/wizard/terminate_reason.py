# See LICENSE file for full copyright and licensing details.

from odoo import api, fields, models


class TerminateReasonLibrary(models.TransientModel):
    _inherit = "terminate.reason"

    info = fields.Text("Message", help="Enter message")

    @api.model
    def default_get(self, fields):
        """Override method to display message if student has issued book
        while terminate student"""
        res = super(TerminateReasonLibrary, self).default_get(fields)
        student_obj = self.env["student.student"].browse(
            self._context.get("active_id"))
        library_card_rec = self.env["library.card"].search(
            [("student_id", "=", student_obj.id), ("state", "=", "running")]
        )
        book_issue_rec = self.env["library.book.issue"].search([
            ("state", "in", ["issue", "reissue"]),
            ("student_id", "=", student_obj.id)],
            limit=1)
        card_info = ""
        if library_card_rec:
            card_info += (
                "The student has library card assigned with number"
                + " "
                + library_card_rec.code
                or "")
        for data in book_issue_rec:
            card_info += ("\nStudent has issued the book " + " " +
                    data.name.name + " " + "issue number is" + " " +
                    data.issue_code + " " + "and library card number is" +
                    " " + data.card_id.code)
        res.update({"info": card_info})
        return res
