# -*- coding: utf-8 -*-
# © 2019 Giacomo Grasso
# License GPL-3.0 or later (http://www.gnu.org/licenses/gpl.html).

from odoo import models, fields, api, tools, _


class ProductTemplate(models.Model):
    _inherit = "product.template"

    bottle_ml = fields.Float(string="Ml", related='product_variant_ids.bottle_ml')
    has_nicotine = fields.Boolean(string="Nicotine")

    excise_nic_tax = fields.Boolean(string="Excise product with nicotine")
    excise_no_nic_tax = fields.Boolean(string="Excise product without nicotine")

    @api.model
    def create(self, vals):
        ''' Store the initial standard price in order to be able to
        retrieve the cost of a product template for a given date .
        '''
        tools.image_resize_images(vals)
        template = super(ProductTemplate, self).create(vals)
        if "create_product_product" not in self._context:
            template.with_context(create_from_tmpl=True).create_variant_ids()

        # This is needed to set given values to first variant after creation
        related_vals = {}
        if vals.get('bottle_ml'):
            related_vals['bottle_ml'] = vals['bottle_ml']
        if vals.get('has_nicotine'):
            related_vals['has_nicotine'] = vals['has_nicotine']
        if related_vals:
            template.write(related_vals)
        return template


class ProductProduct(models.Model):
    _inherit = "product.product"

    bottle_ml = fields.Float(string="Ml")
