# -*- coding: utf-8 -*-
from odoo import models, fields, api, exceptions, _
from datetime import date, datetime, timedelta
from datetime import datetime
from odoo import tools
from dateutil.relativedelta import relativedelta
import math


class PaymentPlanAnalysis(models.TransientModel):
    _name = "sale.order.payment.plan.analysis"

    date_to = fields.Date()
    payment_plan_selection = fields.Selection([
        ('normal', 'Payment Order Analysis'),
        ('intervals', 'Payment Order Analysis Intervals')],
        default='normal', string='Payment Analysis Selection',
        required=True)
    date_from = fields.Date(string='Reference Date')
    intervals = fields.Integer(default=7, string='Intervals')
    line_analysis_ids = fields.One2many('sale.order.payment.plan.analysis.details', 'line_analysis_id')

    @api.multi
    def analysis_upload(self):
        # Unlink in advance to be sure we'll only have 1 record to show
        self.env['sale.order.payment.plan.analysis.details'].search([]).unlink()

        context = ""
        orders = self.env['sale.order'].search([
            ('state', 'in', ['sale']),
            ('payment_plan_residual', '>', 0),
        ])
        payment_details = []
        for order in orders:
            for payment_plan in order.payment_plan_ids.filtered(lambda r: r.residual > 0.00):

                if self.date_from and payment_plan.date < self.date_from:
                    date_due = self.date_from
                elif self.date_to and payment_plan.date > self.date_to:
                    date_due = self.date_to
                else:
                    date_due = payment_plan.date
                context = 'date_due:month'

                # if report is needed based on date intervals
                date_from = datetime.strptime(self.date_from, tools.DEFAULT_SERVER_DATE_FORMAT)
                date_due2 = datetime.strptime(payment_plan.date, tools.DEFAULT_SERVER_DATE_FORMAT)
                days_diff = (date_due2 - date_from).days
                days = str(int(days_diff / self.intervals) * self.intervals).rjust(4, "0")

                payment_details.append((0, 0, {
                    'order_id': order.id,
                    'payment_plan_id': payment_plan.id,
                    'date_due': date_due,
                    'days': days,
                    'line_analysis_id': self.id
                }))

        self.update({'line_analysis_ids': payment_details})

        return {
            'name': _('Payment Analysis'),
            'views': [
                (self.env.ref('sbl_sale.payment_plan_analysis_pivot').id, 'pivot'),
            ],
            'type': 'ir.actions.act_window',
            'view_mode': 'pivot',
            'res_model': 'sale.order.payment.plan.analysis.details',
            'flags': {
                'action_buttons': False,
                'sidebar': False,
            },
            'context': {
                'pivot_column_groupby': [context],
            }
        }


class PaymentPlanAnalysisDetails(models.TransientModel):
    _name = "sale.order.payment.plan.analysis.details"
    _order = "days"

    order_id = fields.Many2one('sale.order', string='Order',
                               domain=[['state', 'in', ['draft', 'sent', 'sale']]],
                               store=True)
    payment_plan_id = fields.Many2one('sale.order.payment.plan', ondelete='cascade', string="Payment")
    line_analysis_id = fields.Many2one('sale.order.payment.plan.analysis', ondelete='cascade')
    name = fields.Char(related='order_id.name', store=True)
    residual = fields.Monetary(related='payment_plan_id.residual', ondelete='cascade', store=True)
    date_due = fields.Date(string='Due date', store=True)
    currency_id = fields.Many2one('res.currency',
                                  default=lambda self: self.env.user.company_id.currency_id.id)
    days = fields.Char(string='Interval')
