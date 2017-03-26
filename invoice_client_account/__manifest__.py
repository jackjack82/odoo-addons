# -*- coding: utf-8 -*-
##############################################################################
#
#    Author: "Giacomo Grasso - "
#
#    This program is free software: you can redistribute it and/or modify
#    it under the terms of the GNU Affero General Public License as published
#    by the Free Software Foundation, either version 3 of the License, or
#    (at your option) any later version.
#
#    This program is distributed in the hope that it will be useful,
#    but WITHOUT ANY WARRANTY; without even the implied warranty of
#    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#    GNU General Public License for more details.
#
#    You should have received a copy of the GNU Affero General Public License
#    along with this program.  If not, see <http://www.gnu.org/licenses/>.
#
##############################################################################
{
    'name': 'Invoice client account',
    'version': '10.0.1.0.0',
    'category': 'Accounting',
    'summary': 'Adding client bank account on invoice',
    'author': "Giacomo Grasso",
    'license': 'AGPL-3',
    'depends': ['account'],
    'data': [
        'views/account_invoice.xml',
        'views/res_partner.xml',
        'report/account_invoice.xml',
    ],
    'installable': True,
}
