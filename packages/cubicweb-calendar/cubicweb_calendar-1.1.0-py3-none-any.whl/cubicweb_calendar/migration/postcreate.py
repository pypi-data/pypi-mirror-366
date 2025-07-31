# -*- coding: utf-8 -*-
# postcreate script. You could setup a workflow here for example

from cubicweb import _
from cubicweb_calendar import WORKING_AM, WORKING_PM, WORKING, NON_WORKING

## DAY TYPES
dt_definitions = {u'journée de congés': (NON_WORKING, True),
                  u'matinée de congés': (WORKING_PM, True),
                  u'après-midi de congés': (WORKING_AM, True),
                  u'journée de mat-paternité': (NON_WORKING, True),
                  u'malade la journée': (NON_WORKING, True),
                  u'malade le matin': (WORKING_PM, True),
                  u"malade l'après-midi": (WORKING_AM, True),
                  u'journée de grève': (NON_WORKING, False),
                  u'matinée de grève': (WORKING_PM, False),
                  u'après-midi de grève': (WORKING_AM, False),
                  u'journée de travail': (WORKING, False),
                  u'matinée de travail': (WORKING_AM, False),
                  u'après-midi de travail': (WORKING_PM, False),
                  u'non travaillé': (NON_WORKING, True),
                  }

dt_store = {}
for dt_title, (dt_type, display_in_user_request) in dt_definitions.items():
    dt_store[dt_title] = create_entity('Daytype', title=dt_title, type=dt_type,
                                       display_in_user_request=display_in_user_request)

weekdays = []
## WEEK DAYS
for day in (u'monday', u'tuesday', u'wednesday', u'thursday', u'friday'):
    weekdays.append(create_entity('WeekDay', day_of_week=day,
                                  day_type=dt_store[u'journée de travail']))

for day in (u'saturday', u'sunday'):
    weekdays.append(create_entity('WeekDay', day_of_week=day,
                                  day_type=dt_store[u'non travaillé']))

## DEFAULT CALENDAR
defaultcal = create_entity('Calendar', title=u'Calendrier Francais')
defaultcal.cw_set(weekdays=weekdays, day_types=list(dt_store.values()))

# Timeperiod workflow
wf = add_workflow('time-period workflow', 'Timeperiod')
tp_pending = wf.add_state(_('pending'), initial=True)
tp_validated  = wf.add_state(_('validated'))
wf.add_transition(_('validate'), tp_pending, tp_validated, ('managers',))
