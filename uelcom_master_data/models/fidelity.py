# @author Giacomo Grasso <giacomo.grasso.82@gmail.com>
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).

import datetime
from odoo import models, fields, api


class FidelityTransaction(models.Model):
    _name = "fidelity.transaction"
    _description = "Fidelity Transaction"

    date = fields.Datetime(string='Date')
    weekday = fields.Integer(string='Weekday', store=True,
                             compute='_compute_weekday')
    partner_id = fields.Many2one(
        string='Partner', comodel_name='res.partner')
    shop = fields.Char(string='Shop')
    amount = fields.Float(string='Amount')
    points = fields.Integer(string='Points')

    @api.multi
    @api.depends('date')
    def _compute_weekday(self):
        for transaction in self:
            if not transaction.date:
                continue
            transaction.weekday = transaction.date.weekday() + 1


class FidelityVoucher(models.Model):
    _name = "fidelity.voucher"
    _description = "Fidelity Voucher"

    partner_id = fields.Many2one(
        string='Partner', comodel_name='res.partner')
    date = fields.Datetime(string='Date')
    shop = fields.Char(string='Shop')
    value = fields.Float(string='Value')
    points = fields.Integer(string='Points')
    status = fields.Char(string='Status')
    typology = fields.Char(string='Typology')
    used_moviment = fields.Char(string='Used Moviment')

