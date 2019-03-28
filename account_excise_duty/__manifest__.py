# -*- coding: utf-8 -*-
# © 2019 Giacomo Grasso
# License GPL-3.0 or later (http://www.gnu.org/licenses/gpl.html).
{
    'name': 'Account Excise Duty',
    'version': '10.0.1.0.0',
    'category': 'Account',
    'summary': 'Account Excise Duty',
    'author': 'giacomo.grasso.82@gmail.com',
    'website': '',
    'license': 'AGPL-3',
    'depends': [
        'account',
        'product',
        ],
    'data': [
        'views/product.xml',
        'views/account_tax.xml',
    ],
    'installable': True,
}
