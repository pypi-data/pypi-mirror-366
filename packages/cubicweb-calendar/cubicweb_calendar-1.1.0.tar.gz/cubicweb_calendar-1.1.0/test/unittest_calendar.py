import unittest
from cubicweb_web.devtools.testlib import WebCWTC

from datetime import date, datetime

from cubicweb_calendar import (NON_WORKING as NW, WORKING as W,
                               WORKING_AM as WAM, WORKING_PM as WPM)


class DaytypeTests(WebCWTC):

    def setup_database(self):
        with self.admin_access.repo_cnx() as cnx:
            self.cal = cnx.find('Calendar', title=u"Calendrier Francais")[0][0]

    def tearDown(self):
        super(DaytypeTests, self).tearDown()
        # clear cache between each test
        self.vreg['etypes'].etype_class('Calendar').daytype_cache.clear()

    def _get_day_type(self, dt_type):
        # only the daytype's type attribute matters, pickup the first
        # matching daytype
        with self.admin_access.repo_cnx() as cnx:
            return cnx.execute('Any X WHERE X is Daytype, X type %(t)s',
                               {'t': dt_type}).get_entity(0, 0)

    def _get_day_types(self, caleid, firstday, lastday):
        with self.admin_access.repo_cnx() as cnx:
            cal = cnx.entity_from_eid(caleid)
            dtypes = []
            # 2010/07/12 is a monday, 16 in a sunday, 14 is national holiday
            for _, dtype_eid, _ in cal.get_days_type(firstday, lastday):
                dtype = cnx.entity_from_eid(dtype_eid)
                dtypes.append(dtype.type)
            return dtypes

    def test_daytype_french_calendar(self):
        # 2010/08/16 is a monday, 22 is a sunday
        dtypes = self._get_day_types(self.cal, date(2010, 8, 16),
                                     date(2010, 8, 22))
        self.assertEqual([W, W, W, W, W, NW, NW], dtypes)

    def test_daytype_holiday_french_calendar(self):
        with self.admin_access.repo_cnx() as cnx:
            cnx.create_entity('Recurrentday', day_month=u'07-14',
                              day_type=self._get_day_type(NW),
                              reverse_days=self.cal)
            cnx.commit()
            # 2010/07/12 is a monday, 16 is a sunday, 14 is a national holiday
            dtypes = self._get_day_types(self.cal, date(2010, 7, 12),
                                         date(2010, 7, 18))
            self.assertEqual([W, W, NW, W, W, NW, NW], dtypes)

    def test_daytype_timeperiod_two_days_french_calendar(self):
        with self.admin_access.repo_cnx() as cnx:
            cnx.create_entity('Timeperiod', start=datetime(2010, 8, 17, 0, 0),
                              stop=datetime(2010, 8, 18, 23, 59),
                              day_type=self._get_day_type(NW),
                              reverse_periods=self.cal)
            cnx.commit()  # trigger SetInitialStateOperation
            dtypes = self._get_day_types(self.cal, date(2010, 8, 16),
                                         date(2010, 8, 22))
            self.assertEqual([W, NW, NW, W, W, NW, NW], dtypes)

    def test_daytype_timeperiod_morning_french_calendar(self):
        with self.admin_access.repo_cnx() as cnx:
            cnx.create_entity('Timeperiod', start=datetime(2010, 8, 17, 0, 0),
                              stop=datetime(2010, 8, 17, 13, 00),
                              day_type=self._get_day_type(WPM),
                              reverse_periods=self.cal)
            cnx.commit()  # trigger SetInitialStateOperation
            dtypes = self._get_day_types(self.cal, date(2010, 8, 16),
                                         date(2010, 8, 22))
            self.assertEqual([W, WPM, W, W, W, NW, NW], dtypes)

    def test_daytype_timeperiod_afternoon_french_calendar(self):
        with self.admin_access.repo_cnx() as cnx:
            dtypes = []
            cnx.create_entity('Timeperiod', start=datetime(2010, 8, 17, 14, 0),
                              stop=datetime(2010, 8, 17, 23, 59),
                              day_type=self._get_day_type(WAM),
                              reverse_periods=self.cal)
            cnx.commit()  # trigger SetInitialStateOperation
            dtypes = self._get_day_types(self.cal, date(2010, 8, 16),
                                         date(2010, 8, 22))
            self.assertEqual([W, WAM, W, W, W, NW, NW], dtypes)

    def test_calendar_inheritance(self):
        with self.admin_access.repo_cnx() as cnx:
            cnx.create_entity('Recurrentday', day_month=u'07-14',
                              day_type=self._get_day_type(NW),
                              reverse_days=self.cal)
            friday_nw = cnx.create_entity('WeekDay', day_of_week=u'friday',
                                          day_type=self._get_day_type(NW))
            cal2 = cnx.create_entity('Calendar', title=u'cal2', inherits=self.cal,
                                     weekdays=friday_nw)
            cnx.commit()
            self.vreg['etypes'].etype_class('Calendar').daytype_cache.clear()
            dtypes = self._get_day_types(cal2.eid, date(2010, 7, 12),
                                         date(2010, 7, 18))
            self.assertEqual([W, W, NW, W, NW, NW, NW], dtypes)


class CalendarTemplatableTC(WebCWTC):
    def test_timeperiod_to_ical(self):
        with self.admin_access.repo_cnx() as cnx:
            day_type = cnx.execute(
                "Any X WHERE X is Daytype, X type %(t)s",
                {"t": W}
            ).one()
            cal = cnx.find("Calendar", title=u"Calendrier Francais").one()
            timeperiod = cnx.create_entity(
                "Timeperiod",
                start=datetime(2020, 3, 2, 8, 00),
                stop=datetime(2020, 3, 2, 18, 30),
                day_type=day_type,
                reverse_periods=cal,
            )
            cnx.commit()
        with self.admin_access.web_request(vid="ical", eid=timeperiod.eid) as req:
            data = self.ctrl_publish(req, "view").decode("utf-8")
            self.assertTrue(data.startswith("BEGIN:VCALENDAR"))
            self.assertIn("START:20200302T080000", data)
            self.assertIn("END:20200302T183000", data)


if __name__ == '__main__':
    unittest.main()
