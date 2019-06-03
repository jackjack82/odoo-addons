# @author Giacomo Grasso <giacomo.grasso.82@gmail.com>
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).

from odoo import models, fields, api


class ResPartner(models.Model):
    _inherit = "res.partner"

    sex = fields.Selection([
        ('male', 'Male'),
        ('female', 'Female'),
        ('other', 'Other'),
    ], string='Sex')

    age = fields.Integer(string='Age')
    total_points = fields.Integer(
        string='Current points',
        compute='_compute_total_points')
    total_amount = fields.Integer(
        string='Total amount',
        compute='_compute_total_amount')
    fidelity_selection = fields.Boolean(string='Fidelity Selection')

    @api.multi
    def _compute_total_points(self):
        transaction_obj = self.env['fidelity.transaction']
        for partner in self:
            transaction_ids = transaction_obj.search([
                ('partner_id', '=', partner.id)])
            new_points = sum([x.points for x in transaction_ids])
            partner.total_points = new_points

    @api.multi
    def _compute_total_amount(self):
        transaction_obj = self.env['fidelity.transaction']
        for partner in self:
            transaction_ids = transaction_obj.search([
                ('partner_id', '=', partner.id)])
            amount = sum([x.amount for x in transaction_ids])
            partner.total_amount = amount
