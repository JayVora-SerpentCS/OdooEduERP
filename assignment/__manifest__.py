# -*- coding: utf-8 -*-
# See LICENSE file for full copyright and licensing details.

{'name': 'Assignment Management',
 'version': "10.0.1.0.0",
 'author': "Serpent Consulting Services Pvt. Ltd., Odoo SA",
 'website': 'http://www.serpentcs.com',
 'license': "AGPL-3",
 'category': 'School Management',
 'summary': 'A Module For Assignment Management In School',
 'complexity': 'easy',
 'depends': ['school'],
 'data': ['views/homework_view.xml', 'security/ir.model.access.csv'],
 'test': ['test/assignment.yml'],
 'installable': True,
 'application': True,
 'auto_install' : False
}
