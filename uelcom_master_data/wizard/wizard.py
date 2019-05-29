from odoo import models, api, fields, _
from odoo.exceptions import UserError


class PartnerAnalysisWizard(models.TransientModel):
    _name = 'partner.analysis.wizard'

    date_from = fields.Datetime('Date from')
    date_to = fields.Datetime('Date to')
    result_order = fields.Selection([
        ('DESC', 'ASC'),
        ('ASC', 'DESC'),
    ])
    limit = fields.Integer('Limit in research')
    age_from = fields.Integer('From age')
    age_to = fields.Integer('To age')
    city = fields.Char('City')
    state_id = fields.Many2one('res.country.state', 'State')
    country_id = fields.Many2one('res.country', 'Country')
    sex = fields.Selection([
        ('male', 'Male'),
        ('female', 'Female'),
    ], string='Sex')

    def partner_analysis(self):
        partner_obj = self.env['res.partner']
        limit = "LIMIT {}".format(self.limit) if self.limit else ""
        main_query = """
            SELECT  partner_id,
                    sum(amount) as amount,
                    sum(points) as points
            FROM fidelity_transaction ft
            WHERE create_date BETWEEN '{_01}' AND '{_02}'
            
            GROUP BY partner_id
            ORDER BY points {_03}
            {_04}
        """.format(_01=self.date_from,
                   _02=self.date_to,
                   _03=self.result_order,
                   _04=limit,
                   )

        self.env.cr.execute(main_query)
        lines = self.env.cr.fetchall()

        client_ids = [x[0] for x in lines]
        # set to false the parameter on ALL partners
        partners = partner_obj.search([
            ('fidelity_selection', '=', True)
        ])
        partners.update({'fidelity_selection': False})

        # managing optional parameters
        clients = partner_obj.browse(client_ids)

        if self.sex:
            clients = clients.filtered(lambda c: c.sex == self.sex)
        if self.age_to and self.age_from > self.age_to:
            raise UserError(_("'From age' can not be smaller than 'To age'."))
        if self.age_from:
            clients = clients.filtered(lambda c: c.age >= self.age_from)
        if self.age_to:
            clients = clients.filtered(lambda c: c.age <= self.age_to)
        if self.city:
            clients = clients.filtered(lambda c: c.city == self.city)
        if self.state_id:
            clients = clients.filtered(lambda c: c.state_id == self.state_id)
        if self.country_id:
            clients = clients.filtered(lambda c: c.country_id == self.country_id)

        # setting parameter on new partners
        clients.update({'fidelity_selection': True})

        return {
            "type": "ir.actions.do_nothing"
        }

