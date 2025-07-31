# coding: utf-8
add_attribute('Daytype', 'display_in_user_request')
rql('SET X display_in_user_request TRUE WHERE X is Daytype, (X title LIKE "%congés%" OR X title LIKE "%maladie%" OR X title LIKE "%paternité%" OR X title LIKE "%maternité%")')
commit()
