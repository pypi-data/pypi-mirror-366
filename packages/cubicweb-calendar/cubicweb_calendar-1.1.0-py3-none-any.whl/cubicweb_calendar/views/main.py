from datetime import timedelta, date as pydate

from logilab.mtconverter import xml_escape
from logilab.common.date import (date_range, first_day,
                                 previous_month, next_month)

from cubicweb_web.view import EntityView
from cubicweb.predicates import is_instance

from cubicweb_calendar import NON_WORKING, WORKING, WORKING_AM, WORKING_PM
from cubicweb_calendar.views import get_date_range_from_reqform

CALENDARS_PAGE = u"""<table class="bigCalendars">
<tr><td class="calendar">%s</td></tr>
</table>
"""


class EuserCalendar(EntityView):
    __select__ = is_instance('Calendar',)
    __regid__ = 'user_calendar'

    def cell_call(self, row, col):
        self._cw.add_css('cubes.calendar.css')
        entity = self.cw_rset.get_entity(row, col)
        firstday, lastday = get_date_range_from_reqform(self._cw.form,
                                                        autoset_lastday=True)
        firstday = first_day(firstday)
        # make calendar
        caption = '%s %s' % (self._cw._(firstday.strftime('%B').lower()), firstday.year)
        prevurl, nexturl = self._prevnext_links(entity, firstday)
        prevlink = '<a href="%s">&lt;&lt;</a>' % xml_escape(prevurl)
        nextlink = '<a href="%s">&gt;&gt;</a>' % xml_escape(nexturl)
        self.w(u'<table id="ctid%s" class="userCal">'
               u'<tr><th class="prev">%s</th>'
               u'<th class="calTitle" colspan="6"><span>%s</span></th>'
               u'<th class="next">%s</th></tr>'
               u'<tr><th>&nbsp;</th><th>L</th><th>M</th><th>M</th><th>J</th><th>V</th><th>S</th><th>D</th></tr>'
               % (entity.eid, prevlink, caption, nextlink))
        start = firstday - timedelta(firstday.weekday())
        # upper bound excluded by date_range, hence the 7
        stop = lastday + timedelta(7 - lastday.weekday())
        celldatas = {}
        for date, dtype_eid, state in entity.get_days_type(firstday, lastday):
            dtype = self._cw.entity_from_eid(dtype_eid)
            celldatas[date] = (dtype, state)
        # build cells
        for curdate in date_range(start, stop):
            if curdate == start or curdate.weekday() == 0:  # sunday
                self.w(u'<tr>')
                self.w(u'<td class="week">%s<br/> %d</td>' % (self._cw._('week'), curdate.isocalendar()[1]))
            self._build_calendar_cell(curdate, celldatas, firstday)
            if curdate.weekday() == 6:
                self.w(u'</tr>')
        self.w(u'</table>')

    def _prevnext_links(self, entity, curdate):
        prevdate = previous_month(curdate)
        nextdate = next_month(curdate)
        rql = 'Any X WHERE X eid %s' % entity.eid
        prevlink = self._cw.ajax_replace_url('ctid%s' % entity.eid, rql=rql,
                                             vid='user_calendar', replacemode='swap',
                                             firstday=prevdate.strftime('%Y%m01'))
        nextlink = self._cw.ajax_replace_url('ctid%s' % entity.eid, rql=rql,
                                             vid='user_calendar', replacemode='swap',
                                             firstday=nextdate.strftime('%Y%m01'))
        return prevlink, nextlink

    def _build_calendar_cell(self, curdate, celldatas, firstday):
        if curdate.month != firstday.month:
            self.w(u'<td class="outofrange"></td>')
        else:
            daytype, daytype_state = celldatas[curdate]
            stickers = self._cw._(daytype.type)

            klasses = []
            am_sticker = u''
            pm_sticker = u''
            _today = pydate.today()
            pending_suffix = '_pending' if daytype_state == 'pending' else ''
            if curdate == _today:
                klasses.append(u'today')
            if daytype.type in (WORKING, NON_WORKING):
                klasses.append(daytype.type + pending_suffix)
                am_sticker = daytype.title
                pm_sticker = daytype.title
            elif daytype.type == WORKING_AM:
                klasses.append(daytype.type + pending_suffix)
                am_sticker = self._cw._(WORKING_AM)
                pm_sticker = daytype.title
            elif daytype.type == WORKING_PM:
                klasses.append(daytype.type + pending_suffix)
                am_sticker = daytype.title
                pm_sticker = self._cw._(WORKING_PM)
            else:
                self.error('Unknown daytype class')
            am_cell = (
                '<tr><td class="am"><div class="mday">am</div>'
                '<div class="stickers">%s</div></td></tr>\n'
            ) % am_sticker
            pm_cell = (
                '<tr><td class="pm"><div class="mday">pm</div>'
                '<div class="stickers">%s</div></td></tr>\n'
            ) % pm_sticker
            cellcontent = u'<table class="caldata">'
            cellcontent += '<tr><td class="caldate">%s</td></tr>%s %s</table>' % (curdate.day,  am_cell, pm_cell)
            self.w(u'<td class="%s" title="%s">%s</td>' % (' '.join(klasses), xml_escape(stickers),  cellcontent))


class TimeperiodCalendarItemView(EntityView):
    __regid__ = 'calendaritem'
    __select__ = is_instance('Timeperiod',)

    def cell_call(self, row, col):
        entity = self.cw_rset.complete_entity(row, col)
        day_types = u' '.join(self._cw._(dt.type) for dt in entity.day_type)
        state = entity.cw_adapt_to('IWorkflowable').printable_state
        self.w(xml_escape(u'%s : %s (%s)' % (entity.from_calendar.title,
                                             day_types, state)))
