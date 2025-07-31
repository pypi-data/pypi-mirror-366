from random import randint
from datetime import timedelta

from cubicweb.devtools.fill import ValueGenerator
from cubicweb_web.devtools.testlib import AutomaticWebTest


class MyValueGenerator(ValueGenerator):
    def generate_Calendaruse_stop(self, entity, index):
        return entity.start + timedelta(days=randint(1, 10))
    generate_Timeperiod_stop = generate_Calendaruse_stop


class AutomaticWebTest(AutomaticWebTest):
    no_auto_populate = ('Daytype', 'WeekDay', 'Calendar', 'Calendaruse')
    ignored_relations = set(('use_calendar',))

    def to_test_etypes(self):
        return set(('Calendar', 'Calendaruse', 'Daytype',
                    'Timeperiod', 'WeekDay', 'Recurrentday',
                    'CWUser'))

    def list_startup_views(self):
        return ()


if __name__ == '__main__':
    import unittest
    unittest.main()
