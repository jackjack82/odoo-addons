# -*- coding: utf-8 -*-

from odoo import models, fields, api
from datetime import timedelta


class FinancialForecast(models.Model):
    _name = 'financial.forecast'
    _order = "date_start desc"
    _description = "Financial Forecast"

    # General data
    name = fields.Char(string="Name", required=True)
    active = fields.Boolean("Active", default=True)
    statement_id = fields.Many2one(
        comodel_name="account.bank.statement",
        )
    state = fields.Selection([
        ('open', "Open"),
        ('closed', "Closed"),
        ], default='open')
    company_id = fields.Many2one(
        comodel_name='res.company',
        string='Company',
        required="True",
        default=lambda self: self.env.user.company_id,)
    date_start = fields.Date(string="Start Date", required=True)
    date_end = fields.Date(string="End Date", required=True)
    initial_balance = fields.Float(
        string='Initial balance',
        readonly=False,
        store=True)
    final_balance = fields.Float(
        string='Final balance',
        compute='compute_periodic_saldo',
        store=True,
        )
    previous_forecast_id = fields.Many2one(
        comodel_name='financial.forecast',
        string='Previous forecast')
    forecast_template_id = fields.Many2one(
        comodel_name='financial.forecast.template',
        string='Forecast Template')
    # overall values
    periodic_saldo = fields.Float(
        string='Periodic saldo', compute='compute_periodic_saldo', store=True)
    payables = fields.Float(
        string='Payables', compute='compute_periodic_saldo', store=True)
    receivables = fields.Float(
        string='Receivables', compute='compute_periodic_saldo', store=True)
    cost_revenues = fields.Float(
        string='Costs/revenues', compute='compute_periodic_saldo', store=True)

    # Payables and receivables
    receivable_ids = fields.One2many(
        comodel_name="account.move.line",
        inverse_name="forecast_id",
        domain=[('debit', '>', 0),
                ('journal_id.type', '!=', 'bank')],
        string="Receivables")
    payable_ids = fields.One2many(
        comodel_name="account.move.line",
        inverse_name="forecast_id",
        domain=[('credit', '>', 0),
                ('journal_id.type', '!=', 'bank')],
        string="Payables")
    recurrent_cost_ids = fields.One2many(
        comodel_name="account.bank.statement.line",
        inverse_name="financial_forecast_id",
        string="Cost/reveues",
        store=True)

    @api.onchange('previous_forecast_id')
    def _onchange_date_saldo(self):
        for item in self:
            if item.previous_forecast_id:
                date_draft = fields.Date.from_string(
                    item.previous_forecast_id.date_end) + timedelta(days=1)
                item.date_start = fields.Date.to_string(date_draft)
                item.date_end = item.date_start
                item.initial_balance = item.previous_forecast_id.final_balance
                item.final_balance = item.initial_balance + item.periodic_saldo

    @api.multi
    def compute_forecast_lines(self):
        for item in self:
            for cost in item.forecast_template_id.recurring_line_ids:
                date_draft = fields.Date.from_string(
                    item.date_start) + timedelta(days=cost.day)
                date = fields.Date.to_string(date_draft)
                values = {
                    'name': cost.name,
                    'ref': cost.ref,
                    'partner_id': cost.partner_id.id,
                    'financial_date': date,
                    'date': date,
                    'amount': cost.amount,
                    'from_forecast': True,
                    'financial_forecast_id': item.id,
                    'statement_id': item.forecast_template_id.bank_statement_id.id,
                }
                statement_line_obj = self.env['account.bank.statement.line']
                new_line = statement_line_obj.create(values)

    @api.depends('payable_ids', 'receivable_ids', 'recurrent_cost_ids')
    def compute_periodic_saldo(self):
        for item in self:
            periodic_debit = 0
            periodic_credit = 0
            others = 0
            for line in item.payable_ids:
                periodic_debit += line.balance
            for line in item.receivable_ids:
                periodic_credit += line.balance
            for line in item.recurrent_cost_ids:
                others += line.amount

            periodic_saldo = periodic_debit + periodic_credit + others
            item.periodic_saldo = periodic_saldo
            item.payables = periodic_debit
            item.receivables = periodic_credit
            item.cost_revenues = others
            item.final_balance = item.initial_balance + periodic_saldo

    @api.multi
    def compute_forecast_data(self):
        for item in self:
            # compute financial date of all account moves
            move_obj = self.env['account.move.line']
            move_list = move_obj.search([
                ('account_id.financial_planning', '=', True),
                ('date_maturity', '>=', item.date_start),
                ('date_maturity', '<=', item.date_end),
                ('financial_date', '=', False),
            ])
            for move in move_list:
                move.financial_date = move.date_maturity

            bank_line_obj = self.env['account.bank.statement.line']
            bank_line_list = bank_line_obj.search([
                ('date', '>=', item.date_start),
                ('date', '<=', item.date_end),
                ('financial_date', '=', False),
            ])
            for line in bank_line_list:
                line.financial_date = line.date

    @api.multi
    def update_forecast_balances(self):
        forecast_obj = self.env['financial.forecast']
        forecast_list = forecast_obj.search([], order="date_start")
        for forecast in forecast_list:
            if forecast.previous_forecast_id:
                forecast.initial_balance = forecast.previous_forecast_id.final_balance
