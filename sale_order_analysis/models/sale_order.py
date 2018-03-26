# coding: utf-8
#   @author Giacom Grasso <giacomo.grasso.82@gmail.com>
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).

from odoo import models, fields, api


class SaleOrder(models.Model):
    _inherit = "sale.order"

    # overriding invoice_ids to make it searcheable

    order_amount_invoiced = fields.Float(
        compute='_get_order_invoice_amount',
        string='Invoiced',
        store=True,
        copy=False)

    order_amount_to_invoice = fields.Float(
        compute='_get_order_invoice_amount',
        string='To Invoice',
        store=True,
        copy=False)

    order_amount_paid = fields.Float(
        string='Paid',
        copy=False)

    order_amount_to_pay = fields.Float(
        string='To be paid',
        copy=False)

    # key sale orders indicators
    invoiced_on_ordered = fields.Float(
        compute='_get_indicators',
        string='Inv/Ord',
        store=True,
        copy=False)
    paid_on_ordered = fields.Float(
        compute='_get_indicators',
        string='Paid/Ord',
        store=True,
        copy=False)
    paid_on_invoiced = fields.Float(
        compute='_get_indicators',
        string='Paid/Inv',
        store=True,
        copy=False)

    @api.multi
    @api.depends('amount_total', 'order_amount_invoiced', 'order_amount_paid')
    def _get_indicators(self):
        for order in self:

            order.invoiced_on_ordered = 0.0
            order.paid_on_ordered = 0.0
            order.paid_on_invoiced = 0.0

            if order.amount_total > 0:
                order.invoiced_on_ordered = round(order.order_amount_invoiced / order.amount_total, 2)
                order.paid_on_ordered = round(order.order_amount_paid / order.amount_total, 2)

            if order.order_amount_invoiced > 0:
                order.paid_on_invoiced = round(order.order_amount_paid / order.order_amount_invoiced, 2)

    @api.multi
    @api.depends('order_line.amount_invoiced', 'order_line.amount_to_invoice')
    def _get_order_invoice_amount(self):
        """
        Compute the total amount invoiced and the remaining amount to be
        invoiced of the entire sale order
        """
        for order in self:
            amount_invoiced = 0.0
            amount_to_invoice = 0.0

            for line in order.order_line:
                amount_invoiced += line.amount_invoiced
                amount_to_invoice += line.amount_to_invoice

            order.order_amount_invoiced = amount_invoiced
            order.order_amount_to_invoice = amount_to_invoice

    @api.multi
    def write(self, vals):
        for order in self:
            if vals.get('order_line', order.order_line):
                # vals['amount_paid'], vals['amount_unpaid'] = order._get_order_paid_amount()
                amount_paid, amount_unpaid = order._get_order_paid_amount()

                vals['order_amount_paid'] = amount_paid
                vals['order_amount_to_pay'] = order.amount_total - amount_paid

        return super(SaleOrder, self).write(vals)

    @api.multi
    def _get_order_paid_amount(self):
        """Compute the total amount paid and the remaining amount"""
        self.ensure_one()

        amount_paid = 0.0

        for invoice in self.invoice_ids:
            if invoice.move_id:
                amount_paid += invoice.amount_total - invoice.residual
        amount_unpaid = self.amount_total - amount_paid

        return amount_paid, amount_unpaid

