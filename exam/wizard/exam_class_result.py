# -*- encoding: utf-8 -*-
##############################################################################
#
#    OpenERP, Open Source Management Solution
#    Copyright (C) 2004-2009 Tiny SPRL (<http://tiny.be>).
#    Copyright (C) 2011-2012 Serpent Consulting Services (<http://www.serpentcs.com>)
#    Copyright (C) 2013-2014 Serpent Consulting Services (<http://www.serpentcs.com>)
#    This program is free software: you can redistribute it and/or modify
#    it under the terms of the GNU Affero General Public License as
#    published by the Free Software Foundation, either version 3 of the
#    License, or (at your option) any later version.
#
#    This program is distributed in the hope that it will be useful,
#    but WITHOUT ANY WARRANTY; without even the implied warranty of
#    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#    GNU Affero General Public License for more details.
#
#    You should have received a copy of the GNU Affero General Public License
#    along with this program.  If not, see <http://www.gnu.org/licenses/>.
#
##############################################################################
from openerp.osv import osv,fields
from openerp.tools.translate import _

class result_print(osv.TransientModel):

    _name = 'result.print'
    _description = 'students result'
    _columns = {
            'standard_id': fields.many2one("school.standard", "Standard", required=True),
            'exam_id': fields.many2one("exam.exam","Exam"),
            'year_id':fields.many2one('academic.year', 'Academic Year', required=True),
    }

    def get_result(self, cr, uid, ids, context=None):
        if context is None:
            context = {}
        domain = []
        for result_line in self.browse(cr, uid, ids, context = context):
            domain = [('standard_id','=',result_line.standard_id.id),('s_exam_ids','=',result_line.exam_id.id)]
            return {
            'name': _('Result Info'),
            'view_type': 'form',
            "view_mode": 'tree,form',
            'res_model': 'exam.result',
            'type': 'ir.actions.act_window',
            'domain': domain,
            }
        return True

# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4: