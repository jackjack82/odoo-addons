# -*- coding: utf-8 -*-

from odoo import api, fields, models, _
from odoo.exceptions import UserError


class AccountMoveEditLine(models.TransientModel):
    _name = 'account.move.edit.line'

    line_id = fields.Many2one(
        comodel_name="account.move.line", string="Invoice Line")
    name = fields.Char(string="Description")
    wizard_id = fields.Many2one(comodel_name="account.move.edit", string="Wizard")
    partner_id = fields.Many2one(comodel_name="res.partner", string="Partner")
    account_id = fields.Many2one(comodel_name="account.account", string="Account")
    balance = fields.Float(string="Original")
    residual = fields.Float(string="New")
    date_maturity = fields.Date(string="Date maturity")


class AccountMoveEdit(models.TransientModel):
    _name = 'account.move.edit'

    wizard_line_ids = fields.One2many(
        comodel_name="account.move.edit.line",
        inverse_name="wizard_id",
        string="Lines")
    orig_residual = fields.Float(string='Total')
    move_residual = fields.Float(
        string='Total', compute='_compute_total')
    move_id = fields.Many2one(
        comodel_name="account.move", string="Move")

    @api.depends('wizard_line_ids.residual')
    def _compute_total(self):
        self.move_residual = sum(
            l.residual for l in self.wizard_line_ids)

    @api.model
    def default_get(self, fields):
        """When wizard opens we show all unreconciled lines with
        amount residual greater than 0."""
        res = super(AccountMoveEdit, self).default_get(fields)

        # collect move lines and check that they belong to the same move
        move = self.env['account.move']
        if self._context.get('active_model') == 'account.move.line':
            mls = self.env['account.move.line'].browse(
                self._context.get('active_ids', []))
            move = mls.mapped('move_id')

        if self._context.get('active_model') == 'account.move':
            move = self.env['account.move'].browse(
                self._context.get('active_ids', []))

        if len(move) != 1:
            raise UserError(_("You can perform this operation on one single move."))

        # create the wizard
        line_ids = []
        acc_type = [self.env.ref('account.data_account_type_receivable').id,
                    self.env.ref('account.data_account_type_payable').id
                    ]
        orig_residual = 0
        for line in move.line_ids:
            if line.account_id.user_type_id.id not in acc_type:
                continue
            orig_residual += line.amount_residual
            line_ids.append((0, 0, {
                'name': line.name,
                'line_id': line.id,
                'partner_id': line.partner_id.id,
                'account_id': line.account_id.id,
                'move_id': line.move_id.id,
                'date_maturity': line.date_maturity,
                'balance': line.balance,
                'residual': line.amount_residual,
            }))

        res.update({
            'move_id': move.id,
            'wizard_line_ids': line_ids,
            'orig_residual': orig_residual
        })
        return res

    @api.multi
    def edit_move(self):
        self.ensure_one()
        if self.wizard_line_ids.filtered(lambda l: l.residual < l.residual):
            raise UserError(_("New residual can not be lower that the original residual."))
        self.move_id.button_cancel()

        # editing existing move_lines
        acc_type = [self.env.ref('account.data_account_type_receivable').id,
                    self.env.ref('account.data_account_type_payable').id
                    ]
        wiz_ml = self.mapped('wizard_line_ids.line_id.id')
        aml_obj = self.env['account.move.line']

        for ml in self.move_id.line_ids:
            if (ml.id not in wiz_ml and
                    ml.account_id.user_type_id.id in acc_type):
                ml.unlink()

        for line in self.wizard_line_ids.with_context(check_move_validity=False):
            residual = line.residual
            if line.line_id:
                if residual < 0:
                    line.line_id.credit = residual
                else:
                    line.line_id.debit = residual
            else:
                new_line = ({
                    'name': line.name,
                    'partner_id': line.partner_id.id,
                    'account_id': line.account_id.id,
                    'move_id': self.move_id.id,
                })

                new_line.update({'credit': residual}) if residual < 0 else \
                    new_line.update({'debit': residual})

                aml_obj.with_context(check_move_validity=False).create(new_line)

        self.move_id.post()
