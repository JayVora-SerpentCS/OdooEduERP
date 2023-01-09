# See LICENSE file for full copyright and licensing details.

from odoo import api, models


class ReportTimetableInfo(models.AbstractModel):
    _name = "report.timetable.timetable"
    _description = "Timetable details"

    def _get_timetable(self, timetable_id):
        """Method to combain values for timetable"""
        timetable_detail = []
        self._cr.execute(
            """
                SELECT
                    t.start_time,
                    t.end_time,
                    s.name,
                    week_day,
                    st.employee_id,
                    hr.name as teacher
                FROM
                    time_table_line t,
                    subject_subject s,
                    resource_resource r,
                    school_teacher st,
                    hr_employee hr
                WHERE
                    t.subject_id= s.id
                and
                    t.teacher_id=st.id
                and
                    st.employee_id= hr.id
                and
                    t.table_id = %s
                group by
                    start_time,end_time,
                    s.name,
                    week_day,
                    st.employee_id,
                    hr.name
                order by start_time
            """,
            tuple([timetable_id.id]),
        )
        res = self._cr.dictfetchall()
        self._cr.execute(
            """
                SELECT
                    start_time,
                    end_time
                FROM
                    time_table_line
                WHERE
                    table_id=%s
                group by
                    start_time,end_time
                order by start_time
            """,
            tuple([timetable_id.id]),
        )
        time_data = self._cr.dictfetchall()
        for time_detail in time_data:
            for data in res:
                if (
                    time_detail.get("start_time") == data.get("start_time")
                ) and (time_detail.get("end_time") == data.get("end_time")):
                    if data.get("name") == "Recess":
                        time_detail[data["week_day"]] = data.get("name")
                    else:
                        td = (
                            data.get("name")
                            + "\n("
                            + data.get("teacher")
                            + ")"
                        )
                        time_detail[data["week_day"]] = td
            timetable_detail.append(time_detail)
        return timetable_detail

    @api.model
    def _get_report_values(self, docids, data=None):
        """Inherited method to get report data"""
        timetable_report = self.env["ir.actions.report"]._get_report_from_name(
            "timetable.timetable"
        )
        docs = self.env["time.table"].browse(docids)
        return {
            "doc_ids": docids,
            "docs": docs,
            "doc_model": timetable_report.model,
            "data": data,
            "get_timetable": self._get_timetable,
        }
