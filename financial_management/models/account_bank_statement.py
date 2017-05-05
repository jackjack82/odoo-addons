# -*- coding: utf-8 -*-

from odoo import models, fields, api, _
from odoo.exceptions import Warning


class AccountBankStatementLine(models.Model):
    _inherit = 'account.bank.statement.line'

    financial_date = fields.Date("Financial Date")
    from_forecast = fields.Boolean('From forecast')
    financial_forecast_id = fields.Many2one(
        comodel_name="financial.forecast",
        compute='_compute_financial_forecast',
        store=True,
        ondelete='restrict',
        string="Financial Forecast")

    @api.model
    def create(self, vals):
        item = super(AccountBankStatementLine, self).create(vals)
        if not item.from_forecast:
            item._compute_financial_date()
        return item

    @api.onchange('date')
    def _compute_financial_date(self):
        for item in self:
            item.financial_date = item.date if item.date else ""

    @api.depends('financial_date')
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
