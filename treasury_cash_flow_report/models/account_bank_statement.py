# -*- coding: utf-8 -*-
# Copyright 2017 Giacomo Grasso <giacomo.grasso.82@gmail.com>
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).

import ast
import json
from odoo import models, fields, api
from . import dictionary_operations as dictop


class AccountBankStatementLine(models.Model):
    _inherit = 'account.bank.statement.line'

    cf_reconciled = fields.Boolean(string='Reconc.')
    counterpart_move_ids = fields.One2many(
        comodel_name='account.move.line',
        inverse_name='bank_statement_line_id',
        # compute='compute_counterpart_lines',
        store=True,
        string='Treasury Forecast')
    cf_share = fields.Text(
        compute='compute_counterpart_lines',
        store=True,
        string='CF reporting share',)

    @api.model
    def bank_compute_share_init(self):
        """Computing share at module installation, method called by data.xml."""
        statement_line_list = self.search([])
        for line in statement_line_list:
            line.compute_counterpart_lines()

    @api.multi
    @api.depends('journal_entry_ids.line_ids.matched_debit_ids',
                 'journal_entry_ids.line_ids.matched_credit_ids')
    def compute_counterpart_lines(self):
        """At line's reconciliation the cash flow share is computed based on
           the counterpart moves share (if reconciled with invoices) or from
           the account move's structure in case of simple reconciliation."""
        for item in self:
            move_debit_lines = []
            move_credit_lines = []

            # list of all the move lines of the payment's move
            line_list = []
            for entry in item.journal_entry_ids:
                for line in entry.line_ids:
                    if line.account_id.treasury_planning:
                        line_list.append(line)

            # for each line above collect all the reconciled counterpart lines
            for line in line_list:
                if line.credit > 0 and line.debit == 0:
                    for match in line.matched_debit_ids:
                        move_debit_lines.append(match.debit_move_id.id)

                if line.credit == 0 and line.debit > 0:
                    for match in line.matched_credit_ids:
                        move_credit_lines.append(match.credit_move_id.id)

            if move_credit_lines:
                counterpart_move_ids = move_credit_lines
            else:
                counterpart_move_ids = move_debit_lines

            # bank move share is transformed to dictionary
            bank_move_dict = (ast.literal_eval(item.cf_share) if
                              item.cf_share else {})

            # the share of each counterpart line is "merged or added"
            # in a weighted manner to the bank line share
            for cpt in counterpart_move_ids:
                dest_move_line = self.env['account.move.line'].browse(cpt)
                weight = round(dest_move_line.balance / item.amount, 2)
                # counterpart share is transformed into dictionary
                move_line_dict = ast.literal_eval(dest_move_line.cf_share)

                # each key is finally added to the bank line share
                for key, value in move_line_dict.iteritems():
                    draft_dictionary = dictop.sum_dictionary(
                        bank_move_dict.get(key, {}), 1,
                        move_line_dict.get(key, {}), weight)
                    bank_move_dict[key] = dictop.check_dict_total(
                        draft_dictionary, 1)

            # the dictionary is transformed into string and assigned
            item.cf_share = json.dumps(bank_move_dict)
