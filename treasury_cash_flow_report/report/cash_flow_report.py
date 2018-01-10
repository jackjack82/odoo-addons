# -*- coding: utf-8 -*-
# Part of Odoo. See LICENSE file for full copyright and licensing details.

from odoo import tools
from odoo import api, fields, models


class CashFlowReport(models.Model):
    _name = "cash.flow.report"
    _description = "Cash Flow Report"
    _auto = False
    _rec_name = 'date'
    _order = 'date desc'

    name = fields.Char(string='Label', readonly=True)
    date = fields.Date('Date', readonly=True)
    value = fields.Float('Amount', readonly=True)
    cf_forecast = fields.Boolean(string='From forecast', readonly=True)
    cf_reconciled = fields.Boolean(string='Reconc.', readonly=True)
    account_id = fields.Many2one(
        comodel_name='account.account',
        string='Account',
        readonly=True)
    analytic_account_id = fields.Many2one(
        comodel_name='account.analytic.account',
        string='Analytic Account',
        readonly=True)
    partner_id = fields.Many2one('res.partner', string='Partner', readonly=True)
    journal_id = fields.Many2one('account.journal', readonly=True,
                                 string='Journal')
    cf_share = fields.Text(string='Share', readonly=True)

    @api.model_cr
    def init(self):
        tools.drop_view_if_exists(self.env.cr, self._table)
        # the first SQL query update the JSONB field according to the
        # query parameter and explosion criteria
        self._get_main_query()

    def _select(self):

        select_str = """
            WITH currency_rate as ({})
             SELECT min(absl.id) as id,
        	    absl.cf_share:: jsonb->'coa_share' as json_share, -- not needed??
        	    absl.name as name,
        	    absl.date as date,
        	    -- absl.amount as amount,
        	    CASE WHEN s.share IS NOT NULL
                     THEN absl.amount * CAST(s.share AS NUMERIC)
                     ELSE absl.amount
                     END AS value,
        	    CASE WHEN (s.key = '') IS NOT TRUE
                     THEN CAST(s.key AS INTEGER)
                     ELSE CAST(NULL AS INTEGER)
                     END AS account_id,
                CAST(NULL AS INTEGER) AS analytic_account_id,
        	    absl.partner_id as partner_id,
    	        absl.journal_id as journal_id,
    	        absl.cf_reconciled as cf_reconciled,
    	        absl.cf_forecast as cf_forecast,
                aa.name as account_name

        """.format(self.env['res.currency']._select_companies_rates())
        return select_str

    def _from(self):
        from_str = """
            account_bank_statement_line absl
            LEFT JOIN LATERAL
            jsonb_each_text(absl.cf_share:: jsonb->'{}') AS s(key, share)
            ON TRUE
            LEFT JOIN account_account aa ON (absl.account_id = aa.id)

        """.format('coa_share')
        return from_str

    def _group_by(self):
        group_by_str = """
            GROUP BY
                absl.id,
                absl.name,
                absl.date,
                -- absl.amount,
                value,
        	    absl.partner_id,
        	    absl.journal_id,
        	    absl.cf_share,
        	    absl.account_id,
    	        absl.cf_reconciled,
    	        absl.cf_forecast,
        	    s.share,
        	    s.key,
                aa.name
        """
        return group_by_str


        # the first SQL query update the JSONB field according to the
        # query parameter and explosion criteria
        # self.env.cr.execute("""
        #UPDATE account_bank_statement_line
        #	    SET json_share = cf_share:: jsonb->'aa_share';
        # """)
        # UPDATE {} SET json_share = cf_share:: jsonb->'aa_share';

        # the second query creates the view

    def _get_main_query(self):
        # self._table = sale_report
        main_query = """
            CREATE or REPLACE VIEW {} as (
            {}
            FROM  {}
            {}
            )

            """.format(self._table, self._select(),
                        self._from(), self._group_by())
        print main_query
        self.env.cr.execute(main_query)
