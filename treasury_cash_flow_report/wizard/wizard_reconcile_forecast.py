# -*- coding: utf-8 -*-

from odoo import models, fields, api, _
import ast, json
from odoo.exceptions import UserError
from ..models import dictionary_operations as dictop


class BankStatementLineReconcileForecast(models.TransientModel):
    _name = 'bank.statement.line.reconcile.forecast'

    preview = fields.Text()

    @api.multi
    def _reconcile_lines(self, result):
        """ Reconciles the selected bank statement lines
        param:  if 'preview' the result is shown in the Text field,
                if 'reconcile' the lines are reconciled.
        resurn: preview or reconciliation, based on input parameter.
        """

        active_ids = self.env['account.bank.statement.line'].browse(
            self.env.context.get('active_ids', []))

        #ensure that there are not reconciled lines selected
        reconciled_lines = active_ids.filtered('cf_reconciled')
        if reconciled_lines:
            raise UserError(_("No reconciled lines shall be selected"))

        #ensure that there is only one forecast line in the reconciliation
        forecast_lines = active_ids.filtered('cf_forecast')
        if len(forecast_lines) != 1:
            raise UserError(_("Please chose one and only one forecast line"
                              " for each reconciliation."))
        else:
            forecast_line = forecast_lines[0]
            # forecast_line.cf_reconciled = True

        total_amount = 0
        result = {}

        # first, sum all the non-forecast lines's dictionaries
        for line in active_ids.filtered(lambda r: r.cf_forecast != True):
            weight = round(forecast_line.amount/line.amount, 2)
            line_dict = ast.literal_eval(line.cf_share  or '{}')
            # computing dictionaries
            for key, value in line_dict.iteritems():
                result_draft = dictop.sum_dictionary(
                    result.get(key, {}), 1,
                    line_dict.get(key, {}), weight)
                # the final dictionary is checked and eventually "completed" to
                # have the sum of all shares equal to 1
                result[key] = dictop.check_dict_total(result_draft, 1)

            total_amount += line.amount
            #line.cf_reconciled = True

        #second, subtract the obtained dictionary with the forecasted lines
        forecast_share = ast.literal_eval(forecast_line.cf_share or '{}')
        final = {}
        weight = round(total_amount/forecast_line.amount ,2)
        for key, value in result.iteritems():
            final_draft = dictop.subtract_dictionary(
                result.get(key, {}), weight,
                forecast_share.get(key, {}), 1)
            # because it is a subraction, the sum of all shares shall be 0
            final[key] = dictop.check_dict_total(final_draft, 1)

        forecast_line.amount -= total_amount
        forecast_line.cf_share = json.dumps(final)

    @api.multi
    def button_reconciliation_preview(self):
        """ Provides a preview of the reconciliation result """
        self._reconcile_lines('preview')
        return {"type": "ir.actions.do_nothing"}

    @api.multi
    def button_reconcile_lines(self):
        """ Reconciles the selected lines"""
        self._reconcile_lines('reconcile')
        return {"type": "ir.actions.act_window_close"}
