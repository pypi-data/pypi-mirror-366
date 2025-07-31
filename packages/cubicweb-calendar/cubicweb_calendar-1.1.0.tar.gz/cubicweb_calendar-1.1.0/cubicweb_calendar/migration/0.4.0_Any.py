# -*- coding: utf-8 -*-
from cubicweb_calendar import WORKING, NON_WORKING, WORKING_AM, WORKING_PM

dt_titles = {
    u'working': (u'journée de travail', WORKING),
    u'non_working': (u'non travaillé', NON_WORKING),
    u'working_am':  (u'matinée de travail', WORKING_AM),
    u'working_pm': (u'après-midi de travail', WORKING_PM),
    u'maladie_matin': (u'malade le matin', WORKING_PM),
    u'maladie_apresmidi': (u"malade l'après-midi", WORKING_AM),
    u'maladie_journee': (u'malade la journée', NON_WORKING),
    u'conges_journee': (u'journée de congés', NON_WORKING),
    u'conges_matin': (u'matinée de congés', WORKING_PM),
    u'conges_apresmidi': (u'après-midi de congés', WORKING_AM),
    u'conges_mpaternite': (u'journée de mat-paternité', NON_WORKING),
    u'greve_journee': (u'journée de grève', NON_WORKING),
    }

missing_dt_titles = {u'matinée de grève': WORKING_PM,
                     u'après-midi de grève': WORKING_AM,
                     }

add_attribute('Daytype', 'type')
for daytype in rql('Any D, DT WHERE D is Daytype, D title DT').entities():
    try:
        new_dt_title, dt_type = dt_titles[daytype.title]
        daytype.cw_set(title=new_dt_title, type=dt_type)
    except KeyError:
        print "Oops, found an unknown daytype (%r) in the database" % daytype.title

drop_entity_type('Timespan')
