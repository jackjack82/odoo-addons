# coding: utf-8
# @author Giacomo Grasso <giacomo.grasso.82@gmail.com>

{
    'name': 'Order line splitting',
    'version': '10.0.1.0.0',
    'category': 'Accounting',
    'summary': 'Splitting sale and purchase order lines',
    'author': "Giacomo Grasso",
    'license': 'AGPL-3',
    'depends': [
        'account',
        'purchase',
        'sale',
        ],
    'data': [
        'views/sale_order.xml',
        'views/purchase_order.xml',
        'wizard/sale_advance_payment_inv.xml',
    ],
    'installable': True,
}

