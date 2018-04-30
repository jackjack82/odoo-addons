# -*- coding: utf-8 -*-
{
    'name': "SBL Sale",
    'summary': """
            Add specific Sale extensions to SBL
        """,
    'description': """
            Add specific Sale extensions to SBL
        """,
    'author': "Levelprime srl",
    'website': "",
    'category': 'Utility',
    'version': '10.0.1.0',
    'depends': ['sale'],
    'data': [
        'views/sale_order.xml',
        'wizard/wizard_payment_plan.xml',
        'security/ir.model.access.csv',
    ],
    'installable': True,
    'application': False,
    'auto-install': False
}
