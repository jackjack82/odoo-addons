# -*- coding: utf-8 -*-

from openerp import models, fields, api, _
from openerp.exceptions import Warning


class AccountMoveLine(models.Model):
    _inherit = "account.move.line"

    financial_planning = fields.Boolean(
        related='account_id.financial_planning',
        string='Financial Planning')
    financial_date = fields.Date(string='Financial Date')
    forecast_id = fields.Many2one(
        comodel_name='financial.forecast',
        compute='_compute_financial_forecast',
        store=True,
        ondelete='restrict',
        string='Financial Forecast')

    """At move line creation, the financial date is equal to the due date"""
    @api.model
    def create(self, vals):
        item = super(AccountMoveLine, self).create(vals)
        item.financial_date = item.date_maturity
        return item

    """ The move line is associated to the financial forecast
        depending on the financial date"""
    @api.depends('financial_date')
    def _compute_financial_forecast(self):
        for item in self:
            if item.financial_date and item.account_id.financial_planning:
                forecast_obj = self.env['financial.forecast']
                forecast_id = forecast_obj.search([
                    ('date_start', '<=', item.financial_date),
                    ('date_end', '>=', item.financial_date),
                    ('state', '=', 'open')])
                if not forecast_id:
                    raise Warning(_("A Financial Forecast for this date has \
                    not been found or is closed. Please create one."))
                item.forecast_id = forecast_id[0].id
