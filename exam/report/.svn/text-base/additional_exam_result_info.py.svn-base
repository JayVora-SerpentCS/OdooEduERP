import time
from report import report_sxw

class additional_exam_result(report_sxw.rml_parse):
    def __init__(self, cr, uid, name, context=None):
        super(additional_exam_result, self).__init__(cr, uid, name, context=context)
        self.localcontext.update({
            'time': time,
        })

report_sxw.report_sxw('report.additional_exam_result', 'additional.exam.result', 'exam/report/add_exm_result_information_report.rml', parser=additional_exam_result, header="internal")
