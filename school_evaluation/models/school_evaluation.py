# See LICENSE file for full copyright and licensing details.

from lxml import etree

from odoo import api, fields, models
from odoo.exceptions import ValidationError
from odoo.tools.translate import _


class SchoolEvaluation(models.Model):
    """Defining School Evaluation."""

    _name = "school.evaluation"
    _description = "School Evaluation details"
    _rec_name = "type"

    @api.depends("eval_line")
    def _compute_total_points(self):
        """Method to compute evaluation points"""
        for rec in self:
            if rec.eval_line:
                rec.total = sum(
                    line.point_id.rating
                    for line in rec.eval_line
                    if line.point_id.rating
                )

    student_id = fields.Many2one(
        "student.student", "Student Name", help="Select Student"
    )
    teacher_id = fields.Many2one(
        "school.teacher", "Teacher", help="Select teacher"
    )
    type = fields.Selection(
        [("student", "Student"), ("faculty", "Faculty")],
        "User Type",
        required=True,
        help="Type of evaluation",
    )
    date = fields.Date(
        "Evaluation Date",
        required=True,
        help="Evaluation Date",
        default=fields.Date.context_today,
    )
    eval_line = fields.One2many(
        "school.evaluation.line",
        "eval_id",
        "Questionnaire",
        help="Enter evaluation details",
    )
    total = fields.Float(
        "Total Points",
        compute="_compute_total_points",
        method=True,
        help="Total Points Obtained",
        store="True",
    )
    state = fields.Selection(
        [
            ("draft", "Draft"),
            ("start", "In Progress"),
            ("finished", "Finish"),
            ("cancelled", "Cancel"),
        ],
        "State",
        readonly=True,
        default="draft",
        help="State of evaluation line",
    )
    username = fields.Many2one(
        "res.users",
        "User",
        readonly=True,
        default=lambda self: self.env.user,
        help="Related user",
    )
    active = fields.Boolean(
        "Active", default=True, help="Activate/Deactivate record"
    )

    @api.model
    def default_get(self, fields):
        """Override method to get default value of teacher"""
        res = super(SchoolEvaluation, self).default_get(fields)
        if res.get("type") == "student":
            hr_emp_rec = self.env["school.teacher"].search(
                [("user_id", "=", self._uid)]
            )
            res.update({"teacher_id": hr_emp_rec.id})
        return res

    @api.model
    def fields_view_get(
        self, view_id=None, viewtype="form", toolbar=False, submenu=False
    ):
        """Inherited this method to hide the create,edit button from list"""

        res = super(SchoolEvaluation, self).fields_view_get(
            view_id=view_id,
            view_type=viewtype,
            toolbar=toolbar,
            submenu=submenu,
        )
        teacher_group = self.env.user.has_group("school.group_school_teacher")
        doc = etree.XML(res["arch"])
        if teacher_group:
            if viewtype == "tree":
                nodes = doc.xpath("//tree[@name='teacher_evaluation']")
                for node in nodes:
                    node.set("create", "false")
                    node.set("edit", "false")
                res["arch"] = etree.tostring(doc)
            if viewtype == "form":
                nodes = doc.xpath("//form[@name='teacher_evaluation']")
                for node in nodes:
                    node.set("create", "false")
                    node.set("edit", "false")
                res["arch"] = etree.tostring(doc)
        return res

    def get_record(self):
        """Method to get the evaluation questions"""
        eval_temp_obj = self.env["school.evaluation.template"]
        for rec in self:
            eval_list = []
            eval_temps_rec = eval_temp_obj.search([("type", "=", rec.type)])
            for eval_temp in eval_temps_rec:
                eval_list.append((0, 0, {"stu_eval_id": eval_temp.id}))
            if rec.eval_line:
                rec.write({"eval_line": []})
            rec.write({"eval_line": eval_list})
        return True

    def set_start(self):
        """change state to start"""
        for rec in self:
            if not rec.eval_line:
                raise ValidationError(
                    _(
                        'Please Get the Questions First!\
            \nTo Get the Questions please click on "Get Questions" Button!'
                    )
                )
        self.state = "start"

    def set_finish(self):
        """Change state to finished"""
        for rec in self:
            if [
                line.id
                for line in rec.eval_line
                if (not line.point_id or not line.rating)
            ]:
                raise ValidationError(
                    _(
                        """
                You can't mark the evaluation as Finished untill
                the Rating/Remarks are not added for all the Questions!"""
                    )
                )
        self.state = "finished"

    def set_cancel(self):
        """Change state to cancelled"""
        self.state = "cancelled"

    def set_draft(self):
        """Changes state to draft"""
        self.state = "draft"

    def unlink(self):
        """Inherited unlink method to check state at record deletion"""
        for rec in self:
            if rec.state in ["start", "finished"]:
                raise ValidationError(
                    _(
                        """
                    You can delete record in unconfirmed state only!"""
                    )
                )
        return super(SchoolEvaluation, self).unlink()


class StudentEvaluationLine(models.Model):
    """Defining School Evaluation Line."""

    _name = "school.evaluation.line"
    _description = "School Evaluation Line Details"

    eval_id = fields.Many2one(
        "school.evaluation", "Evaluation id", help="Select school evaluation"
    )
    stu_eval_id = fields.Many2one(
        "school.evaluation.template",
        "Question",
        help="Select evaluation question",
    )
    point_id = fields.Many2one(
        "rating.rating",
        "Rating",
        domain="[('template_id', '=', stu_eval_id)]",
        help="Evaluation point",
    )
    rating = fields.Char("Remarks", help="Enter remark")

    _sql_constraints = [
        (
            "number_uniq",
            "unique(eval_id, stu_eval_id)",
            "Questions already exist!",
        )
    ]

    @api.onchange("point_id")
    def onchange_point(self):
        """Method to get rating point based on rating"""
        self.rating = False
        if self.point_id:
            self.rating = self.point_id.feedback


class SchoolEvaluationTemplate(models.Model):
    """Defining School Evaluation Template."""

    _name = "school.evaluation.template"
    _description = "School Evaluation Template Details"
    _rec_name = "desc"

    desc = fields.Char("Description", required=True, help="Description")
    type = fields.Selection(
        [("faculty", "Faculty"), ("student", "Student")],
        "User Type",
        required=True,
        default="faculty",
        help="Type of Evaluation",
    )
    rating_line = fields.One2many(
        "rating.rating", "template_id", "Rating", help="Rating"
    )


class RatingRating(models.Model):
    """Defining Rating."""

    _inherit = "rating.rating"
    _description = "Rating"

    @api.model
    def create(self, vals):
        """Set Document model name for rating."""
        res_model_rec = self.env["ir.model"].search(
            [("model", "=", "school.evaluation.template")]
        )
        vals.update({"res_model_id": res_model_rec.id})
        res = super(RatingRating, self).create(vals)
        return res

    @api.depends("res_model", "res_id")
    def _compute_res_name(self):
        """Override this method to set the alternate rec_name as rating"""
        # cannot change the rec_name of session since
        #                    it is use to create the bus channel
        # so, need to override this method to set the same
        #                           alternative rec_name as rating
        for rate in self:
            if rate.res_model == "school.evaluation.template":
                rate.res_name = rate.rating
            else:
                super(RatingRating, self)._compute_res_name()

    template_id = fields.Many2one(
        "school.evaluation.template", "Stud", help="Ratings"
    )


class StudentExtend(models.Model):
    _inherit = "student.student"

    def set_alumni(self):
        """Override method to set active false student evaluation when
        student is set to alumni"""
        for rec in self:
            student_eval_rec = self.env["school.evaluation"].search(
                [("type", "=", "student"), ("student_id", "=", rec.id)]
            )
            if student_eval_rec:
                student_eval_rec.write({"active": False})
        return super(StudentExtend, self).set_alumni()
