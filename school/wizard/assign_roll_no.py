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

from openerp.osv import fields,osv

# This wizard is designed for assigning the roll number to a student.

class assign_roll_no(osv.TransientModel):

    _name = 'assign.roll.no'
    _description = 'Assign Roll Number'
    _columns = {
        'standard_id': fields.many2one('standard.standard', 'Class', required=True),
        'medium_id': fields.many2one('standard.medium', 'Medium', required=True),
        'division_id': fields.many2one('standard.division', 'Division', required=True),
        
    }

    def assign_rollno(self, cr, uid, ids, context=None):
        res = {}
        student_obj = self.pool.get('school.standard')
        for student_data in self.browse(cr, uid, ids, context=context):
            domain = [('standard_id', '=', student_data.standard_id.id), ('medium_id' ,'=', student_data.medium_id.id), ('division_id', '=', student_data.division_id.id)]
            search_student_ids = student_obj.search(cr, uid, domain, context=context)
        number = 1
        for student in student_obj.browse(cr, uid, search_student_ids, context=context):
            student_obj.write(cr, uid, student.id, {'roll_no':number}, context=context)
            number = number + 1
        return res

# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4:
