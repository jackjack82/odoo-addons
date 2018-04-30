# coding=utf-8

from odoo import models, fields, api, _
from odoo.exceptions import ValidationError


class SaleOrder(models.Model):
    _inherit = 'sale.order'

    payment_plan_ids = fields.One2many('sale.order.payment.plan', 'sale_order_id',
                                       string='Payment Plan', ondelete='cascade')
    payment_plan_amount = fields.Monetary(string='Payment Plan Amount', compute='_compute_payment_plan_amount')
    payment_plan_residual = fields.Monetary(string='Payment Plan Residual', compute='_compute_payment_plan_residual')

    payment_plan_amount_total = fields.Monetary(related='amount_total', readonly=True)

    @api.multi
    def write(self, vals):
        sale = super(SaleOrder,self).write(vals)
        if self.payment_plan_ids:
            if self.payment_plan_amount != self.amount_total and self.env.context.get('payment_plan_validation', True):
                raise ValidationError(_('Payment plan amount {} differ from Sale Order total amount {}'.format(self.payment_plan_amount, self.amount_total)))
        return sale

    @api.depends('payment_plan_ids.amount')
    def _compute_payment_plan_amount(self):
        for record in self:
            amount_total = 0.0
            if record.payment_plan_ids:
                for payment in record.payment_plan_ids:
                    amount_total += payment.amount
            record.payment_plan_amount = amount_total

    @api.depends('payment_plan_ids.residual')
    def _compute_payment_plan_residual(self):
        for record in self:
            residual_total = 0.0
            if record.payment_plan_ids:
                for payment in record.payment_plan_ids:
                    residual_total += payment.residual
            record.payment_plan_residual = residual_total

    def _compute_payment_plan_reconcile(self):
        for record in self:
            if record.payment_plan_ids:
                # we interested in emitted invoices and customer refund which are open and paid, for those
                # we calculate all the amount emitted that has to be reconciled over the payment plan
                total_residual = sum(record.invoice_ids.\
                                     filtered(lambda r: r.state in ['open', 'paid'] and r.type in ['out_invoice','out_refund']).\
                                     mapped(lambda r: r.amount_total if r.type == 'out_invoice' else -r.amount_total))
                # Loop over the payment plan sorted by date and update the residual
                for payment_plan in record.payment_plan_ids.sorted(key=lambda r: r.date):
                    if total_residual >= payment_plan.amount:
                        payment_plan.update({'residual': 0.0, 'reconciled': True})
                        total_residual -= payment_plan.amount
                    else:
                        payment_plan.update({'residual': payment_plan.amount - total_residual, 'reconciled': False})
                        total_residual = 0
