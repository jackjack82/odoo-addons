# coding: utf-8
# @author Giacom Grasso <giacomo.grasso.82@gmail.com>

from odoo import models, fields, api


class PurchaseOrder(models.Model):
    _inherit = "purchase.order"

    split_lines = fields.Boolean(
        string='Split lines',
        help="If flagged, at invoice validation, order lines that have been invoiced are split."
             "The open amount of each line is moved into a new line")
