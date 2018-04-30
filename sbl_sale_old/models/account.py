# coding=utf-8

from odoo import models, fields, api


class AccountInvoice(models.Model):
    _inherit = "account.invoice"

    @api.multi
    def write(self, vals):
        ret = super(AccountInvoice, self).write(vals)

        if (self.type in ['out_invoice', 'out_refund'] and
                ('state' in vals or 'amount_total' in vals)):
            for order in self.mapped('invoice_line_ids.sale_line_ids.order_id'):
                order._compute_payment_plan_reconcile()

        return ret


class AccountPaymentTerm(models.Model):
    _inherit = "account.payment.term"

    model = fields.Selection([
        ('invoice', 'Invoice'),
        ('order', 'Order'),
    ], default='invoice')
