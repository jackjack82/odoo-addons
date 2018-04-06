# coding: utf-8
# @author Giacomo Grasso <giacomo.grasso.82@gmail.com>
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).

from odoo import models, fields, api


class AccountInvoice(models.Model):
    _inherit = "account.invoice"

    """
    When an invoice is edited, the related purchase order lines are split
    """

    @api.multi
    def action_invoice_open(self):
        res = super(AccountInvoice, self).action_invoice_open()

        order_lines = self.mapped('invoice_line_ids.purchase_line_id')
        line_obj = self.env['purchase.order.line']

        # split each order line if the order is set as "split lines"
        for line in order_lines:
            if not line.order_id.split_lines:
                continue

            # we create a new line with the amount not yet invoiced
            invoiced_amount = line.invoice_lines[0].price_subtotal
            invoiced_price = line.invoice_lines[0].price_unit
            uninvoiced_amount = line.price_subtotal - invoiced_amount
            open_qty = line.product_qty - line.qty_invoiced
            if uninvoiced_amount <= 0 or open_qty <= 0:
                continue
            price_unit = uninvoiced_amount / open_qty

            taxes = [tax.id for tax in line.taxes_id]
            new_line_data = ({
                'name': line.name,
                'product_uom': line.product_uom.id,
                'price_unit': price_unit,
                'product_id': line.product_id.id,
                'order_id': line.order_id.id,
                'taxes_id': [(4, taxes)],
                'product_qty': open_qty,
                'date_planned': line.date_planned,
                'account_analytic_id': line.account_analytic_id,
            })

            line_obj.create(new_line_data)

            # in the old line we set the ordered amount equal to the invoiced amount
            line.product_qty = line.qty_invoiced
            line.price_unit = invoiced_price
            if line.product_id.type not in ['consu', 'product']:
                line.qty_received = line.qty_invoiced

        return res
