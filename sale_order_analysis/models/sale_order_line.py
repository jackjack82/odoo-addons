# coding: utf-8
#   @author Giacom Grasso <giacomo.grasso.82@gmail.com>
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).

from odoo import models, fields, api
import odoo.addons.decimal_precision as dp


class SaleOrderLine(models.Model):
    _inherit = "sale.order.line"

    amount_invoiced = fields.Float(
        compute='_get_invoice_amount',
        string='Amount Inv.',
        store=True,
        readonly=True,
        digits=dp.get_precision('Product Price'))
    amount_to_invoice = fields.Float(
        compute='_get_invoice_amount',
        string='Amount to Inv.',
        store=True,
        readonly=True,
        digits=dp.get_precision('Product Price'))

    @api.multi
    @api.depends('invoice_lines.invoice_id.state',
                 'invoice_lines.quantity',
                 'product_uom_qty',
                 'price_unit',
                 'tax_id',
                 )
    def _get_invoice_amount(self):
        """
        Compute the total amount invoiced and the remaining amount to be
        invoiced. If case of a refund, these amounts are decreased.
        """
        for order_line in self:
            amount_invoiced = 0.0
            for invoice_line in order_line.invoice_lines:
                if invoice_line.invoice_id.state != 'cancel':
                    tax_list = invoice_line.invoice_line_tax_ids.compute_all(
                        invoice_line.price_unit,
                        invoice_line.invoice_id.currency_id,
                        invoice_line.quantity,
                        invoice_line.product_id,
                        invoice_line.invoice_id.partner_id)['taxes']
                    taxes = 0.0
                    for tax in tax_list:
                        taxes += tax['amount']
                    if invoice_line.invoice_id.type == 'out_invoice':
                        amount_invoiced += invoice_line.price_subtotal + taxes
                    elif invoice_line.invoice_id.type == 'out_refund':
                        amount_invoiced -= invoice_line.price_subtotal + taxes

            order_line.amount_invoiced = amount_invoiced
            order_line.amount_to_invoice = order_line.price_total - amount_invoiced
