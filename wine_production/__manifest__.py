# -*- coding: utf-8 -*-

{
    'name': "Wine production",
    'summary': """ Testing wine production """,
    'description': """
        Wine production module
    """,
    'author': 'Herzog',
    'version': '10.0.0.1',
    'depends': [
        'base',
        'product',
        'mail',
        ],

    'data': [
        'views/menu.xml',
        'views/vineyards_tank.xml',
        'views/treatm_analysis.xml',
        'views/grape_wort.xml',
        'security/ir.model.access.csv',

        'reports/grape_report.xml',
        'reports/wort_report.xml',

        ],

    'installable': True,
    'auto_install': False,
    'application': True,
}
