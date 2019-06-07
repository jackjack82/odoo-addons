# -*- coding: utf-8 -*-
# © 2019 Giacomo Grasso
# License GPL-3.0 or later (http://www.gnu.org/licenses/gpl.html).

{
    'name': 'Stock Landed Cost Average Price',
    'version': '10.0.1.0.0',
    'category': 'Stock',
    'summary': 'Integrate landed cost to average price methodology.',
    'author': 'OdooMinds.com',
    'website': 'www.odoominds.com',
    'license': 'AGPL-3',
    'depends': [
        'stock_landed_costs',
        ],
    'data': [
        'views/stock_landed_cost.xml',
    ],
    'installable': True,
}
