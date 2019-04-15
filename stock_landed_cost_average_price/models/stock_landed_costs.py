# -*- coding: utf-8 -*-
# © 2019 Giacomo Grasso
# License GPL-3.0 or later (http://www.gnu.org/licenses/gpl.html).

from odoo import models, fields, api


class LandedCost(models.Model):
    _inherit = 'stock.landed.cost'
    _description = 'Stock Landed Cost'

    use_average_cost = fields.Boolean(
        string='Use average cost only', help='Flagging this field you will apply '
        'landed costs to products with average price costing method, any other'
        'line will be ignored.')

    def get_valuation_lines(self):

        if not self.use_average_cost:
            return super(LandedCost, self).get_valuation_lines()

        lines = []

        for move in self.mapped('picking_ids').mapped('move_lines'):
            # compute landed cost for product with average cost method
            if move.product_id.valuation != 'manual_periodic' or move.product_id.cost_method != 'average':
                continue
            vals = {
                'product_id': move.product_id.id,
                'move_id': move.id,
                'quantity': move.product_qty,
                'former_cost': sum(quant.cost * quant.qty for quant in move.quant_ids),
                'weight': move.product_id.weight * move.product_qty,
                'volume': move.product_id.volume * move.product_qty
            }
            lines.append(vals)

        if not lines and self.mapped('picking_ids'):
            return super(LandedCost, self).get_valuation_lines()
        else:
            return lines

    @api.multi
    def button_validate(self):
        for cost in self:
            if not cost.use_average_cost:
                return super(LandedCost, self).button_validate()
            for line in cost.valuation_adjustment_lines:
                product = line.product_id
                ctx = dict(self.env.context.copy())
                # ctx.update({'location': location[0].id})
                qty_dict = product.with_context(
                    ctx)._compute_quantities_dict(False, False, False)
                qty = qty_dict[product.id]['qty_available']
                amount = round(line.additional_landed_cost / qty, 2)
                product.update({'standard_price': product.standard_price + amount})

                # cost.write({'state': 'done'})
        return True
