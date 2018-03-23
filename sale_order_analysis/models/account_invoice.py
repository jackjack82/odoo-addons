# coding: utf-8
#   @author Giacom Grasso <giacomo.grasso.82@gmail.com>
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).

from odoo import models, fields, api


class AccountInvoice(models.Model):
    _inherit = "account.invoice"

    """
    When an invoice is edited, the related sale orders indicators are updated
    """
    """
    test = fields.Boolean("test", compute='_test', store=True)

    @api.multi
    @api.depends('residual')
    def _test(self):

        sale_orders = self.mapped('invoice_line_ids.sale_line_ids.order_id')
        for order in sale_orders:
            order._get_order_paid_amount()

    @api.multi
    def write(self, vals):
        res = super(AccountInvoice, self).write(vals)

        sale_orders = self.mapped('invoice_line_ids.sale_line_ids.order_id')
        for order in sale_orders:
            order._get_order_paid_amount()

        return res
    """

class AccountMoveLine(models.Model):
    _inherit = "account.move.line"

    """
    When an invoice is edited, the related sale orders indicators are updated
    """

    @api.multi
    def write(self, vals):
        res = super(AccountMoveLine, self).write(vals)

        sale_orders = self.mapped('invoice_id.invoice_line_ids.sale_line_ids.order_id')
        for order in sale_orders:
            order._get_order_paid_amount()

        return res