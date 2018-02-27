# coding: utf-8
#   @author Giacom Grassso <giacomo.grasso.82@gmail.com>
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).

from odoo import models, fields, api
import odoo.addons.decimal_precision as dp

class SaleOrder(models.Model):
    _inherit = "sale.order"

    order_amount_invoiced = fields.Float(
        compute='_get_order_invoice_amount',
        string='Invoiced',
        store=True,
        readonly=True,
        digits=dp.get_precision('Product Price'))
    order_amount_to_invoice = fields.Float(
        compute='_get_order_invoice_amount',
        string='To Invoice',
        store=True,
        readonly=True,
        digits=dp.get_precision('Product Price'))

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
