# coding: utf-8
#   @author Giacom Grasso <giacomo.grasso.82@gmail.com>
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).

from odoo import models, fields, api


class SequenceIntegrityCheck(models.Model):
    _name = "sequence.integrity.check"
    _description = "Sequence Integrity Check"

    name = fields.Char("Name")
    sequence_id = fields.Many2one("ir.sequence", "Sequence", required=True,
                               help="Select the sequence that needs to be checked")
    object_id = fields.Many2one('ir.model', 'Model', required=True,
                                help="Select the model that uses the sequence")
    field_id = fields.Many2one('ir.model.fields', 'Model Field', required=True,
                            domain="[('model_id', '=', object_id), ('ttype', 'in', ['char','text'])]",
                            help="Select the field of the model where the sequence is used")
    date_field = fields.Many2one('ir.model.fields', 'Date Field',
                                 help="If selected, the module will check that the sequence is ordered by date")
    domain = fields.Char("Domain")
    date_from = fields.Date("Initial date")
    date_to = fields.Date("Final date")
    last_check = fields.Date("Last check")
    status = fields.Selection([
        ('success', 'Success'),
        ('failed', 'Failed')])
    output = fields.Text("Output")

    @api.multi
    def sequence_integrity_check(self):
        pass


