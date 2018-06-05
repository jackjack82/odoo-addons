# coding: utf-8
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).

{
    'name': 'Purchase order account move',
    'version': '10.0.1.0.0',
    'category': 'Accounting',
    'summary': 'Purchase order account move',
    'author': "Giacomo Grasso",
    'license': 'AGPL-3',
    'depends': [
        'account',
        'purchase',
        ],
    'data': [
        'views/purchase_order.xml',
        'views/order_accounting.xml',
    ],
    'installable': True,
}
