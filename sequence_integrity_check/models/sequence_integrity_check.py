# coding: utf-8
#   @author Giacom Grasso <giacomo.grasso.82@gmail.com>
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).

from odoo import models, fields, api
from odoo.tools.safe_eval import safe_eval

from datetime import datetime

class SequenceIntegrityCheck(models.Model):
    _name = "sequence.integrity.check"
    _description = "Sequence Integrity Check"

    name = fields.Char(string="Name", required=True)
    sequence_id = fields.Many2one(
        "ir.sequence", "Sequence", required=True,
        help="Select the sequence that needs to be checked"
    )
    prefix = fields.Char("Prefix")
    suffix = fields.Char("Suffix")
    increment = fields.Integer("Increment")
    model_id = fields.Many2one(
        'ir.model', 'Model', required=True,
        help="Select the model that uses the sequence"
    )
    model_name = fields.Char('Model name', related='model_id.model')
    field_id = fields.Many2one(
        'ir.model.fields', 'Model Field', required=True,
        domain="[('model_id', '=', model_id), ('ttype', 'in', ['char','text'])]",
        help="Select the field of the model where the sequence is written."
    )
    date_field_id = fields.Many2one(
        'ir.model.fields', 'Date Field',
        domain="[('model_id', '=', model_id), ('ttype', 'in', ['date'])]",
        help="If selected, the module will check that the sequence is ordered by date"
    )
    filter_domain = fields.Char(
        string='Order Filter Domain', default=[]
    )
    last_check = fields.Datetime(string="Last check", readonly=True)
    status = fields.Selection([
        ('draft', 'Draft'),
        ('success', 'Success'),
        ('failed', 'Failed')],
        default='draft')
    output = fields.Text("Output")

    @api.multi
    def sequence_integrity_check(self):
        for check in self:
            domain = []
            if self.filter_domain:
                domain = safe_eval(self.filter_domain)

            # creating ordered list of elements
            search = self.env[self.model_id.model].search(domain)
            obj_list = []
            for obj in search:
                # cleaning the sequence
                name = getattr(obj, self.field_id.name, None)
                start = len(self.prefix) if self.prefix else None
                end = len(self.suffix) if self.suffix else None
                num = name[start:end]

                date = getattr(obj, self.date_field_id.name, False)
                obj_list.append((date, num, obj.id))
            obj_list.sort(key=lambda o: o[1])

            output = ""
            previous = (0, 0, 0)
            for following in obj_list:
                try:
                    # check sequence structure
                    if int(previous[1]) + self.increment != int(following[1]):
                        output += "Sequence error between {} and {}\n".format(
                            previous[1], following[1])

                    # check date progression
                    if previous[0] > following[0]:
                        output += "Date error between {} and {}\n".format(
                            previous[1], following[1])
                except:
                    output += "Format error between {} and {}\n".format(
                        previous[1], following[1])
                previous = following

            self.last_check = datetime.now()

            # returning output and check state
            self.output = output
            if output:
                self.status = 'failed'
            else:
                self.status = 'success'


    @api.onchange('sequence_id')
    def _onchange_sequence(self):
        if self.sequence_id:
            self.prefix = self.sequence_id.prefix
            self.suffix = self.sequence_id.suffix
            self.increment = self.sequence_id.number_increment
