# -*- coding: utf-8 -*-

from odoo import api, models,fields, _
from odoo.exceptions import UserError


class PurchaseOrder(models.Model):
    _inherit = 'purchase.order'

    order_accounting_id = fields.Many2one(
        comodel_name="order.accounting",
        string='Order accounting')
    move_id = fields.Many2one(
        comodel_name="account.move",
        string='Order move')

    # TODO: at order variation update move lines

    @api.multi
    def button_confirm(self):
        res = super(PurchaseOrder, self).button_confirm()
        mv_obj = self.env['account.move']
        for order in self:
            if not order.order_accounting_id:
                continue
            name = "Provising for {}".format(order.name)
            order_mv = mv_obj.create({
                'ref': name,
                'journal_id': order.order_accounting_id.journal_id,
                'date': order.date_order.date(),
            })

            line_ids = [
                (0, 0, {
                    'account_id': order.order_accounting_id.cost_prov_acc_id.id,
                    'name': name,
                    'debit': order.amount_total,
                }),
                (0, 0, {
                    'account_id': order.order_accounting_id.debit_prov_acc_id.id,
                    'name': name,
                    'debit': order.amount_total,
                })]

            order_mv.with_context(check_move_validity=False).update(
                {'line_ids': line_ids})
            order.move_id = order_mv.id

        return res


