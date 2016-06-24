# -*- coding: utf-8 -*-
# Part of Odoo. See LICENSE file for full copyright and licensing details.

import time
from datetime import datetime, timedelta
from dateutil.relativedelta import relativedelta
from openerp import pooler
from openerp.report.interface import report_rml
from openerp.report.interface import toxml
from openerp.report import report_sxw
from openerp.tools import ustr

one_day = relativedelta(days=1)
month2name = [0, 'January', 'February', 'March', 'April', 'May', 'June',
              'July', 'August', 'September', 'October', 'November', 'December']


def lengthmonth(year, month):
    if ((month == 2)
            and ((year % 4 == 0)
                 and ((year % 100 != 0)
                      or (year % 400 == 0)))):
        return 29
    return [0, 31, 28, 31, 30, 31, 30, 31, 31, 30, 31, 30, 31][month]


class ReportCustom(report_rml):

    def create_xml(self, cr, uid, ids, datas, context=None):
        obj_student = pooler.get_pool(cr.dbname).get('student.student')
        sheet_obj = pooler.get_pool(cr.dbname).get('attendance.sheet')
        if context is None:
            context = {}
        month = datetime(datas['form']['year'], datas['form']['month'], 1)
        # stu_ids = context.get('active_ids', [])
        stu_ids = datas['form']['stud_ids']
        user_xml = ['<month>%s</month>' % month2name[month.month],
                    '<year>%s</year>' % month.year]
        if stu_ids:
            for student in obj_student.read(cr, uid, stu_ids,
                                            ['name', 'standard_id']):
                days_xml = []
                user_repr = '''
                <user>
                  <name>%s</name>
                  %%s
                </user>
                ''' % (ustr(toxml(student['name'])))
                today, tomor = month, month + one_day

                while today.month == month.month:
                    day = today.day
                    domain = [('standard_id', '=', student['standard_id'][0]),
                              ('month_id', '=', today.month)]
                    sheet_ids = sheet_obj.search(cr, uid, domain,
                                                 context=context)

                    if not sheet_ids:
                        var = 'A'
                    else:
                        att_browse = sheet_obj.browse(cr, uid, sheet_ids,
                                                      context=context)
                        for attendance_sheet_data in att_browse:

                            for line in attendance_sheet_data.attendance_ids:

                                if line.name == student['name']:

                                    if day == 1:
                                        att = line.one
                                    elif day == 2:
                                        att = line.two
                                    elif day == 3:
                                        att = line.three
                                    elif day == 4:
                                        att = line.four
                                    elif day == 5:
                                        att = line.five
                                    elif day == 6:
                                        att = line.six
                                    elif day == 7:
                                        att = line.seven
                                    elif day == 8:
                                        att = line.eight
                                    elif day == 9:
                                        att = line.nine
                                    elif day == 10:
                                        att = line.ten
                                    elif day == 11:
                                        att = line.one_1
                                    elif day == 12:
                                        att = line.one_2
                                    elif day == 13:
                                        att = line.one_3
                                    elif day == 14:
                                        att = line.one_4
                                    elif day == 15:
                                        att = line.one_5
                                    elif day == 16:
                                        att = line.one_6
                                    elif day == 17:
                                        att = line.one_7
                                    elif day == 18:
                                        att = line.one_8
                                    elif day == 19:
                                        att = line.one_9
                                    elif day == 20:
                                        att = line.one_0
                                    elif day == 21:
                                        att = line.two_1
                                    elif day == 22:
                                        att = line.two_2
                                    elif day == 23:
                                        att = line.two_3
                                    elif day == 24:
                                        att = line.two_4
                                    elif day == 25:
                                        att = line.two_5
                                    elif day == 26:
                                        att = line.two_6
                                    elif day == 27:
                                        att = line.two_7
                                    elif day == 28:
                                        att = line.two_8
                                    elif day == 29:
                                        att = line.two_9
                                    elif day == 30:
                                        att = line.two_0
                                    else:
                                        att = line.three_1

                                    if att:
                                        var = 'P'
                                    else:
                                        var = 'A'

                    today_xml = '<day num="%s"><wh>%s</wh></day>'\
                                % ((today - month).days + 1, var)
                    dy = (today - month).days + 1
                    days_xml.append(today_xml)
                    today, tomor = tomor, tomor + one_day
                user_xml.append(user_repr % '\n'.join(days_xml))

        rpt_obj = pooler.get_pool(cr.dbname).get('student.student')
        rml_obj = report_sxw.rml_parse(cr, uid, rpt_obj._name, context)
        users_obj = pooler.get_pool(cr.dbname).get('res.users')
        header_xml = '''
        <header>
        <date>%s</date>
        <company>%s</company>
        </header>
        ''' % (str(rml_obj.formatLang(time.strftime("%Y-%m-%d"), date=True))
               + ' ' + str(time.strftime("%H:%M")),
               users_obj.browse(cr, uid, uid).company_id.name)

        first_date = str(month)
        som = datetime.strptime(first_date, '%Y-%m-%d %H:%M:%S')
        eom = som + timedelta(int(dy) - 1)
        day_diff = eom - som
        date_xml = []
        cell = 1
        date_xml.append('<days>')
        if day_diff.days >= 30:
            date_xml += ['<dayy number="%d" name="%s" cell="%d"/>' %
                         (x, som.replace(day=x).strftime('%a'),
                          x - som.day + 1)
                         for x in range(som.day,
                                        lengthmonth(som.year, som.month) + 1)]
        else:
            if day_diff.days >= (lengthmonth(som.year, som.month) - som.day):
                date_xml += ['<dayy number="%d" name="%s" cell="%d"/>' %
                             (x, som.replace(day=x).strftime('%a'),
                              x - som.day + 1)
                             for x in range(som.day,
                                            lengthmonth(som.year, som.month)
                                            + 1)]
            else:
                date_xml += ['<dayy number="%d" name="%s" cell="%d"/>' %
                             (x, som.replace(day=x).strftime('%a'),
                              x - som.day + 1)
                             for x in range(som.day, eom.day + 1)]
        cell = x - som.day + 1
        day_diff1 = day_diff.days - cell + 1
        width_dict = {}
        month_dict = {}
        i = 1
        j = 1
        year = som.year
        month = som.month
        month_dict[j] = som.strftime('%B')
        width_dict[j] = cell

        while day_diff1 > 0:
            if month + i <= 12:
                if day_diff1 > lengthmonth(year, i + month):
                    # Not on 30 else you have problems when
                    # entering 01-01-2009 for example
                    som1 = datetime.date(year, month + i, 1)
                    date_xml += ['<dayy number="%d" name="%s" cell="%d"/>' %
                                 (x, som1.replace(day=x).strftime('%a'),
                                  cell + x)
                                 for x in range(1,
                                                lengthmonth(year, i + month)
                                                + 1)]
                    i = i + 1
                    j = j + 1
                    month_dict[j] = som1.strftime('%B')
                    cell = cell + x
                    width_dict[j] = x
                else:
                    som1 = datetime.date(year, month + i, 1)
                    date_xml += ['<dayy number="%d" name="%s" cell="%d"/>' %
                                 (x, som1.replace(day=x).strftime('%a'),
                                  cell + x) for x in range(1, eom.day + 1)]
                    i = i + 1
                    j = j + 1
                    month_dict[j] = som1.strftime('%B')
                    cell = cell + x
                    width_dict[j] = x
                day_diff1 = day_diff1 - x
            else:
                years = year + 1
                year = years
                month = 0
                i = 1
                if day_diff1 >= 30:
                    som1 = datetime.date(years, i, 1)
                    date_xml += ['<dayy number="%d" name="%s" cell="%d"/>' %
                                 (x, som1.replace(day=x).strftime('%a'),
                                  cell + x)
                                 for x in range(1, lengthmonth(years, i) + 1)]
                    i = i + 1
                    j = j + 1
                    month_dict[j] = som1.strftime('%B')
                    cell = cell + x
                    width_dict[j] = x
                else:
                    som1 = datetime.date(years, i, 1)
                    i = i + 1
                    j = j + 1
                    month_dict[j] = som1.strftime('%B')
                    date_xml += ['<dayy number="%d" name="%s" cell="%d"/>' %
                                 (x, som1.replace(day=x).strftime('%a'),
                                  cell + x)
                                 for x in range(1, eom.day + 1)]
                    cell = cell + x
                    width_dict[j] = x
                day_diff1 = day_diff1 - x
        date_xml.append('</days>')
        date_xml.append('<cols>3.5cm%s</cols>\n' % (',0.74cm' * (int(dy))))
        xml = '''<?xml version="1.0" encoding="UTF-8" ?>
                 <report>
                 %s
                 %s
                 %s
                 </report>
              ''' % (header_xml, '\n'.join(user_xml), date_xml)
        return xml

ReportCustom('report.attendance.by.month.student', 'student.student', '',
             'addons/school_attendance/report/attendance_by_month.xsl')
