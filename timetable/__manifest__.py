# See LICENSE file for full copyright and licensing details.

{
    "name": "Timetable Management",
    "version": "15.0.1.0.0",
    "author": """Serpent Consulting Services Pvt. Ltd.""",
    "website": "http://www.serpentcs.com",
    "license": "AGPL-3",
    "category": "School Management",
    "complexity": "easy",
    "summary": "A Module For Timetable Management In School",
    "images": ["static/description/SchoolTimetable.png"],
    "depends": ["school"],
    "data": [
        "security/timetable_security.xml",
        "security/ir.model.access.csv",
        "report/report_view.xml",
        "report/timetable.xml",
        "views/timetable_view.xml",
    ],
    "demo": ["demo/timetable_demo.xml"],
    "installable": True,
    "application": True,
}
