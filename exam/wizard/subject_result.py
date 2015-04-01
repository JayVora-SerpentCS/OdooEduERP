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
from openerp import models, fields, api, _

class subject_result_wiz(models.TransientModel):
    
    _name= "subject.result.wiz"
    _description= "Subject Wise Result"
    
    result_ids = fields.Many2many("exam.subject",'subject_result_wiz_rel','result_id',"exam_id","Exam Subjects",select=1)
    
    @api.multi
    def result_report(self):
            data = self.read(self.ids)[0]
            
            datas = {
                     'ids': self._context.get('active_ids',[]),
                     'form': data,
                     'model':'exam.result',
            }
            return self.env['report'].get_action('exam.exam_result_report', data=data)
          # return {'type': 'ir.actions.report.xml', 'report_name': 'exam.exam_result_report', 'datas':datas }
    
# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4: