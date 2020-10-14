# See LICENSE file for full copyright and licensing details.

{
    "name": "Attendance Management for Education ERP",
    "version": "14.0.1.0.0",
    "author": "Serpent Consulting Services Pvt. Ltd.",
    "website": "http://www.serpentcs.com",
    "images": ["static/description/SchoolAttendance.png"],
    "category": "School Management",
    "license": "AGPL-3",
    "summary": "A Module For Attendance Management In School",
    "complexity": "easy",
    "depends": ["school", "web_widget_x2many_2d_matrix"],
    #    Here the module web_widget_x2many_2d_matrix is a OCA module
    #    To install : Refer the link provided in README file.
    "data": [
        "security/attendance_security.xml",
        "security/ir.model.access.csv",
        "views/school_attendance_view.xml",
        "wizard/attendance_sheet_wizard_view.xml",
        "wizard/student_attendance_by_month_view.xml",
        "report/month_attendance.xml",
        "report/report_view.xml",
    ],
    "demo": ["demo/school_attendance_demo.xml"],
    "installable": True,
    "application": True,
}
