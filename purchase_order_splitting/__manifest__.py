# coding: utf-8
# @author Giacomo Grasso <giacomo.grasso.82@gmail.com>

{
    'name': 'Purchase order line splitting',
    'version': '10.0.1.0.0',
    'category': 'Accounting',
    'summary': 'Splitting purchase order lines',
    'author': "Giacomo Grasso",
    'license': 'AGPL-3',
    'depends': [
        'account',
        'purchase',
        'sale',
        ],
    'data': [
        'views/purchase_order.xml',
    ],
    'installable': True,
}

