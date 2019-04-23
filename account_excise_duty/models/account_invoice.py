# -*- coding: utf-8 -*-
# © 2019 Giacomo Grasso
# License GPL-3.0 or later (http://www.gnu.org/licenses/gpl.html).

from odoo import models, fields, api, tools, _
from odoo.exceptions import UserError


class AccountInvoice(models.Model):
    _inherit = "account.invoice"


    @api.multi
    def compute_nicotine_taxes(self, vals):
        ''' Compute taxes on nicotine quantities and add two lines with
        related tax lines, each with its specific product.
        '''
        for inv in self:
            product_obj = self.env["product.product"]
            tax_prod_with = product_obj.search([('excise_nic_tax', '!=', False)])
            tax_prod_without = product_obj.search([('excise_no_nic_tax', '!=', False)])
            if len(tax_prod_with) != 1 or len(tax_prod_without) != 1:
                raise UserError(_("Selezionare almeno ed una sola imposta per i prodotti "
                                  "con e senza nicotina."))

            inv_lines = []
            ml_with_nicotine = 0.0
            ml_without_nicotine = 0.0
            sequence = max(line.sequence for line in inv.invoice_line_ids)

            for line in inv.invoice_line_ids:
                if line.product_id.has_nicotine:
                    ml_with_nicotine += line.product_id.bottle_ml * line.quantity
                else:
                    ml_without_nicotine += line.product_id.bottle_ml * line.quantity

            if ml_with_nicotine:
                inv_lines.append((0, 0, {
                    'product_id': tax_prod_with.id,
                    'name': tax_prod_with.name,
                    'quantity': ml_with_nicotine,
                    'account_id': tax_prod_with.property_account_income_id,
                    'price_unit': tax_prod_with.lst_price,
                    'uom_id': tax_prod_without.uom_id,
                    'invoice_line_tax_ids': [(4, tax.id) for tax in tax_prod_with.taxes_id],
                    'sequence': sequence + 1,
                }))
            if ml_without_nicotine:
                inv_lines.append((0, 0, {
                    'product_id': tax_prod_without.id,
                    'name': tax_prod_without.name,
                    'quantity': ml_without_nicotine,
                    'uom_id': tax_prod_without.uom_id,
                    'account_id': tax_prod_without.property_account_income_id,
                    'price_unit': tax_prod_without.lst_price,
                    'invoice_line_tax_ids': [(4, tax.id) for tax in tax_prod_without.taxes_id],
                    'sequence': sequence + 2,

                }))

            inv.update({'invoice_line_ids': inv_lines})
            inv.compute_taxes()


class ProductProduct(models.Model):
    _inherit = "product.product"

    bottle_ml = fields.Float(string="Ml")
