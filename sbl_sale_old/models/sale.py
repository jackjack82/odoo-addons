# coding=utf-8

from odoo import models, fields, api, _
from odoo.exceptions import ValidationError


class SaleOrder(models.Model):
    _inherit = 'sale.order'

    payment_plan_id = fields.Many2one(comodel_name='account.payment.term', string='Payment plan')
    payment_plan_ids = fields.One2many('sale.order.payment.plan', 'sale_order_id',
                                       string='Payment Plan', ondelete='cascade')
    payment_plan_amount = fields.Monetary(string='Payment Plan Amount', compute='_compute_payment_plan_amount')
    payment_plan_residual = fields.Monetary(string='Payment Plan Residual', compute='_compute_payment_plan_residual')

    @api.multi
    def write(self, vals):
        sale = super(SaleOrder, self).write(vals)
        if self.payment_plan_ids and not self._context.get('uncheck'):
            if self.payment_plan_amount != self.amount_total:
                raise ValidationError(_('Payment plan amount {} differ from Sale'
                                        ' Order total amount {}'.format(
                    self.payment_plan_amount, self.amount_total)))

        self._compute_payment_plan_reconcile()

        return sale

    @api.multi
    def compute_payment_deadlines(self):
        for order in self.with_context(uncheck=True):

            # remove existing payment terms
            terms_list = [(5, 0, {})]

            # creating new payment terms
            due_list = order.payment_plan_id.compute(
                order.amount_total, order.date_order)[0]

            for term in due_list:
                terms_list.append((0, 0, {
                    'date': term[0],
                    'amount': term[1],
                    'residual': term[1],
                    'payment_term_id': order.payment_term_id.id,
                    }))
            order.update({'payment_plan_ids': terms_list})

            # compute again the residual of each line
            order._compute_payment_plan_reconcile()

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
            if record.payment_plan_ids and record.invoice_ids:
                # we are interested in emitted invoices and customer refund which are open and paid, for those
                # we calculate all the amount emitted that has to be reconciled over the payment plan
                total_residual = sum(record.invoice_ids.filtered(
                    lambda r: r.state in ['open', 'paid'] and r.type in ['out_invoice', 'out_refund']).mapped(
                    lambda r: r.amount_total if r.type == 'out_invoice' else -r.amount_total))
                # Loop over the payment plan sorted by date and update the residual
                for payment_plan in record.payment_plan_ids.sorted(key=lambda r: r.date):
                    if total_residual >= payment_plan.amount:
                        payment_plan.update({'residual': 0.0, 'reconciled': True})
                        total_residual -= payment_plan.amount
                    else:
                        payment_plan.update({'residual': payment_plan.amount - total_residual, 'reconciled': False})
                        total_residual = 0
