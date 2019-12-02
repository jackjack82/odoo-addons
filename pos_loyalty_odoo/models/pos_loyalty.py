# -*- coding: utf-8 -*-
# Part of BrowseInfo. See LICENSE file for full copyright and licensing details.

from odoo import fields, models, api, _, tools
from datetime import date, time, datetime
from odoo.tools import DEFAULT_SERVER_DATETIME_FORMAT
from odoo.exceptions import UserError, ValidationError,Warning
import logging
_logger = logging.getLogger(__name__)

class PosConfig(models.Model):
	_inherit = 'pos.config'
	
	max_order_amt = fields.Float('Maximum Amount')


class res_partner(models.Model):
	_inherit = 'res.partner'

	loyalty_points = fields.Integer('Loyalty Points')
	prev_points = fields.Integer('Prev Loyalty Points')
	loyalty_amount = fields.Float('Loyalty Amount')
	dob = fields.Date('Date Of Birth')
	gender = fields.Selection([('male','Male'),('female','Female'), ('other','Other')], string="Gender")
	history_ids = fields.One2many('pos.loyalty.history','partner_id',string="Loyalty history")
		
class pos_loyalty_setting(models.Model):
	_name = 'pos.loyalty.setting'
		
	name  = fields.Char('Name' ,default='Configuration for POS Loyalty Management')
	product_id  = fields.Many2one('product.product','Voucher Product', domain = [('type', '=', 'service'),('available_in_pos','=',True)])
	issue_date  =  fields.Datetime(default = datetime.now(),required=True)
	expiry_date  = fields.Datetime('Expiry date',required=True)
	issue_onlydate = fields.Date("Issue only date")
	expiry_onlydate = fields.Date("Expiry only date")
	loyalty_basis_on = fields.Selection([('amount', 'Purchase Amount')], string='Loyalty Basis On', help='Where you want to apply Loyalty Method in POS.')
	active  =  fields.Boolean('Active')
	company_id = fields.Many2one('res.company', string='Company', required=True, default=lambda self: self.env.user.company_id)
	currency_id = fields.Many2one(related='company_id.currency_id')

	loyaly_points = fields.Float('Loyalty Points')
	point_footer = fields.Float('Loyalty Points', related='loyaly_points')
	currency_amt = fields.Float("Currency",default="1")

	redeem_points = fields.Float("Points")
	

	loyality_amount = fields.Float('Amount')
	amount_footer = fields.Float('Amount', related='loyality_amount')

	@api.onchange('expiry_date')
	def get_date(self):
		if self.expiry_date:
			is_dt = self.issue_date.strftime(DEFAULT_SERVER_DATETIME_FORMAT)
			ex_dt = self.expiry_date.strftime(DEFAULT_SERVER_DATETIME_FORMAT)
			d1= datetime.strptime(is_dt,DEFAULT_SERVER_DATETIME_FORMAT).date()
			d2= datetime.strptime(ex_dt,DEFAULT_SERVER_DATETIME_FORMAT).date()
			self.issue_onlydate = d1
			self.expiry_onlydate = d2

	@api.one
	@api.constrains('issue_date','expiry_date')
	def check_date(self):
		record = self.env['pos.loyalty.setting'].search([('active','=',True)])
		for line in record:
			if line.id != self.id:
				if line.issue_date <= self.issue_date  <= line.expiry_date: 
					msg = _("You can not apply two Loyalty Configuration within same date range please change dates.")
					raise Warning(msg) 
					break
				if line.issue_date <= self.expiry_date  <= line.expiry_date:
					msg = _("You can not apply two Loyalty Configuration within same date range please change dates.")
					raise Warning(msg) 
					break

	@api.model
	def search_loyalty_product(self,product_id):
		
		product = self.product_id.search([('id','=',product_id)])

		return product.id

class pos_loyalty_history(models.Model):
	_name = 'pos.loyalty.history'
	_rec_name = 'order_id'
		
	order_id  = fields.Many2one('pos.order','POS Order')
	partner_id  = fields.Many2one('res.partner','Customer')
	partner_barcode = fields.Char('Partner Barcode', related='partner_id.barcode')
	partner_vat = fields.Char('Partner VAT', related='partner_id.vat')
	date  =  fields.Datetime(default = datetime.now(), )
	transaction_type = fields.Selection([('credit', 'Credit'), ('debit', 'Debit')], string='Transaction Type', help='credit/debit loyalty transaction in POS.')
	points = fields.Integer('Gained/Used Points')
	user_id =  fields.Many2one('res.users','User')
	total_points = fields.Integer('Total Loyalty Points')
	session_id  = fields.Many2one('pos.session',"POS session")
	config_id = fields.Many2one('POS', related='session_id.config_id')
	product_id = fields.Many2one('product.product','Voucher Product', domain = [('type', '=', 'service'),('available_in_pos','=',True)])
	voucher_amount = fields.Float("Voucher Amount")

class POSOrder(models.Model):
	_inherit = 'pos.order'

	redeemed_points = fields.Float("Redeemed Points")
	order_loyalty  = fields.Float("Gained Points")

	@api.model
	def _order_fields(self, ui_order):
		rec = super(POSOrder, self)._order_fields(ui_order)
		if  "loyalty" in ui_order:
			rec.update({
				'order_loyalty' : ui_order['loyalty']
			})
		if "redeemed_points" in ui_order:
			rec.update({
				'redeemed_points' : ui_order['redeemed_points']
			})
		return rec

	@api.model
	def create_from_ui(self, orders):
		order_ids = super(POSOrder, self).create_from_ui(orders)
		loyalty_history_obj = self.env['pos.loyalty.history']
		for order_id in order_ids:
			try:
				pos_order_id = self.browse(order_id)
				
				if pos_order_id:
					ref_order = [o['data'] for o in orders if o['data'].get('name') == pos_order_id.pos_reference]
					for order in ref_order:
						cust_loyalty = pos_order_id.partner_id.loyalty_points + order.get('loyalty')
						order_loyalty = order.get('loyalty')
						redeemed = order.get('redeemed_points')
						pos_order_id.write({
							'redeemed_points' : redeemed,
							'order_loyalty' : order_loyalty
							})
						if order_loyalty > 0:
							vals1 = {
								'order_id':pos_order_id.id,
								'partner_id': pos_order_id.partner_id.id,
								'date' : datetime.now(),
								'transaction_type' : 'credit',
								'points': order_loyalty,
								'user_id' : pos_order_id.user_id.id,
								'session_id' : pos_order_id.session_id.id,
								'total_points' : pos_order_id.partner_id.prev_points + order_loyalty,
							}
							loyalty_history = loyalty_history_obj.create(vals1)
						if order.get('redeem_done') == True:
							voucher_product = self.env['pos.loyalty.setting'].search([('active','=',True)]).product_id
							vals = {
								'order_id':pos_order_id.id,
								'partner_id': pos_order_id.partner_id.id,
								'date' : datetime.now(),
								'transaction_type' : 'debit',
								'points': redeemed,
								'total_points' : pos_order_id.partner_id.prev_points - redeemed + order_loyalty,
								'user_id' : pos_order_id.user_id.id,
								'session_id' : pos_order_id.session_id.id,
								'product_id': voucher_product.id,
								'voucher_amount' : voucher_product.lst_price,
							}
							loyalty_history = loyalty_history_obj.create(vals)
						
					
			except Exception as e:
				_logger.error('Error in point of sale validation: %s', tools.ustr(e))
		return order_ids

	@api.model
	def get_partner_points(self, client):

		partner = self.env['res.partner'].browse(client)
		curr_loyalty_amount = partner.loyalty_points

		return curr_loyalty_amount

	@api.model
	def update_partner_points(self, client,loyalty_points):

		partner = self.env['res.partner'].browse(client)
		loyalty_points = loyalty_points
		partner.update({
			'prev_points' : partner.loyalty_points,
			'loyalty_points': loyalty_points,
		})
		return loyalty_points

			
		
# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4:    
