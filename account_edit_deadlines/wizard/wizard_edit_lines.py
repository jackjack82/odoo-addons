# -*- coding: utf-8 -*-

from odoo import api, fields, models, _
from odoo.exceptions import UserError


class AccountMoveEditLine(models.TransientModel):
    _name = 'account.move.edit.line'

    move_id = fields.Many2one(comodel_name="", string="Wizard")
    line_id = fields.Integer(string="Invoice Line")
    name = fields.Char(string="Description")
    wizard_id = fields.Many2one(comodel_name="sale.advance.payment.inv", string="Wizard")
    debit = fields.Float(string="Debit")
    credit = fields.Float(string="Credit")


class AccountMoveEdit(models.TransientModel):
    _name = 'account.move.edit'

    def _compute_line_ids(self):
        """When wizard opens we show all unreconciled lines with
        amount residual greater than 0."""

        moves = self.env['account.move'].browse(self._context.get('active_ids', []))
        line_ids = []
        for move in moves:
            for line in move.line_ids:
                if line.amount_residual == 0:
                    continue
                residual = (line.debit - line.credit) - line.amount_residual
                line_ids.append((0, 0, {
                    'name': line.name,
                    'line_id': line.id,
                    'debit': line.debit,
                    'credit': line.credit,
                    'amount_residual': residual,
                }))

        self.update({'wizard_line_ids': line_ids})

    wizard_line_ids = fields.One2many(
        comodel_name="account.move.edit.line",
        inverse_name="wizard_id",
        default=_compute_line_ids,
        string="Lines")

    """
    @api.multi
    def edit_move(self):

        if self.advance_payment_method in ['select_qty', 'select_amount']:

            # we now check that there are no wizard lines with 0 quantity/amount
            if self.advance_payment_method == 'select_qty' and not all(
                    self.wizard_line_ids.mapped('qty_to_invoice')):
                raise UserError(_("No lines shall have quantity equal to 0."))

            if self.advance_payment_method == 'select_amount' and not all(
                    self.wizard_line_ids.mapped('amount_to_invoice')):
                raise UserError(_("No lines shall have amount equal to 0."))

            # once checks are done, we proceed creating the invoice
            orders = self.env['sale.order'].browse(self._context.get('active_ids', []))
            inv_id = orders.action_invoice_create(final=True)
            invoice = self.env['account.invoice'].browse(inv_id)
            order_lines = self.wizard_line_ids.mapped('line_id')

            # we now delete/edit the exceeding lines and update quantities where needed
            for line in invoice.invoice_line_ids:
                order_line = line.sale_line_ids[0]

                # price unit is computed again from order line to include discounts and similar
                price_unit = order_line.price_subtotal / order_line.product_uom_qty

                # if the order line of the invoice line is in the wizard, it is updated, elsewhere is deleted
                if line.sale_line_ids[0].id in order_lines:
                    wizard_line = self.wizard_line_ids.filtered(lambda r: r.line_id == order_line.id)
                    if self.advance_payment_method == 'select_qty':
                        line.write({
                            'quantity': wizard_line.qty_to_invoice,
                        })
                    elif self.advance_payment_method == 'select_amount':
                        # if we invoice a fixed amount to invoice, we divide the total by the
                        # fixed price unit and get the rounding
                        precision = self.env['decimal.precision'].precision_get('Product Unit of Measure')
                        round_qty = round(wizard_line.amount_to_invoice/price_unit, precision)
                        line.write({'quantity': round_qty})
                        order_line.write({'quantity': round_qty})

                else:
                    line.unlink()

            # after editing/deleting invoice lines it is required to compute taxes again
            invoice.compute_taxes()

            if self._context.get('open_invoices', False):
                return orders.action_view_invoice()
            return {'type': 'ir.actions.act_window_close'}
        else:
            return super(SaleAdvancePaymentInv, self).create_invoices()
    """