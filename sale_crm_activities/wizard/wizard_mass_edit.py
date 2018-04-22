# -*- coding: utf-8 -*-

from odoo import models, fields, api, _


class BankStatementLineMassEdit(models.TransientModel):
    _name = 'calendar.event.mass.edit'

    allday = fields.Boolean(string='All day')
    start_date = fields.Date(string='Start date')
    event_status = fields.Selection([
        ('todo', "To do"),
        ('done', "Done"),
        ('cancelled', "Cancelled"),
    ], default='todo', string='Status')

    @api.multi
    def button_edit_data(self):
        """ Upon confirmation data will be edited in all
            calendar event selected."""
        context = dict(self._context or {})
        active_ids = context.get('active_ids', []) or []

        for event in self.env['calendar.event'].browse(active_ids):
            event.allday = self.allday
            event.start_date = self.start_date
            event.status = self.status

        return {"type": "ir.actions.act_window_close"}
