# coding: utf-8
# @author Giacomo Grasso <giacomo.grasso.82@gmail.com>

{
    'name': 'Sale order line splitting',
    'version': '10.0.1.0.0',
    'category': 'Accounting',
    'summary': 'Splitting sale order lines',
    'author': "Giacomo Grasso",
    'license': 'AGPL-3',
    'depends': [
        'account',
        'purchase',
        'sale',
        ],
    'data': [
        'views/product_template.xml',
        'views/sale_order.xml',
        'wizard/sale_advance_payment_inv.xml',
    ],
    'installable': True,
}

