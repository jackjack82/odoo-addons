# -*- coding: utf-8 -*-

from odoo import models, fields, api


class AccountInvoice(models.Model):
    _inherit = "account.invoice"

    client_bank_account_id = fields.Many2one(
        comodel_name='res.partner.bank',
        string='Client account',
        help="Bank account of the client to be printed in sales invoice")

    @api.onchange('partner_id', 'company_id')
    def _onchange_partner_id(self):
        res = super(AccountInvoice, self)._onchange_partner_id()
        self.partner_bank_id = self.partner_id.company_bank_id

        return res
