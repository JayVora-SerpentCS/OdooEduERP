from openerp.osv import fields, osv


# import time
# import openerp
# from datetime import datetime
# from openerp.tools.translate import _
# from openerp.tools import DEFAULT_SERVER_DATE_FORMAT,
# DEFAULT_SERVER_DATETIME_FORMAT, image_colorize, image_resize_image_big
class school_standard(osv.Model):
    ''' Defining a standard related to school '''
    _inherit = 'school.standard'

    def _compute_student(self, cr, uid, ids, name, args, context=None):
        ''' This function will automatically computes the students
            related to particular standard.'''
        result = {}
        student_obj = self.pool.get('student.student')
        for standard_data in self.browse(cr, uid, ids, context=context):
            student_ids = student_obj.search(cr, uid, [('standard_id', '=',
                                                        standard_data.
                                                        standard_id.id)],
                                             context=context)
            result[standard_data.id] = student_ids
        return result

    _columns = {'student_ids': fields.function(_compute_student, method=True,
                                               relation='student.student',
                                               type="one2many",
                                               string='Student In Class'),
                }
