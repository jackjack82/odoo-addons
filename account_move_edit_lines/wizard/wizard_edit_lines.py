# -*- coding: utf-8 -*-

from odoo import api, fields, models, _
from odoo.exceptions import UserError


class AccountMoveEditLine(models.TransientModel):
    _name = 'account.move.edit.line'
    _order = 'sequence'

    sequence = fields.Integer("")
    move_id = fields.Many2one(
        comodel_name="account.move", string="Move")
    line_id = fields.Many2one(
        comodel_name="account.move.line", string="Invoice Line")
    name = fields.Char(string="Description")
    wizard_id = fields.Many2one(
        comodel_name="sale.advance.payment.inv", string="Wizard")
    residual = fields.Float(string="Residual")
    balance = fields.Float(string="Balance")
    date_maturity = fields.Date(string="Date maturity")

    @api.multi
    def split_line(self):
        self.ensure_one()

        new_line = (0, 0, {
            'name': self.name,
            'move_id': self.move_id.id,
            'line_id': self.id,
            'date_maturity': self.date_maturity,
            'balance': self.residual,
            'residual': self.residual,
        })
        self.residual = 0
        self.wizard_id.update({'wizard_line_ids': new_line})


class AccountMoveEdit(models.TransientModel):
    _name = 'account.move.edit'

    def _compute_line_ids(self):
        """When wizard opens we show all unreconciled lines with
        amount residual greater than 0."""

        if self._context.get('active_model') == 'account.move.line':
            mls = self.env['account.move.line'].browse(
                self._context.get('active_ids', []))
            moves = mls.mapped('move_id')

        if self._context.get('active_model') == 'account.move':
            moves = self.env['account.move'].browse(
                self._context.get('active_ids', []))
        line_ids = []
        for move in moves:
            acc_type = [self.env.ref(
                            'account.data_account_type_receivable').id,
                        self.env.ref(
                            'account.data_account_type_payable').id
                        ]
            for line in move.line_ids:
                if (line.amount_residual == 0 or
                        line.account_id.user_type_id.id not in acc_type):
                    continue
                line_ids.append((0, 0, {
                    'name': line.name,
                    'line_id': line.id,
                    'move_id': line.move_id.id,
                    'date_maturity': line.date_maturity,
                    'balance': line.balance,
                    'residual': line.amount_residual,
                }))

        return line_ids

    wizard_line_ids = fields.One2many(
        comodel_name="account.move.edit.line",
        inverse_name="wizard_id",
        default=_compute_line_ids,
        string="Lines")

    @api.multi
    def edit_move(self):
        for line in self.wizard_line_ids:
            if line.residual > 0:
                line.line_id.credit -= line.residual

    """
            # there should be no line with 0 residual
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