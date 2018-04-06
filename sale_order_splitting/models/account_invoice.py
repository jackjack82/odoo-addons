# coding: utf-8
# @author Giacomo Grasso <giacomo.grasso.82@gmail.com>
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).

from odoo import models, fields, api, _
from odoo.exceptions import UserError


class AccountInvoice(models.Model):
    _inherit = "account.invoice"

    """
    When an invoice is edited, the related sale orders lines are split
    """

    @api.multi
    def action_invoice_open(self):
        res = super(AccountInvoice, self).action_invoice_open()

        # for managing rounding problems we store the original total amount of orders
        orders = self.mapped('invoice_line_ids.sale_line_ids.order_id')
        ord_orig_amount = {}
        for order in orders:
            ord_orig_amount[order.id] = order.amount_total

        # split each order line if the order is set as "split lines"
        order_lines = self.mapped('invoice_line_ids.sale_line_ids')
        line_obj = self.env['sale.order.line']

        for line in order_lines:
            if not line.order_id.split_lines:
                continue

            # we create a new line with the amount not yet invoiced
            invoiced_amount = line.invoice_lines[0].price_subtotal
            invoiced_price = line.invoice_lines[0].price_unit
            uninvoiced_amount = line.price_subtotal - invoiced_amount
            open_qty = line.product_uom_qty - line.qty_invoiced
            if uninvoiced_amount <= 0 or open_qty <= 0:
                continue
            price_unit = uninvoiced_amount / open_qty

            taxes = [tax.id for tax in line.tax_id]
            new_line_data = ({
                'name': line.name,
                'product_uom': line.product_uom.id,
                'price_unit': price_unit,
                'product_id': line.product_id.id,
                'order_id': line.order_id.id,
                'tax_id': [(4, taxes)],
                'discount': line.discount,
                'product_uom_qty': open_qty,
            })
            line_obj.create(new_line_data)

            # the original order line is updated
            line.price_unit = invoiced_price
            line.product_uom_qty = line.qty_invoiced

            # once lines are split, there might be order total difference.
            # we compare the original and new amount, we offset the difference in a specific line
            for order in orders:
                round_prod = self.env['product.product'].search([('rounding_product', '=', '1')])
                diff = ord_orig_amount.get(order.id, False) - order.amount_total
                if not diff:
                    continue
                rounding_line = order.order_line.product_id.filtered(lambda r: r.rounding_product)
                if rounding_line[0]:
                    rounding_line[0].price_unit += diff

                # if there is a difference in old and new totals, a new line is created
                if not round_prod[0] or round_prod[0].type != 'service':
                    raise UserError(_('Please define a product for rounding. It must be a service.'))
                round_line = ({
                    'name': _('Rounding'),
                    'product_id': round_prod[0].id,
                    'product_uom': round_prod[0].uom_id.id,
                    'price_unit': diff,
                    'order_id': order.id,
                })
                line_obj.create(round_line)

        return res
