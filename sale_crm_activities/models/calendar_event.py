# -*- coding: utf-8 -*-
# © 2017 Giacomo Grasso
# License GPL-3.0 or later (http://www.gnu.org/licenses/gpl.html).

from datetime import datetime

from odoo import models, fields, api, _


class CalendarEvent(models.Model):
    _inherit = "calendar.event"

    partner_id = fields.Many2one(related='opportunity_id.partner_id')
    duration_text = fields.Char(
        string='Duration',
        compute='compute_duration_text',
        store=True)
    event_status = fields.Selection([
        ('todo', "To do"),
        ('done', "Done"),
        ('cancelled', "Cancelled"),
    ], default='todo', string='Status')

    start = fields.Datetime('Start', required=True,
                            help="Start date of an event, without time for full days events",
                            default=lambda self: datetime.today())
    stop = fields.Datetime('Stop', required=True,
                           help="Stop date of an event, without time for full days events",
                           default=lambda self: datetime.today())

    @api.multi
    def open_full_record(self):
        self.ensure_one()
        form_view = self.env.ref('calendar.view_calendar_event_form')
        return {
            'name': _('Meeting'),
            'type': 'ir.actions.act_window',
            'view_type': 'form',
            'view_mode': 'form',
            'res_model': self._name,
            'res_id': self.id,
            'view_id': form_view.id,
            'target': 'new',
        }

    @api.depends('allday', 'start_date', 'stop_date',
                 'start_datetime', 'stop_datetime')
    def compute_duration_text(self):
        for event in self:
            if event.allday:
                event.duration_text = _("{} >> {}".format(
                    event.start_date, event.stop_date))
            else:
                event.duration_text = _("{} >>   {}".format(
                    event.start_datetime, event.stop_datetime))
