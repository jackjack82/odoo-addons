# -*- coding: utf-8 -*-
# Copyright 2017 Giacomo Grasso <giacomo.grasso.82@gmail.com>
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).

from odoo import models, fields, api, _
from collections import Counter
import json


class AccountInvoice(models.Model):
    _inherit = "account.invoice"

    cf_share = fields.Text(string="CF reporting share")

    @api.multi
    def write(self, vals):
        """Cash flow share on invoice is computed at each invoice edit"""
        item = super(AccountInvoice, self).write(vals)
        for invoice in self:
            invoice.invoice_compute_share()
        return item

    @api.multi
    def invoice_compute_share(self):
        """Computes the cash flow share from invoice lines based on COA
        account and analytic account.
        Note that the share is computed on line values NET of taxes."""
        coa_share = {}
        aa_share = {}
        for line in self.invoice_line_ids:
            line_share = round(line.price_subtotal / self.amount_untaxed, 2)
            if str(line.account_id.id) not in coa_share:
                coa_share[str(line.account_id.id) or ''] = line_share
            else:
                coa_share[str(line.account_id.id) or ''] += line_share
            if str(line.account_analytic_id.id) not in aa_share:
                aa_share[str(line.account_analytic_id.id or '')] = line_share
            else:
                aa_share[str(line.account_analytic_id.id or '')] += line_share
        cf_share = """{"coa_share": %s, "aa_share": %s }""" % (
            json.dumps(coa_share), json.dumps(aa_share))

        # the cash flow share field is edited using SQL
        # to avoid recursion with overriding "write"
        self.env.cr.execute("""
            UPDATE account_invoice
            SET cf_share = '%s'
            WHERE id = %d;
            """ % (cf_share, self.id))

    @api.model
    def invoice_compute_share_init(self):
        """Computing cash flow share of invoices at module installation"""
        invoice_list = self.search([])
        for invoice in invoice_list:
            invoice.invoice_compute_share()
