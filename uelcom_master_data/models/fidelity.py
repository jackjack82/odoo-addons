# @author Giacomo Grasso <giacomo.grasso.82@gmail.com>
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).
from odoo import models, fields, api


class FidelityTransaction(models.Model):
    _name = "fidelity.transaction"
    _description = "Fidelity Transaction"

    date = fields.Datetime(string='Date')
    partner_id = fields.Many2one(
        string='Partner', comodel_name='res.partner')
    shop = fields.Char(string='Shop')
    amount = fields.Float(string='Amount')
    points = fields.Integer(string='Points')


class FidelityVoucher(models.Model):
    _name = "fidelity.voucher"
    _description = "Fidelity Voucher"

    partner_id = fields.Many2one(
        string='Partner', comodel_name='res.partner')
    date = fields.Datetime(string='Date')
    shop = fields.Char(string='Shop')
    value = fields.Float(string='Value')
    points = fields.Integer(string='Points')
