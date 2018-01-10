# -*- coding: utf-8 -*-
# Copyright 2017 Giacomo Grasso <giacomo.grasso.82@gmail.com>
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).


{
    'name': 'Treasury Management',
    'version': '10.0.1.0',
    'description': """
            Addding treasury management features Odoo
        """,
    'author': 'Giacomo Grasso - giacomo.grasso.82@gmail.com',
    'maintainer': '',
    'website': '',
    'depends': [
        'account',
        'account_accountant',
        'base',
        ],
    'data': [
        'data/data.xml',

        'views/account_bank_statement.xml',
        'views/account_invoice.xml',
        'views/account_move.xml',

        'report/cash_flow_report.xml',
     ],
    'installable': True,
    'auto_install': False,
}
