# coding: utf-8
#   @author Giacom Grassso <giacomo.grasso.82@gmail.com>
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).
{
    'name': 'Sale order invoiced amount',
    'version': '10.0.1.0.0',
    'category': 'Sale',
    'summary': 'Showing on sale order the amount invoiced',
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
