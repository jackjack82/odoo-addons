# -*- coding: utf-8 -*-
# © 2019 Giacomo Grasso
# License GPL-3.0 or later (http://www.gnu.org/licenses/gpl.html).

from odoo import models, fields, api


class SaleOrder(models.Model):
    _inherit = "sale.order"

    client_bank_account_id = fields.Many2one(
        comodel_name='res.partner.bank',
        string='Client account',
        help="Bank account of the client to be printed in sales orders for, "
             "e.g., invoice advance with banks.")

    partner_bank_id = fields.Many2one(
        comodel_name='res.partner.bank',
        string='Company account',
        help="Bank account of the Company e.g. for client's advance payment")

    @api.onchange('partner_id', 'company_id')
    def onchange_partner_id(self):
        """
        Update this additional fields when the partner is changed:
        - Partner bank
        """
        res = super(SaleOrder, self).onchange_partner_id()
        self.partner_bank_id = self.partner_id.company_bank_id

        return res

    @api.multi
    def _prepare_invoice(self):
        res = super(SaleOrder, self)._prepare_invoice()
        res['client_bank_account_id'] = self.client_bank_account_id.id
        res['partner_bank_id'] = self.partner_bank_id.id

        return res
