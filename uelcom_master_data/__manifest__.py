# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).
{
    'name': 'Uelcom master data',
    'version': '12.0.1.0.0',
    'category': 'Sale',
    'summary': 'Master data for the Uelcom project',
    'description': 'Master data for the Uelcom project',
    'author': "Giacomo Grasso",
    'maintainer': 'Giacomo Grasso - giacomo.grasso.82@gmail.com',
    'license': 'AGPL-3',
    'depends': [
        'base',
        'account',
        ],
    'data': [
        'views/res_partner.xml',
        'views/fidelity_transaction.xml',
        'views/fidelity_voucher.xml',
        'wizard/views.xml',

        'security/ir.model.access.csv',
    ],
    'installable': True,
    'auto_install': False,
}
