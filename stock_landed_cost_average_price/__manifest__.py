# -*- coding: utf-8 -*-
# © 2019 Giacomo Grasso
# License GPL-3.0 or later (http://www.gnu.org/licenses/gpl.html).

{
    'name': 'Invoice and order bank accounts',
    'version': '10.0.1.0.0',
    'category': 'Accounting',
    'summary': 'Adding client and company bank account on invoices and sale order',
    'author': 'OdooMinds.com',
    'website': 'www.odoominds.com',
    'license': 'AGPL-3',
    'depends': [
        'stock_landed_costs',
        ],
    'data': [
        'views/stock_landed_cost.xml',
        'views/product_category.xml',
    ],
    'installable': True,
}
