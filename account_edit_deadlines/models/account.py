# coding: utf-8

from odoo import models, fields, api, _


class AccountMove(models.Model):
    _inherit = 'account.move'

    @api.multi
    def edit_move_line(self):
        move = self[0]
        return {
            'name': _('Edit move lines'),
            'view_type': 'form',
            'view_mode': 'form',
            'res_model': 'account.move',
            'type': 'ir.actions.act_window',
            'target': 'new',
            'res_id': move.id or False,
        }