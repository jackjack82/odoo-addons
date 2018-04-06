# -*- coding: utf-8 -*-
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from odoo import api, fields, models, _


class SaleAdvancePaymentInvLines(models.TransientModel):
    _name = 'sale.advance.payment.inv.line'

    line_id = fields.Integer(string="Invoice Line")
    name = fields.Char(string="Description")
    wizard_id = fields.Many2one(comodel_name="sale.advance.payment.inv", string="Wizard")
    qty_invoiced = fields.Float(string="Qty Inv.")
    qty_to_invoice = fields.Float(string="Qty to Inv.")
    price_invoiced = fields.Float(string="Price Inv.")
    price_to_invoice = fields.Float(string="Price to Inv.")


class SaleAdvancePaymentInv(models.TransientModel):

    _inherit = 'sale.advance.payment.inv'

    advance_payment_method = fields.Selection(
        selection_add=[('lines_selection', 'Lines Selection')])
    invoice_line_ids = fields.One2many(
        comodel_name="sale.advance.payment.inv.line",
        inverse_name="wizard_id",
        string="Lines")

    @api.onchange('advance_payment_method')
    def onchange_line_ids(self):
        if self.advance_payment_method == 'lines_selection':
            sale_orders = self.env['sale.order'].browse(self._context.get('active_ids', []))
            line_ids = []
            for order in sale_orders:
                for line in order.order_line:
                    qty_to_invoice = line.product_uom_qty - line.qty_invoiced
                    if qty_to_invoice <= 0:
                        continue
                    line_ids.append((0, 0, {
                        'name': line.name,
                        'line_id': line.id,
                        'qty_invoiced': line.qty_invoiced,
                        'qty_to_invoice': qty_to_invoice,
                        'price_invoiced': line.price_unit,
                        'price_to_invoice': line.price_unit,
                    }))

            self.update({'invoice_line_ids': line_ids})

    @api.multi
    def create_invoices(self):
        # if the line selection is chosen, we create a normal invoice and then we delete exceeding lines
        if self.advance_payment_method == 'lines_selection':
            orders = self.env['sale.order'].browse(self._context.get('active_ids', []))
            inv_id = orders.action_invoice_create(final=True)
            invoice = self.env['account.invoice'].browse(inv_id)
            order_lines = self.invoice_line_ids.mapped('line_id')

            # once the invoice has been created we delete the exceeding lines
            # invoice lines and wizard lines are both linked to the order line
            for line in invoice.invoice_line_ids:
                # if the order line of the invoice line is in the wizard, it is updated, elsewhere is deleted
                if line.sale_line_ids[0].id in order_lines:
                    wizard_line = self.invoice_line_ids.filtered(lambda r: r.line_id == line.sale_line_ids[0].id)
                    line.write({
                        'quantity': wizard_line.qty_to_invoice,
                        'price_unit': wizard_line.price_to_invoice,
                    })
                else:
                    line.unlink()
            if self._context.get('open_invoices', False):
                return orders.action_view_invoice()
            return {'type': 'ir.actions.act_window_close'}
        else:
            return super(SaleAdvancePaymentInv, self).create_invoices()
