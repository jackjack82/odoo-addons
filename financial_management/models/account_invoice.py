# -*- coding: utf-8 -*-
# Copyright 2017 Giacomo Grasso <giacomo.grasso.82@gmail.com>
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).


from openerp import models, fields, api, _
from openerp.exceptions import Warning


class AccountInvoice(models.Model):
    _inherit = "account.invoice"

    financial_date = fields.Date(string="Planning date")
    financial_forecast_id = fields.Many2one(
        comodel_name='financial.forecast',
        string='Financial Forecast',
        # required=True,
        ondelete='restrict',
        help="Financial forecast in which the invoice is planned to be paid")

    @api.onchange('financial_date')
    def _compute_financial_forecast(self):
        for item in self:
            if item.financial_date:
                forecast_obj = self.env['financial.forecast']
                forecast_id = forecast_obj.search([
                    ('date_start', '<=', item.financial_date),
                    ('date_end', '>=', item.financial_date),
                    ('state', '=', 'open')])
                if forecast_id:
                    item.financial_forecast_id = forecast_id[0]
                else:
                    raise Warning(_("A Financial Forecast for this date has \
                    not been found or is closed. Please create one."))
