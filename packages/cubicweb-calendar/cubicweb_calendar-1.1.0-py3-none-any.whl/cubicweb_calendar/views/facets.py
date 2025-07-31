from cubicweb.predicates import is_instance
from cubicweb_web.facet import RelationFacet


class TimeperiodCalendarFacet(RelationFacet):
    __regid__ = 'timeperiod-calendar-facet'
    __select__ = RelationFacet.__select__ & is_instance('Timeperiod',)
    rtype = 'periods'
    target_attr = 'title'
