# coding: utf-8
# @author Giacomo Grasso <giacomo.grasso.82@gmail.com>
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).

from odoo import models, fields, api


class AccountInvoice(models.Model):
    _inherit = "account.invoice"

    """
    When an invoice is edited, the related sale orders indicators are updated
    """

    @api.multi
    def action_invoice_open(self):
        res = super(AccountInvoice, self).action_invoice_open()

        # if it is a purchase invoice, edit the related purchase order line
        po_lines = self.mapped('invoice_line_ids.purchase_line_id')
        for line in po_lines:
            if not line.order_id.split_lines:
                continue
            line_obj = self.env['purchase.order.line']

            # we create a new line with the amount not yet invoiced
            uninvoiced_amount = line.product_qty - line.qty_invoiced
            if uninvoiced_amount == 0:
                continue
            taxes = [tax.id for tax in line.taxes_id]
            new_line_data = ({
                'name': line.name,
                'product_qty': uninvoiced_amount,
                'date_planned': line.date_planned,
                'taxes_id': [(4, taxes)],
                'product_uom': line.product_uom.id,
                'price_unit': line.price_unit,
                'product_id': line.product_id.id,
                'order_id': line.order_id.id,
                'account_analytic_id': line.account_analytic_id,
            })
            line_obj.create(new_line_data)

            # in the old line we set the ordered amount equal to the invoiced amount
            line.product_qty = line.qty_invoiced
            if line.product_id.type not in ['consu', 'product']:
                line.qty_received = line.qty_invoiced

        return res

        """
        # if it is a sale invoice, edit the related sale order lines
        so_lines = self.mapped('invoice_line_ids.sale_line_ids.order_id')
        for order in so_lines:
            amount_paid, amount_unpaid = order._get_order_paid_amount()

            order.write({
                'order_amount_paid': amount_paid,
                'order_amount_to_pay': order.amount_total - amount_paid,
            })

        return res
        """
