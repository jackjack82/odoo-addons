# coding: utf-8
#   @author Giacomo Grasso <giacomo.grasso.82@gmail.com>
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).

from odoo import models, fields, api


class AccountInvoice(models.Model):
    _inherit = "account.invoice"

    """
    When an invoice is edited, the related sale orders indicators are updated
    """

    @api.one
    @api.depends(
        'state', 'currency_id', 'invoice_line_ids.price_subtotal',
        'move_id.line_ids.amount_residual',
        'move_id.line_ids.currency_id')
    def _compute_residual(self):
        res = super(AccountInvoice, self)._compute_residual()

        sale_orders = self.mapped('invoice_line_ids.sale_line_ids.order_id')
        for order in sale_orders:
            amount_paid, amount_unpaid = order._get_order_paid_amount()

            order.write({
                'order_amount_paid': amount_paid,
                'order_amount_to_pay': order.amount_total - amount_paid,
            })

        return res
