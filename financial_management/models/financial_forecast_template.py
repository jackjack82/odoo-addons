# -*- coding: utf-8 -*-

from openerp import models, fields, api, _


class FinancialPlanningTemplate(models.Model):
    _name = 'financial.forecast.template'
    _description = "Financial Planning Template"

    name = fields.Char(
        string="Template name",
        required=True)
    recurring_line_ids = fields.One2many(
        comodel_name="financial.forecast.line.template",
        inverse_name="financial_forecast_template_id",
        string="Recurring Line")
    bank_statement_id = fields.Many2one(
        comodel_name="account.bank.statement",
        string="Bank statement",
        help="Select the virtual bank statement to be used for financial\
             planning operations",)


class FinancialForecastLineTemplate(models.Model):
    _name = 'financial.forecast.line.template'
    _description = "Recurring Costs"

    name = fields.Char(string="Label", required=True)
    ref = fields.Char(string="Reference")
    day = fields.Integer(string="Day",
                         required=True,
                         default=0)
    partner_id = fields.Many2one(
        comodel_name="res.partner",
        string="Partner")
    journal_id = fields.Many2one(
        comodel_name="account.journal",
        string="Journal")
    amount = fields.Float(string="Amount")
    financial_forecast_template_id = fields.Many2one(
        "financial.forecast.template",
        string="Treasury Template")

    @api.constrains('amount')
    def checking_processing_value(self):
        for rec in self:
            if rec.amount == 0:
                raise Warning(_("Each line's amount can not be equal to 0"))
        return True
