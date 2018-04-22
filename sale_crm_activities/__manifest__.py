# -*- coding: utf-8 -*-
# © 2017 Giacomo Grasso
# License GPL-3.0 or later (http://www.gnu.org/licenses/gpl.html).
{
    'name': 'Sale CRM improvements',
    'version': '10.0.1.0.0',
    'category': 'Sale',
    'summary': 'Small improvements to CRM workflow',
    'author': 'giacomo.grasso.82@gmail.com',
    'website': '',
    'license': 'AGPL-3',
    'depends': [
        'sale',
        'calendar',
        'crm'],
    'data': [
        'views/calendar_event.xml',
        'wizard/wizard_mass_edit.xml',
    ],
    'installable': True,
}
