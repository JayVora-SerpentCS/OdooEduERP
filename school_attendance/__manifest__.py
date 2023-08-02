# See LICENSE file for full copyright and licensing details.

{
    "name": "Attendance Management",
    "version": "16.0.1.0.0",
    "author": "Serpent Consulting Services Pvt. Ltd.",
    "website": "http://www.serpentcs.com",
    "images": ["static/description/SchoolAttendance.png"],
    "category": "School Management",
    "license": "AGPL-3",
    "summary": "A Module For Attendance Management In School",
    "complexity": "easy",
    "depends": ["school", "hr"],
    "data": [
        "security/attendance_security.xml",
        "security/ir.model.access.csv",
        "views/school_attendance_view.xml",
        "views/month_attendance.xml",
        "views/report_view.xml",
        "wizard/attendance_sheet_wizard_view.xml",
        "wizard/student_attendance_by_month_view.xml",
        "wizard/monthly_attendance_wizard_view.xml",
        "report/monthly_attendance_report_view.xml",
    ],
    "demo": ["demo/school_attendance_demo.xml"],
    "installable": True,
    "application": True,
}
