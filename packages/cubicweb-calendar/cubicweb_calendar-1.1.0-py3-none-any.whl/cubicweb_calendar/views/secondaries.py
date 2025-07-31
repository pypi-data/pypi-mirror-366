from logilab.mtconverter import xml_escape

from cubicweb.predicates import is_instance
from cubicweb_web.views import baseviews

# out of context  ####################################################################


class RecurrentDayOutOfContext(baseviews.OutOfContextView):
    __select__ = is_instance('Recurrentday')

    def cell_call(self, row, col):
        entity = self.cw_rset.get_entity(row, col)
        self.w(u'<a href="%s">' % xml_escape(entity.absolute_url(vid='edition')))
        self.wdata(entity.dc_long_title())
        self.w(u'</a>')


class TimePeriodOutOfContext(baseviews.OutOfContextView):
    __select__ = is_instance('Timeperiod')

    def cell_call(self, row, col):
        entity = self.cw_rset.get_entity(row, col)
        self.w(u'<a href="%s">' % xml_escape(entity.absolute_url(vid='edition')))
        self.wdata(entity.dc_long_title())
        self.w(u'</a>')
