# See LICENSE file for full copyright and licensing details.

# from cStringIO import StringIO
import base64
import calendar
import io
from datetime import date, datetime, timedelta

from odoo import _, api, fields, models
from odoo.exceptions import ValidationError
from odoo.tools import DEFAULT_SERVER_DATETIME_FORMAT

try:
    import xlsxwriter
except:
    pass


class DailyAttendanceStudentRemark(models.TransientModel):
    _name = "monthly.attendance.wizard"
    _description = "Monthly Attendance Sheet"

    def _get_current_academic_year(self):
        return self.env["academic.year"].search([("current", "=", True)])

    academic_year_id = fields.Many2one(
        "academic.year",
        ondelete="restrict",
        string="Academic Session",
        default=lambda obj: obj.env["academic.year"].search(
            [("current", "=", True)]
        ),
    )
    course_id = fields.Many2one(
        "school.standard", "Class", ondelete="restrict"
    )
    user_id = fields.Many2one("school.teacher", "Teacher")
    month = fields.Selection(
        [
            ("1", "January"),
            ("2", "February"),
            ("3", "March"),
            ("4", "April"),
            ("5", "May"),
            ("6", "June"),
            ("7", "July"),
            ("8", "August"),
            ("9", "September"),
            ("10", "October"),
            ("11", "November"),
            ("12", "December"),
        ],
        "Month",
    )
    month_str = fields.Char("Month")
    subject_ids = fields.Many2many(
        "subject.subject",
        "subject_wizard_rel",
        "subject_id",
        "wizard_id",
        "Subject",
        ondelete="restrict",
    )
    subject_id = fields.Many2one("subject.subject", "Subject", help="Subject")
    is_elective_subject = fields.Boolean(
        "Is Elective Subject", help="Check this if subject is elective."
    )

    @api.onchange("is_elective_subject")
    def onchange_is_elective_subject(self):
        self.subject_id = False

    @api.onchange("month")
    def onchange_month(self):
        for rec in self:
            rec.month_str = ""
            if rec.month:
                months = {
                    "1": "January",
                    "2": "February",
                    "3": "March",
                    "4": "April",
                    "5": "May",
                    "6": "June",
                    "7": "July",
                    "8": "August",
                    "9": "September",
                    "10": "October",
                    "11": "November",
                    "12": "December",
                }
                rec.month_str = months.get(rec.month)

    def generate_attendance(self):
        data = self.read()[0]
        for rec in self:
            # months = {
            #     "1": "January",
            #     "2": "February",
            #     "3": "March",
            #     "4": "April",
            #     "5": "May",
            #     "6": "June",
            #     "7": "July",
            #     "8": "August",
            #     "9": "September",
            #     "10": "October",
            #     "11": "November",
            #     "12": "December",
            # }
            # days_of_month = calendar.monthrange(
            #     int(rec.academic_year_id.code), int(rec.month)
            # )[1]
            # month_days = range(1, days_of_month + 1)
            last_day_month = calendar.monthrange(
                int(rec.academic_year_id.code), int(rec.month)
            )[1]
            start_date_str = (
                str(int(rec.academic_year_id.code))
                + "-"
                + str(int(rec.month))
                + "-01"
            )
            end_date_str = (
                str(int(rec.academic_year_id.code))
                + "-"
                + str(int(rec.month))
                + "-"
                + str(last_day_month)
                + " 23:00:00"
            )

            elective_subject = f"and is_elective_subject = 'f'"
            if rec.is_elective_subject:
                elective_subject = f"and subject_id = {rec.subject_id.id}"

            self._cr.execute(
                f"""
                SELECT
                    id
                FROM
                    daily_attendance
                WHERE
                    state = 'validate' and
                    standard_id = %s and
                    date >= %s and
                    date <= %s 
                    {elective_subject} ORDER BY user_id,date
                    """,
                (rec.course_id.id, start_date_str, end_date_str),
            )
            if not self._cr.fetchall():
                raise ValidationError(_("Data Not Found"))
        if not self.user_id:
            report_id = self.env.ref(
                "school_attendance.monthly_attendance_report"
            )
            return report_id.report_action(self, data=data, config=False)

    @api.model
    def _send_monthly_attendance(self):
        pr_mon = pre_month = (
            date.today().replace(day=1) - timedelta(days=1)
        ).month
        pr_mon = str(pr_mon)
        for subject in self.env["subject.subject"].search([]):
            for user in subject.teacher_ids:
                if int(pre_month) < 10:
                    pre_month = "0" + str(pre_month)
                academic_year = self.env["academic.year"].search(
                    [("current", "=", True)]
                )
                last_day_month = calendar.monthrange(
                    int(academic_year.code), int(pre_month)
                )[1]
                start_date_str = (
                    str(int(academic_year.code))
                    + "-"
                    + str(int(pre_month))
                    + "-01"
                )
                end_date_str = (
                    str(int(academic_year.code))
                    + "-"
                    + str(int(pre_month))
                    + "-"
                    + str(last_day_month)
                    + " 23:00:00"
                )
                self._cr.execute(
                    """select id
                                    from daily_attendance WHERE
                                    state = 'validate' and
                                    standard_id = %s and
                                    user_id = %s and
                                    date >= %s and
                                    date <= %s ORDER BY user_id,date
                                    """,
                    (
                        subject.course_id.id,
                        user.id,
                        start_date_str,
                        end_date_str,
                    ),
                )
                vals = {
                    "user_id": user.id,
                    "course_id": subject.course_id.id,
                    "month": pr_mon,
                    "subject_ids": [(6, 0, [subject.id])],
                }
                wizard = self.create(vals)
                wizard.onchange_month()
                attachment_id = wizard.generate_attendance()
                template_id = self.env["ir.model.data"].get_object_reference(
                    "school_attendance", "email_template_monthly_attendace"
                )[1]
                template_rec = self.env["mail.template"].browse(template_id)
                template_rec.write(
                    {"attachment_ids": [(6, 0, [attachment_id.id])]}
                )
                template_rec.send_mail(wizard.id, force_send=True)
        return True

    def get_total_class(self, rec, teacher, subject):
        # total_class = 0
        user = self.env["school.teacher"].search(
            [("name", "=", teacher)], limit=1
        )
        subject = self.env["subject.subject"].search(
            [("id", "=", subject)], limit=1
        )
        last_day_month = calendar.monthrange(
            int(rec.academic_year_id.code), int(rec.month)
        )[1]
        start_date_str = (
            str(int(rec.academic_year_id.code))
            + "-"
            + str(int(rec.month))
            + "-01"
        )
        end_date_str = (
            str(int(rec.academic_year_id.code))
            + "-"
            + str(int(rec.month))
            + "-"
            + str(last_day_month)
            + " 23:00:00"
        )

        elective_subject = f"and is_elective_subject = 'f'"
        if rec.is_elective_subject:
            elective_subject = f"and subject_id = {rec.subject_id.id}"

        self._cr.execute(
            f"""
            SELECT
                id
            FROM
                daily_attendance
            WHERE
                state = 'validate' and
                standard_id = %s and
                user_id = %s and
                date >= %s and
                date <= %s 
                {elective_subject} ORDER BY user_id,date
                """,
                (
                    rec.course_id.id,
                    user.id,
                    start_date_str,
                    end_date_str,
                ),
        )

        records = []
        for record in self._cr.fetchall():
            if record and record[0]:
                records.append(record[0])
        # for att in self.env["daily.attendance"].browse(records):
        #     total_class += 1
        total_class_att = {"total": len(records)}

        class_str = ""
        if total_class_att["total"] == 0:
            class_str += "Total No. of Classes: "
        else:
            class_str += "Total No. of Combined Classes: "
        if total_class_att["total"] != 0:
            class_str += str(total_class_att["total"])
        return (class_str, total_class_att)

    def print_report(self):
        attch_obj = self.env["ir.attachment"]
        # fp = StringIO()
        fp = io.BytesIO()
        for rec in self:
            months = {
                "1": "January",
                "2": "February",
                "3": "March",
                "4": "April",
                "5": "May",
                "6": "June",
                "7": "July",
                "8": "August",
                "9": "September",
                "10": "October",
                "11": "November",
                "12": "December",
            }
            days_of_month = calendar.monthrange(
                int(rec.academic_year_id.code), int(rec.month)
            )[1]
            month_days = range(1, days_of_month + 1)
            last_day_month = calendar.monthrange(
                int(rec.academic_year_id.code), int(rec.month)
            )[1]
            start_date_str = (
                str(int(rec.academic_year_id.code))
                + "-"
                + str(int(rec.month))
                + "-01"
            )
            end_date_str = (
                str(int(rec.academic_year_id.code))
                + "-"
                + str(int(rec.month))
                + "-"
                + str(last_day_month)
                + " 23:00:00"
            )

            elective_subject = f"and is_elective_subject = 'f'"
            if rec.is_elective_subject:
                elective_subject = f"and subject_id = {rec.subject_id.id}"

            self._cr.execute(
                f"""
                SELECT
                    id
                FROM
                    daily_attendance
                WHERE
                    state = 'validate' and
                    standard_id = %s and
                    date >= %s and
                    date <= %s 
                    {elective_subject} ORDER BY user_id,date
                    """,
                    (
                        rec.course_id.id,
                        start_date_str,
                        end_date_str,
                    ),
            )
            all_att_data = self._cr.fetchall()
            records = []
            if not all_att_data:
                raise ValidationError(_("Data Not Found"))
            for record in all_att_data:
                if record and record[0]:
                    records.append(record[0])
            group_data = []
            for att in self.env["daily.attendance"].browse(records):
                date = datetime.strptime(
                    str(att.date), DEFAULT_SERVER_DATETIME_FORMAT
                )
                day_date = date.strftime("%Y-%m-%d")
                if not group_data:
                    group_data.append(
                        {
                            "user": att.user_id,
                            "att_ids": [{"date": day_date, "att": [att]}],
                        }
                    )
                else:
                    flag = False
                    for gdata in group_data:
                        if gdata.get("user").id == att.user_id.id:
                            flag = True
                            flag_date = False
                            for att_id in gdata.get("att_ids"):
                                if att_id.get("date") == day_date:
                                    flag_date = True
                                    att_id.get("att").append(att)
                                    break
                            if not flag_date:
                                gdata.get("att_ids").append(
                                    {"date": day_date, "att": [att]}
                                )
                    if not flag:
                        group_data.append(
                            {
                                "user": att.user_id,
                                "att_ids": [{"date": day_date, "att": [att]}],
                            }
                        )
            res_data = []
            for gdata in group_data:
                result_data = []
                att_data = {}
                data = []
                for attdata in gdata.get("att_ids"):
                    date = datetime.strptime(attdata.get("date"), "%Y-%m-%d")
                    day_date = int(date.strftime("%d"))
                    for att in attdata.get("att"):
                        no_of_class = 1
                        self._cr.execute(
                            """select id
                                from daily_attendance_line WHERE
                                standard_id = %s ORDER BY roll_no
                            """,
                            (att.id,),
                        )
                        lines = []
                        for line in self._cr.fetchall():
                            if line and line[0]:
                                lines.append(line[0])
                        matched_dates = []
                        for student in self.env[
                            "daily.attendance.line"
                        ].browse(lines):
                            for att_count in range(1, days_of_month + 1):
                                if day_date == att_count:
                                    status = "A"
                                    if student.is_present:
                                        status = no_of_class
                                        if (
                                            day_date in matched_dates
                                            or not matched_dates
                                        ):
                                            if att_data.get(
                                                student.stud_id.name
                                            ) and att_data.get(
                                                student.stud_id.name
                                            ).get(
                                                att_count
                                            ):
                                                if (
                                                    att_data.get(
                                                        student.stud_id.name
                                                    ).get(att_count)
                                                    != "A"
                                                ):
                                                    status = (
                                                        int(
                                                            att_data.get(
                                                                student.stud_id.name
                                                            ).get(att_count)
                                                        )
                                                        + no_of_class
                                                    )
                                    else:
                                        if day_date in matched_dates:
                                            if att_data.get(
                                                student.stud_id.name
                                            ) and att_data.get(
                                                student.stud_id.name
                                            ).get(
                                                att_count
                                            ):
                                                if (
                                                    att_data.get(
                                                        student.stud_id.name
                                                    ).get(att_count)
                                                    != "A"
                                                ):
                                                    status = int(
                                                        att_data.get(
                                                            student.stud_id.name
                                                        ).get(att_count)
                                                    )
                                    if not att_data.get(student.stud_id.name):
                                        total_absent = 0
                                        if not student.is_present:
                                            total_absent = no_of_class
                                        att_data.update(
                                            {
                                                student.stud_id.name: {
                                                    att_count: str(status)
                                                }
                                            }
                                        )
                                        data.append(
                                            {
                                                "roll_no": student.stud_id.roll_no,
                                                "student_code": student.stud_id.student_code,
                                                "school_name": student.stud_id.school_id.name,
                                                "divisions": gdata.get(
                                                    "divisions"
                                                ),
                                                "total_absent": total_absent,
                                                "name": student.stud_id.name,
                                                "att": {
                                                    att_count: str(status)
                                                },
                                            }
                                        )
                                    else:
                                        att_data.get(
                                            student.stud_id.name
                                        ).update({att_count: str(status)})
                                        for stu in data:
                                            if (
                                                stu.get("name")
                                                == student.stud_id.name
                                            ):
                                                if not student.is_present:
                                                    stu.update(
                                                        {
                                                            "total_absent": stu.get(
                                                                "total_absent"
                                                            )
                                                            + no_of_class
                                                        }
                                                    )
                                                stu.get("att").update(
                                                    {att_count: str(status)}
                                                )
                                else:
                                    status = ""
                                    if not att_data.get(student.stud_id.name):
                                        att_data.update(
                                            {
                                                student.stud_id.name: {
                                                    att_count: status
                                                }
                                            }
                                        )
                                        data.append(
                                            {
                                                "roll_no": student.stud_id.roll_no,
                                                "student_code": student.stud_id.student_code,
                                                "school_name": student.stud_id.school_id.name,
                                                "divisions": gdata.get(
                                                    "divisions"
                                                ),
                                                "total_absent": 0,
                                                "name": student.stud_id.name,
                                                "att": {att_count: status},
                                            }
                                        )
                                    else:
                                        if (
                                            att_data.get(
                                                student.stud_id.name
                                            ).get("att_count")
                                            == ""
                                        ):
                                            att_data.get(
                                                student.stud_id.name
                                            ).update({att_count: status})
                                            for stu in data:
                                                if (
                                                    stu.get("name")
                                                    == student.stud_id.name
                                                ):
                                                    stu.get("att").update(
                                                        {att_count: status}
                                                    )
                            if day_date not in matched_dates:
                                matched_dates.append(day_date)
                roll_no_list = []
                for stu in data:
                    roll_no_list.append(stu.get("roll_no"))
                roll_no_list.sort()
                for roll_no in roll_no_list:
                    for stu in data:
                        if stu.get("roll_no") == roll_no:
                            result_data.append(stu)
                            data.remove(stu)
                res_data.append(
                    {
                        "user": gdata.get("user").name,
                        "month": months.get(rec.month)
                        + "-"
                        + rec.academic_year_id.code,
                        "semester": rec.course_id.name,
                        "result_data": result_data,
                        "school_name": result_data,
                    }
                )

            # Create Work Book
            workbook = xlsxwriter.Workbook(fp)
            # Set Table Header format
            tbl_data_fmt = workbook.add_format(
                {
                    "border": 1,
                    "font_name": "Calibri",
                    "align": "center",
                    "font_size": 10,
                }
            )
            tbl_data_fmt.set_bg_color("#D3D3D3")
            tbl_data_fmt_left = workbook.add_format(
                {"border": 1, "font_name": "Calibri", "font_size": 10}
            )
            tbl_data_fmt_p = workbook.add_format(
                {
                    "border": 1,
                    "font_name": "Calibri",
                    "align": "center",
                    "font_size": 10,
                }
            )
            # sub header format
            head_fmt = workbook.add_format(
                {
                    "border": 1,
                    "font_name": "Calibri",
                    "font_size": 10,
                    "align": "center",
                    "bold": True,
                }
            )
            head_fmt_left = workbook.add_format(
                {
                    "border": 1,
                    "font_name": "Calibri",
                    "font_size": 10,
                    "bold": True,
                }
            )
            # Main head format
            main_head_fmt = workbook.add_format(
                {
                    "border": 1,
                    "font_name": "Calibri",
                    "align": "center",
                    "font_size": 14,
                    "bold": True,
                }
            )
            main_head_fmt.set_bg_color("#DCDCDC")
            # print the data of students
            for data in res_data:
                count = 1
                row = 5
                # Add Sheet
                sheet = workbook.add_worksheet(data.get("user"))
                sheet.freeze_panes(5, 0)
                # Main Header
                sheet.merge_range(
                    0,
                    0,
                    0,
                    len(month_days) + 4,
                    data.get("result_data")[0].get("school_name"),
                    main_head_fmt,
                )
                sheet.set_column(0, 0, 3)
                sheet.set_column(3, len(month_days) + 4, 3)
                sheet.set_column(1, 1, 25)
                # Sub Headers
                sheet.merge_range(
                    1,
                    0,
                    1,
                    8,
                    "Name of the Teacher:" + str(data.get("user")),
                    head_fmt_left,
                )
                sheet.merge_range(
                    1,
                    9,
                    1,
                    19,
                    "Month:"
                    + str(months.get(rec.month))
                    + "-"
                    + str(rec.academic_year_id.code),
                    head_fmt,
                )
                sheet.merge_range(
                    1, 29, 1, 34, "Batch:" + str(rec.course_id.name), head_fmt
                )
                if rec.is_elective_subject:
                    sheet.merge_range(
                        2,
                        0,
                        2,
                        8,
                        "Subject:" + str(rec.subject_id.name),
                        head_fmt_left,
                    )
                sheet.merge_range(
                    1, 20, 1, 28, "key P=Present, A=Absent", head_fmt
                )
                sheet.write(4, 0, "Sn.", head_fmt)
                sheet.write(4, 1, "Name", head_fmt)
                sheet.write(4, 2, "Reg. No", head_fmt)
                col = 3
                for mday in month_days:
                    sheet.write(4, col, mday, head_fmt)
                    col += 1
                sheet.write(4, col, "P", head_fmt)
                sheet.write(4, col + 1, "A", head_fmt)
                for line in data.get("result_data"):
                    present_no = 0
                    present = 0
                    absent = 0
                    col = 0
                    if line.get("divisions") or data.get("elective"):
                        sheet.write(row, col, count, tbl_data_fmt)
                    else:
                        sheet.write(
                            row, col, line.get("student_code"), tbl_data_fmt
                        )
                    sheet.write(
                        row, col + 1, line.get("name"), tbl_data_fmt_left
                    )
                    sheet.write(
                        row,
                        col + 2,
                        line.get("stud_reg_code"),
                        tbl_data_fmt_left,
                    )

                    col = col + 3
                    for date in month_days:
                        if line.get("att").get(date):
                            if line.get("att").get(date) not in ["A", False]:
                                present_no = present + int(
                                    line.get("att").get(date)
                                )
                                present = present + int(
                                    line.get("att").get(date)
                                )
                            if line.get("att").get(date) == "A":
                                absent += 1
                                sheet.write(
                                    row,
                                    col,
                                    line.get("att").get(date),
                                    tbl_data_fmt,
                                )
                            elif line.get("att").get(date) != "A":
                                sheet.write(
                                    row, col, 'P', tbl_data_fmt_p
                                )
                        col += 1
                    sheet.write(row, col, present, tbl_data_fmt_p)
                    absent_res = absent
                    self._cr.execute(
                        """
                            SELECT
                                id,
                                medium_id
                            FROM
                                student_student
                            WHERE
                                roll_no = %s
                        """,
                        (line.get("roll_no"),),
                    )
                    student = self._cr.fetchone()
                    if student:
                        total_class_att = self.get_total_class(
                            rec, data.get("user"), data.get("subject_id")
                        )[1]
                        if not total_class_att.get("total"):
                            if student[1] == 3:
                                if present + absent != total_class_att.get(
                                    "A"
                                ):
                                    absent_res = (
                                        total_class_att.get("A") - present
                                    )
                            elif student[1] == 4:
                                if present + absent != total_class_att.get(
                                    "B"
                                ):
                                    absent_res = (
                                        total_class_att.get("B") - present
                                    )
                    if total_class_att.get("A") == 0:
                        sheet.write(
                            row,
                            col + 1,
                            total_class_att.get("total") - present_no,
                            tbl_data_fmt,
                        )
                    else:
                        sheet.write(
                            row,
                            col + 1,
                            line.get("total_absent"),
                            tbl_data_fmt,
                        )
                    row += 1
                    count += 1
            # Workbook save and end
            workbook.close()
            data = base64.b64encode(fp.getvalue())
            fp.close()
            # Deleting existing attachment files
            attach_ids = attch_obj.search(
                [("res_model", "=", "monthly.attendance.wizard")]
            )
            if attach_ids:
                try:
                    attach_ids.unlink()
                except:
                    pass
            # Creating Attachment
            doc_id = attch_obj.create(
                {
                    "name": str(months.get(rec.month))
                    + " "
                    + str(rec.course_id.name)
                    + " "
                    + "Monthly Attendance.xlsx",
                    "datas": data,
                    "res_model": "monthly.attendance.wizard",
                }
            )
            # Downloading the file
            return {
                "type": "ir.actions.act_url",
                "url": "web/content/%s?download=true" % (doc_id.id),
                "target": "current",
            }
