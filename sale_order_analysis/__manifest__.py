# coding: utf-8
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).
{
    'name': 'Sale order analysis',
    'version': '10.0.1.0.0',
    'category': 'Sale',
    'summary': 'Showing on sale order invoiced and paid amount',
    'author': "Giacomo Grasso",
    'license': 'AGPL-3',
    'depends': [
        'sale',
        'account',
        ],
    'data': [
        'views/sale_order.xml',
    ],
    'installable': True,
}
