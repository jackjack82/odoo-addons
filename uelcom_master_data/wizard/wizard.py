import re
import pytz
from odoo import models, api, fields, _
from odoo.exceptions import UserError


class PartnerAnalysisWizard(models.TransientModel):
    _name = 'partner.analysis.wizard'
    _description = 'Partner Analysis Wizard'

    clear_previous = fields.Boolean(
        string='Clear previous selection', default=True,
        help="If flagged all previous selection will be removed.")
    no_operations = fields.Boolean(
        string='No operations', default=False,
        help="Select clients with NO operations, this overrides "
             "all the filters below!")

    num_operations = fields.Integer(
        string='Number of operations',
        help="Max number of operations the user has done.")
    result_order = fields.Selection([
        ('DESC', 'ASC'), ('ASC', 'DESC')], default='ASC')
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

    select_dates = fields.Boolean(string='Select dates')
    date_from = fields.Datetime(string='Date from')
    date_to = fields.Datetime(string='Date to')

    select_hours = fields.Boolean('Select hours')
    from_hr = fields.Char(string='From:', help="Write hour in format HH:MM")
    to_hr = fields.Char(string='To:', help="Write hour in format HH:MM")

    weekdays_filter = fields.Char(
        string='Weekdays',
        help="Set days in numerical value starting from Monday i.e. "
             "Monday=1, Tuesday=2 ... in the following format: 1,2,3,4")

    max_amount = fields.Integer('Max amount')
    min_amount = fields.Integer('Min amount')

    def partner_analysis(self):
        partner_obj = self.env['res.partner']
        limit = "LIMIT {}".format(self.limit) if self.limit else ""
        # manage time errors and query
        local_timezone = pytz.timezone(self._context.get('tz'))
        if not local_timezone:
            raise UserError('Please set the time zone on the user!')
        date_from = self.date_from.replace(
            tzinfo=pytz.utc).astimezone(local_timezone)
        date_to = self.date_to.replace(
            tzinfo=pytz.utc).astimezone(local_timezone)

        time_re = re.compile(r'^(([01]\d|2[0-3]):([0-5]\d)|24:00)$')
        if self.select_hours:
            if not (bool(time_re.match(self.from_hr) and
                         bool(time_re.match(self.to_hr)))):
                raise UserError(
                    'Hours fields for filtering is not in the correct '
                    'format, which is HH:MM . Please check')
            hours_range = "AND '{}:00' <= time_detail " \
                "AND time_detail <= '{}:00'".format(self.from_hr, self.to_hr)
        else:
            hours_range = ""

        # adding weekday filter
        weekdays = ''
        day_filter = ''
        if self.weekdays_filter:
            weekdays = tuple([int(z) for z in self.weekdays_filter.split(',')])*2
            day_filter = "AND weekday in {}".format(weekdays)

        main_query = """
        SELECT partner_id, count(partner_id) AS num_operations, 
            sum(amount) as amount, sum(points) as points
        FROM (
                    SELECT  partner_id, amount, points, date, weekday,
                    CAST(date::timestamp::time AS time) AS time_detail
            FROM fidelity_transaction ft
            ) AS data
        WHERE date BETWEEN '{_01}' AND '{_02}'
        {_05}
        {_06}

        GROUP BY partner_id
        ORDER BY points {_03}
        {_04}
        """.format(_01=date_from,
                   _02=date_to,
                   _03=self.result_order,
                   _04=limit,
                   _05=hours_range,
                   _06=day_filter,
                   )

        self.env.cr.execute(main_query)
        lines = self.env.cr.fetchall()

        # due to SQL query results, it is easier to filter data using
        # python based on the result of the query
        client_ids = []

        for line in lines:
            # filtering clients with limited num of operations
            if (self.num_operations and
                    not 0 < line[1] <= self.num_operations):
                continue
            # filtering clients per operation amount
            if (self.max_amount and
                    line[2] > self.max_amount):
                continue
            if (self.min_amount and
                    self.min_amount > line[2]):
                continue

            client_ids.append(line[0])

        # set to false the parameter on ALL partners
        if self.clear_previous:
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
            clients = clients.filtered(
                lambda c: c.country_id == self.country_id)

        # setting parameter on new partners
        clients.update({'fidelity_selection': True})

        return {
            "type": "ir.actions.do_nothing"
        }

