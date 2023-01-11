# See LICENSE file for full copyright and licensing details.

{
    "name": "Evaluation Management for Education ERP",
    "version": "16.0.1.0.0",
    "author": "Serpent Consulting Services Pvt. Ltd.",
    "website": "http://www.serpentcs.com",
    "category": "School Management",
    "license": "AGPL-3",
    "summary": "A Module For Evaluation Management In School",
    "images": ["static/description/Evaluation1.jpg"],
    "depends": ["school", "rating"],
    "data": [
        "security/evaluation_security.xml",
        "security/ir.model.access.csv",
        "views/school_evaluation_view.xml",
    ],
    "demo": ["demo/school_evaluation_demo.xml"],
    "assets": {
        "web.assets_backend": [
            "/school_evaluation/static/src/css/school_evaluation.css"
        ]
    },
    "installable": True,
    "application": True,
}
