# See LICENSE file for full copyright and licensing details.

{
    "name": "School Event Management For Education ERP",
    "version": "17.0.1.0.0",
    "author": "Serpent Consulting Services Pvt. Ltd.",
    "website": "http://www.serpentcs.com",
    "images": ["static/description/Banner_school_event_17.png"],
    "category": "School Management",
    "license": "AGPL-3",
    "summary": "A Module For Event Management In School",
    "depends": ["school", "event"],
    "data": [
        "security/event_security.xml",
        "security/ir.model.access.csv",
        "views/event_view.xml",
        "views/participants.xml",
        "views/report_view.xml",
    ],
    "demo": ["demo/event_demo.xml"],
    "installable": True,
    "application": True,
}
