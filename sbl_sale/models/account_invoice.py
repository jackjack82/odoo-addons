# coding=utf-8

from odoo import models, api


class AccountInvoice(models.Model):
    _inherit = "account.invoice"

    @api.multi
    def write(self, values):
        ret = super(AccountInvoice,self).write(values)

        if self.type in ['out_invoice','out_refund'] and ('state' in values or 'amount_total' in values):
            for order in self.mapped('invoice_line_ids.sale_line_ids.order_id'):
                order._compute_payment_plan_reconcile()

        return ret