# -*- coding: utf-8 -*-
# © 2019 Giacomo Grasso
# License GPL-3.0 or later (http://www.gnu.org/licenses/gpl.html).

from odoo import models, fields, api


class ProductCategory(models.Model):
    _inherit = 'product.category'
    _description = 'Product Category'

    apply_landed_cost = fields.Boolean(
        string='Apply landed costs', help='Apply landed cost to all'
        ' products included in this category')
