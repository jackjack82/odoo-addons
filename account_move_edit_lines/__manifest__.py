# coding: utf-8
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).

{
    'name': 'Account move edit lines',
    'version': '10.0.1.0.0',
    'category': 'Accounting',
    'summary': 'Edit lines in posted account moves',
    'author': "Giacomo Grasso",
    'license': 'AGPL-3',
    'depends': [
        'account',
        ],
    'data': [
        'data/account.xml',
        'wizard/wizard_edit_lines.xml',
    ],
    'installable': True,
}
