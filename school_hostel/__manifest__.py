# See LICENSE file for full copyright and licensing details.

{
    "name": "Hostel Management for Education ERP",
    "version": "16.0.1.0.0",
    "author": "Serpent Consulting Services Pvt. Ltd.",
    "category": "School Management",
    "website": "http://www.serpentcs.com",
    "license": "AGPL-3",
    "complexity": "easy",
    "summary": "Module For HOSTEL Management In School",
    "depends": ["school"],
    "images": ["static/description/SchoolHostel.png"],
    "data": [
        "security/hostel_security.xml",
        "security/ir.model.access.csv",
        "data/hostel_schedular.xml",
        "views/hostel_view.xml",
        "data/hostel_sequence.xml",
        "report/hostel_fee_receipt.xml",
        "report/report_view.xml",
        "wizard/terminate_reason_view.xml",
    ],
    "demo": ["demo/school_hostel_demo.xml"],
    "installable": True,
}
