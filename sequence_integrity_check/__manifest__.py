# coding: utf-8
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).

{
    'name': 'Sequence Integrity Check',
    'version': '10.0.1.0.0',
    'category': 'Accounting',
    'summary': 'Checking sequence integrity status',
    'author': "Giacomo Grasso",
    'license': 'AGPL-3',
    'depends': [
        'account',
        ],
    'data': [
        'views/sequence_integrity_check.xml',
    ],
    'installable': True,
}
