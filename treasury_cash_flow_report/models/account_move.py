# -*- coding: utf-8 -*-
# Copyright 2017 Giacomo Grasso <giacomo.grasso.82@gmail.com>
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).

import ast
from odoo import models, fields, api, _
from . import dictionary_operations as DICTOP


class AccountMoveLine(models.Model):
    """Move lines are now linked to a treasury forecast depending on the
       treasury date, and they inherit the cash flow share 1) from invoice
       or 2) from their account move structure"""
    _inherit = "account.move.line"

    cf_share = fields.Text(
        compute='_compute_accounting_share',
        store=True,
        string="CF share",)
    bank_statement_line_id = fields.Many2one(
        comodel_name='account.bank.statement.line',
        string='Bank statement line',
        store=True)

    @api.multi
    @api.depends('invoice_id', 'matched_credit_ids', 'matched_debit_ids')
    def _compute_accounting_share(self):
        """Computing cash flow share of move lines"""
        for mvl in self:
            # if move lines belongs to invoice, it is inherited
            if mvl.invoice_id and not mvl.statement_id:
                mvl.cf_share = mvl.invoice_id.cf_share
                mvl.cf_share = mvl.invoice_id.cf_share