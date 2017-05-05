# -*- coding: utf-8 -*-

from odoo import models, fields


class AccountJournal(models.Model):
    _inherit = "account.journal"

    financial_planning = fields.Boolean(string="Financial Planning")
