# -*- coding: utf-8 -*-
# Copyright 2017 Giacomo Grasso <giacomo.grasso.82@gmail.com>
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).
-

from openerp import models, fields


class AccountJournal(models.Model):
    _inherit = "account.journal"

    financial_planning = fields.Boolean(string="Financial Planning")
