# -*- coding: utf-8 -*-

from openerp import models, fields, api


class ResPartner(models.Model):
    _inherit = 'res.partner'

    @api.model
    def _get_company_account(self):
        company_id = self._context.get(
            'company_id',
            self.env.user.company_id.id)
        return [('partner_id', '=', company_id)]

    company_bank_id = fields.Many2one(
        comodel_name='res.partner.bank',
        company_dependent=True,
        domain=_get_company_account,
        help="Company bank account to be set in sale invoices to this partner",
        string='Company account')
