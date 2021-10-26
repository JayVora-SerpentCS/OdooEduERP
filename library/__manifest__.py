# See LICENSE file for full copyright and licensing details.

{
    "name": "Library Management for Education ERP",
    "version": "14.0.1.0.0",
    "author": "Serpent Consulting Services Pvt. Ltd.",
    "category": "School Management",
    "website": "http://www.serpentcs.com",
    "license": "AGPL-3",
    "summary": "A Module For Library Management For School",
    "complexity": "easy",
    "depends": ["school", "stock", "delivery", "purchase"],
    "data": [
        "data/library_sequence.xml",
        "data/library_category_data.xml",
        "data/library_card_schedular.xml",
        "security/library_security.xml",
        "security/ir.model.access.csv",
        'views/card_details.xml',
        "report/report_view.xml",
        "report/qrcode_label.xml",
        "views/library_view.xml",
        "wizard/terminate_reason.xml",
    ],
    "demo": ["demo/library_demo.xml"],
    "image": ["static/description/SchoolLibrary.png"],
    "installable": True,
    "application": True,
}
