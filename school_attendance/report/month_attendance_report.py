# See LICENSE file for full copyright and licensing details.

import calendar
from datetime import datetime

from odoo import api, models


class ReportMonthAttendace(models.AbstractModel):
    _name = "report.school_attendance.monthly_attendance_report_tmpl"
    _description = "Monthly Attendance Report"

    def get_dates(self, rec):
        days_of_month = calendar.monthrange(
            int(rec.academic_year_id.code), int(rec.month)
        )[1]
        return range(1, days_of_month + 1)

    def get_data(self, rec):
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
        group_data = []
        month = rec.month
        if int(rec.month) < 10:
            month = "0" + rec.month
        last_day_month = calendar.monthrange(
            int(rec.academic_year_id.code), int(month)
        )[1]
        start_date_str = (
            str(int(rec.academic_year_id.code)) + "-" + str(int(month)) + "-01"
        )
        end_date_str = (
            str(int(rec.academic_year_id.code))
            + "-"
            + str(int(month))
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

        records = []
        for record in self._cr.fetchall():
            if record and record[0]:
                records.append(record[0])
        for att in self.env["daily.attendance"].browse(records):
            date = datetime.strptime(str(att.date), "%Y-%m-%d %H:%M:%S")
            day_date = date.strftime("%Y-%m-%d")
            if not group_data:
                group_data.append(
                    {
                        "user": att.user_id,
                        "school_name": att.user_id.sudo().school_id.name,
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
                            "school_name": att.user_id.sudo().school_id.name,
                            "att_ids": [{"date": day_date, "att": [att]}],
                        }
                    )
        res_data = []
        for gdata in group_data:
            result_data = []
            att_data = {}
            data = []
            days_of_month = calendar.monthrange(
                int(rec.academic_year_id.code), int(date.strftime("%m"))
            )[1]
            for attdata in gdata.get("att_ids"):
                date = datetime.strptime(attdata.get("date"), "%Y-%m-%d")
                day_date = int(date.strftime("%d"))
                for att in attdata.get("att"):
                    no_of_class = 1
                    self._cr.execute(
                        """
                            SELECT
                                id
                            FROM
                                daily_attendance_line
                            WHERE
                                standard_id = %s
                            ORDER BY roll_no
                        """,
                        (att.id,),
                    )
                    lines = []
                    for line in self._cr.fetchall():
                        if line and line[0]:
                            lines.append(line[0])
                    matched_dates = []
                    for student in self.env["daily.attendance.line"].browse(
                        lines
                    ):
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
                                    att_data.update(
                                        {
                                            student.stud_id.name: {
                                                att_count: str(status)
                                            }
                                        }
                                    )
                                    total_absent = 0
                                    if not student.is_present:
                                        total_absent = no_of_class
                                    data.append(
                                        {
                                            "roll_no": student.stud_id.roll_no,
                                            "student_code": student.stud_id.student_code,
                                            "total_absent": total_absent,
                                            "name": student.stud_id.name,
                                            "att": {att_count: str(status)},
                                        }
                                    )
                                else:
                                    att_data.get(student.stud_id.name).update(
                                        {att_count: str(status)}
                                    )
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
                                            "total_absent": 0,
                                            "name": student.stud_id.name,
                                            "att": {att_count: status},
                                        }
                                    )
                                else:
                                    if (
                                        att_data.get(student.stud_id.name).get(
                                            "att_count"
                                        )
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
                    "school_name": gdata.get("school_name"),
                    "month": months.get(rec.month)
                    + "-"
                    + rec.academic_year_id.code,
                    "batch": rec.course_id.name,
                    "result_data": result_data,
                    "elective_subject": rec.is_elective_subject,
                    "subject": rec.subject_id.name,
                }
            )
        return res_data

    def get_total_class(self, rec):
        # total_class = 0
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
        self._cr.execute(
            """
            SELECT
                id
            FROM
                daily_attendance
            WHERE
                state = 'validate' and
                standard_id = %s and
                date >= '%s' and
                date <= '%s' ORDER BY user_id,date
                """,
            (rec.course_id.id, start_date_str, end_date_str),
        )
        records = []
        for record in self._cr.fetchall():
            if record and record[0]:
                records.append(record[0])
        # for att in self.env["daily.attendance"].browse(records):
        #     total_class += 1
        return {"total": len(records)}

    @api.model
    def _get_report_values(self, docids, data):
        report = self.env["ir.actions.report"]
        emp_report = report._get_report_from_name(
            "school_attendance.monthly_attendance_report_tmpl"
        )
        model = self.env.context.get("active_model")
        docs = self.env[model].browse(self.env.context.get("active_id"))
        return {
            "doc_ids": docids,
            "doc_model": emp_report.model,
            "data": data,
            "docs": docs,
            "get_dates": self.get_dates,
            "get_total_class": self.get_total_class,
            "get_data": self.get_data,
        }
