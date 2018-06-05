# -*- coding: utf-8 -*-

from odoo import api, models,fields, _
from odoo.exceptions import UserError


class OrderAccounting(models.Model):
    _name = 'order.accounting'

    name = fields.Char('Name')
    cost_prov_acc_id = fields.Many2one(
        comodel_name="account.account",
        string='Cost provision account')
    debit_prov_acc_id = fields.Many2one(
        comodel_name="account.account",
        string='Debit provision account')
    journal_id = fields.Many2one(
        comodel_name="account.journal",
        string='Provision Journal')



