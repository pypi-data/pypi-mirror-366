from cubicweb import _
from cubicweb.predicates import is_instance
from cubicweb_web.views import primary
from cubicweb.uilib import toggle_link

# calendar  ######################################################################


class PrimaryCalendar(primary.PrimaryView):
    __select__ = is_instance('Calendar')

    def render_entity_attributes(self, entity):
        entity.view('user_calendar', w=self.w)
        self._show_periods(entity)
        self._show_recurrent_days(entity)
        self._show_week_days(entity)
        self._show_day_types(entity)
        self._show_children(entity)

    def _show_periods(self, calendar):
        items = calendar.related('periods')
        title = u'%s (%i)' % (_(u'Periods'), len(items))
        self.w(u'<h2 class="cal_properties">%s</h2>\n' %
               toggle_link('cal_pd', title))
        self.wview('list', items, 'null', klass='hidden', listid='cal_pd')

    def _show_recurrent_days(self, calendar):
        items = calendar.related('days')
        title = u'%s (%i)' % (_(u'Recurrent days'), len(items))
        self.w(u'<h2 class="cal_properties">%s</h2>\n' %
               toggle_link('cal_rd', title))
        self.wview('list', items, 'null', klass='hidden', listid='cal_rd')

    def _show_week_days(self, calendar):
        items = calendar.related('weekdays')
        title = u'%s (%i)' % (_(u'Week days'), len(items))
        self.w(u'<h2 class="cal_properties">%s</h2>\n' %
               toggle_link('cal_wd', title))
        self.wview('list', items, 'null', klass='hidden', listid='cal_wd')

    def _show_day_types(self, calendar):
        items = calendar.related('day_types')
        title = u'%s (%i)' % (_(u'Day types'), len(items))
        self.w(u'<h2 class="cal_properties">%s</h2>\n' %
               toggle_link('cal_dt', title))
        self.wview('list', items, 'null', klass='hidden', listid='cal_dt')

    def _show_children(self, calendar):
        items = calendar.related('inherits', 'object')
        title = u'%s (%i)' % (_(u'inherits_object'), len(items))
        self.w(u'<h2 class="cal_properties">%s</h2>\n' %
               toggle_link('cal_ch', title))
        self.wview('list', items, 'null', klass='hidden', listid='cal_ch')
