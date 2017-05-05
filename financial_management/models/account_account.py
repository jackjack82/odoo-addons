# -*- coding: utf-8 -*-

from odoo import models, fields


class AccountAccount(models.Model):
    _inherit = "account.account"

    financial_planning = fields.Boolean(string="Financial Planning")
