# -*- coding: utf-8 -*-
# © 2019 Giacomo Grasso
# License GPL-3.0 or later (http://www.gnu.org/licenses/gpl.html).

import math

from odoo import models, fields, api, _
from odoo.exceptions import UserError


class AccountTax(models.Model):
    _inherit = "account.tax"

    excise_type = fields.Selection([
        ('nicotine', 'Excise on nicotine'),
        ],
        string="Excise type",
        help="Each excise type shall add a different computation method"
             "for taxation."
    )

    def _compute_amount(self, base_amount, price_unit, quantity=1.0, product=None, partner=None):
        """ Override of tax computation method for computing excise tax.
        """
        self.ensure_one()

        if self.excise_type == 'nicotine':
            if not product:
                raise UserError(_("The excise tax {} can not be computed because the related"
                                  "product is missing in tax computation method. Please provide one.").format(
                    self.name
                ))

            total_qty = float(product.bottle_ml * quantity)
            if self.amount_type == 'fixed':
                if base_amount:
                    return math.copysign(quantity, base_amount) * self.amount * product.bottle_ml
                else:
                    return quantity * self.amount
            if (self.amount_type == 'percent' and not self.price_include) or (
                    self.amount_type == 'division' and self.price_include):
                return total_qty * self.amount / 100
            if self.amount_type == 'division' and not self.price_include:
                return total_qty / (1 - self.amount / 100) - total_qty
            if self.amount_type == 'percent' and self.price_include:
                return total_qty - (total_qty / (1 + self.amount / 100))

        if not self.excise_type:
            return super(AccountTax, self)._compute_amount(
                base_amount, price_unit, quantity=1.0, product=None, partner=None)
