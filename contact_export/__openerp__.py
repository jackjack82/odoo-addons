# -*- coding: utf-8 -*-
##############################################################################
#
##############################################################################

{
    'name': "Export partners",
    'summary': """Partners export""",
    'description': """
        Partners export
    """,
    'version': '8.0.1.1',
    'depends': [
        'base',
        'sale',
    ],
    'data': [
        'views/export_partner_data.xml'
    ],

    'installable': True,
    'auto_install': False,
    'application': True,
}
