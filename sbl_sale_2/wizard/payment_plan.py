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
    payment_plan_selection = fields.Selection([('payment_order_analysis', 'Payment Order Analysis'), (
        'payment_order_analysis_intervals', 'Payment Order Analysis Intervals')],
                                              default='payment_order_analysis', string='Payment Analysis Selection',
                                              required=True)
    date_from = fields.Date(string='Reference Date')
    intervals = fields.Integer(default=0, string='Intervals')
    line_analysis_ids = fields.One2many('sale.order.payment.plan.analysis.details', 'line_analysis_id')

    @api.multi
    def analysis_upload(self):
        # Unlink in advance to be sure we'll only have 1 record to show
        self.env['sale.order.payment.plan.analysis.details'].search([]).unlink()

        orders = self.env['sale.order'].search(
            [('confirmation_date', '>=', self.date_from), ('confirmation_date', '<=', self.date_to)])
        for order in orders:
            for payment_plan in order.payment_plan_ids.filtered(lambda r: r.residual > 0.00):
                if payment_plan.date <= self.date_from:
                    self.update({'line_analysis_ids': [(0, 0, {
                        'order_id': order.id,
                        'payment_plan_id': payment_plan.id,
                        'date_due': self.date_from,
                        'line_analysis_id': self.id
                    })]})
                else:

                    self.update({'line_analysis_ids': [(0, 0, {
                        'order_id': order.id,
                        'payment_plan_id': payment_plan.id,
                        'date_due': payment_plan.date,
                        'line_analysis_id': self.id
                    })]})

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
            }
        }

    @api.multi
    def upload_intervals(self):
        self.env['sale.order.payment.plan.analysis.details'].search([]).unlink()

        orders = self.env['sale.order'].search(
            [('confirmation_date', '>=', self.date_from), ('confirmation_date', '<=', self.date_to)])
        for order in orders:
            for payment_plan in order.payment_plan_ids:
                if payment_plan.date >= self.date_from and payment_plan.residual > 0.00:
                    date_from = datetime.strptime(self.date_from, tools.DEFAULT_SERVER_DATE_FORMAT)
                    date_due = datetime.strptime(payment_plan.date, tools.DEFAULT_SERVER_DATE_FORMAT)
                    daysDiff = (date_due - date_from).days
                    days = float(daysDiff) / float(self.intervals)
                    days_round = math.ceil(days) * 15
                    self.update({'line_analysis_ids': [(0, 0, {
                        'order_id': order.id,
                        'days': days_round,
                        'payment_plan_id': payment_plan.id,
                        'line_analysis_id': self.id
                    })]})

        return {
            'name': _('Payment Analysis Intervals'),
            'views': [
                (self.env.ref('sbl_sale.payment_plan_analysis_intervals_pivot').id, 'pivot'),
            ],
            'type': 'ir.actions.act_window',
            'view_mode': 'pivot',
            'res_model': 'sale.order.payment.plan.analysis.details',
            'flags': {
                'action_buttons': False,
                'sidebar': False,
            }
        }


class PaymentPlanAnalysisDetails(models.TransientModel):
    _name = "sale.order.payment.plan.analysis.details"

    order_id = fields.Many2one('sale.order', string='Order',
                               domain=[['state', 'in', ['draft', 'sent', 'sale']]],
                               store=True)
    payment_plan_id = fields.Many2one('sale.order.payment.plan', ondelete='cascade', string="Payment")
    line_analysis_id = fields.Many2one('sale.order.payment.plan.analysis', ondelete='cascade')
    name = fields.Char(related='order_id.name', store=True)
    residual = fields.Monetary(related='payment_plan_id.residual', ondelete='cascade', store=True)
    date_due = fields.Date()
    currency_id = fields.Many2one('res.currency',
                                  default=lambda self: self.env.user.company_id.currency_id.id)
    days = fields.Integer()
