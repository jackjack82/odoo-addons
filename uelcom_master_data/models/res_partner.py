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
        string='Total points',
        compute='_compute_total_points')
    total_voucher = fields.Integer(
        string='Total voucher', store=True,
        compute='_compute_total_voucher')
    total_amount = fields.Integer(
        string='Total amount', store=True,
        compute='_compute_total_amount')
    fidelity_selection = fields.Boolean(string='Fidelity Selection')
    transaction_ids = fields.One2many(
        string='Transactions', comodel_name='fidelity.transaction',
        inverse_name='partner_id')
    voucher_ids = fields.One2many(
        string='Vouchers', comodel_name='fidelity.voucher',
        inverse_name='partner_id')

    @api.multi
    @api.depends('transaction_ids')
    def _compute_total_points(self):
        transaction_obj = self.env['fidelity.transaction']
        for partner in self:
            # transaction_ids = transaction_obj.search([
            #     ('partner_id', '=', partner.id)])
            # new_points = sum([x.points for x in transaction_ids])
            new_points = sum(x.amount for x in partner.transaction_ids)
            partner.total_points = new_points

    @api.multi
    @api.depends('voucher_ids')
    def _compute_total_voucher(self):
        voucher_obj = self.env['fidelity.voucher']
        for partner in self:
            voucher_ids = voucher_obj.search([
                ('partner_id', '=', partner.id)])
            new_vouchers = sum([x.points for x in voucher_ids])
            partner.total_voucher = new_vouchers

    @api.multi
    def _compute_total_amount(self):
        transaction_obj = self.env['fidelity.transaction']
        for partner in self:
            transaction_ids = transaction_obj.search([
                ('partner_id', '=', partner.id)])
            amount = sum([x.amount for x in transaction_ids])
            partner.total_amount = amount
