odoo.define('pos_loyalty_odoo.pos', function(require) {
	"use strict";

	var models = require('point_of_sale.models');
	var screens = require('point_of_sale.screens');
	var core = require('web.core');
	var gui = require('point_of_sale.gui');
	var popups = require('point_of_sale.popups');
	var utils = require('web.utils');
	var rpc = require('web.rpc');
	var QWeb = core.qweb;
	var _t = core._t;
	var redeem;
	var point_value = 0;
	var remove_line;
	var remove_true = false;
	var entered_code = 0;
	var redeemed_points = 0;
	// Load Models
	models.load_models({
		model: 'pos.loyalty.setting',
		fields: ['name', 'product_id', 'issue_onlydate', 'expiry_onlydate', 'loyalty_basis_on','active', 'loyaly_points', 'redeem_points','currency_amt'],
		domain: function(self) 
		{
			var today = new Date();
			var dd = today.getDate();
			var mm = today.getMonth()+1; //January is 0!s
			var yyyy = today.getFullYear();
			if(dd<10){
				dd='0'+dd;
			} 
			if(mm<10){
				mm='0'+mm;
			} 
			var today = yyyy+'-'+mm+'-'+dd;
			return [['issue_onlydate', '<=',today],['expiry_onlydate', '>=',today]];
		},
		loaded: function(self, pos_loyalty_setting) {
			self.pos_loyalty_setting = pos_loyalty_setting;
		},
	});
		
	var _super_posmodel = models.PosModel.prototype;
	models.PosModel = models.PosModel.extend({
		initialize: function (session, attributes) {
			var partner_model = _.find(this.models, function(model){ return model.model === 'res.partner'; });
			partner_model.fields.push('loyalty_points','loyalty_amount','dob','gender');
			return _super_posmodel.initialize.call(this, session, attributes);
		},
	});
	
	var _super = models.Order;
	var OrderSuper = models.Order;
	models.Order = models.Order.extend({
		initialize: function(attributes, options) {
			OrderSuper.prototype.initialize.apply(this, arguments);
			this.set({ redeem_done: false });
		},
		
		remove_orderline: function(line) {
			var product_id = line.product.id;
			this.set('redeem_done', false);
			_super.prototype.remove_orderline.apply(this, arguments);
		},

		get_total_loyalty: function() {
			var final_loyalty = 0
			var order = this.pos.get_order();
			var orderlines = this.get_orderlines();
			var partner_id = this.get_client();
			var loyalty_setting = this.pos.pos_loyalty_setting;	
			var amount_total = order.get_total_with_tax();
			

			if(loyalty_setting.length != 0)
			{	
				var loyaly_points = loyalty_setting[0].loyaly_points;
				var currency_amt = loyalty_setting[0].currency_amt;
			   	if (loyalty_setting[0].loyalty_basis_on == 'amount') {
					if (order && partner_id)
					{
						if(amount_total >= currency_amt)
						{
							var temp = Math.floor(amount_total / currency_amt);
							final_loyalty = temp * loyaly_points;
						}
						return Math.floor(final_loyalty);
						
					}
				}
			}
		
		},

		get_redeemed_points: function() {
			return parseInt(redeemed_points);
		},

		export_as_JSON: function() {
			var json = OrderSuper.prototype.export_as_JSON.apply(this, arguments);
			var self = this;
			var selectedOrder = self.pos.get_order();
			if (selectedOrder != undefined) {
				if(selectedOrder.get('redeem_done') == true)
				{
					json.redeemed_points = parseInt(redeemed_points);
					json.loyalty = this.get_total_loyalty();
				}
				else{
					json.loyalty = this.get_total_loyalty();
				}				
				json.redeem_done = selectedOrder.get('redeem_done');
			}
			return json;
		},
	
	});

	var OrderWidgetExtended = screens.OrderWidget.include({

		orderline_remove: function(line){
			var order = this.pos.get_order();
			var partner = order.get_client();
			this.remove_orderline(line);
			this.numpad_state.reset();
			if(line.id == remove_line)
			{
				remove_true = true;
				partner.loyalty_points = parseInt(partner.loyalty_points) + order.get("redeem_point");
			}
			else
			{
				remove_true = false;
			}
			this.update_summary();
		},

		update_summary: function(){
			var order = this.pos.get_order();
			var partner = order.get_client();
			if(partner)
				var temp_loyalty_point = partner.loyalty_points
				
			if (!order.get_orderlines().length) {
				return;
			}

			var total     = order ? order.get_total_with_tax() : 0;
			var taxes     = order ? total - order.get_total_without_tax() : 0;

			var round_pr = utils.round_precision;
			var rounding = this.pos.currency.rounding;
			
			this.el.querySelector('.summary .total > .value').textContent = this.format_currency(total);
			this.el.querySelector('.summary .total .subentry .value').textContent = this.format_currency(taxes);

			if(this.pos.pos_loyalty_setting.length != 0)
			{
				if (partner) {
					if(remove_true == true)
					{
						partner.loyalty_points = partner.loyalty_points
						order.set('update_after_redeem',partner.loyalty_points)
					}
					else{
						if(order.get('update_after_redeem') >= 0){
							partner.loyalty_points = order.get("update_after_redeem");
						}else{
							partner.loyalty_points = partner.loyalty_points
						}
					}

					var loyalty_points = 0

					loyalty_points    = order ? order.get_total_loyalty() : 0;
					temp_loyalty_point = partner.loyalty_points + loyalty_points ;    

					this.el.querySelector('.items').style.display = 'inline-block'
					this.el.querySelector('.items .loyalty').textContent = loyalty_points;
					this.el.querySelector('.items .value').textContent = temp_loyalty_point;
					order.set("temp_loyalty_point",temp_loyalty_point)
				}
			}

		},
	});
	
	

	// LoyaltyPopupWidget start
	var LoyaltyPopupWidget = popups.extend({
		template: 'LoyaltyPopupWidget',
		init: function(parent, args) {
			this._super(parent, args);
			this.options = {};
			this.loyalty = 0;
			this.vouchers = 0;
			this.redeem_points = 0;
		},

		events: {
			'click #apply_redeem_now':  'redeem_loyalty_points',
			'click .button.cancel':  'close_popup_o',
		},

		close_popup_o: function(ev){
			ev.stopPropagation();
			ev.preventDefault(); 
			ev.stopImmediatePropagation();
		   	this.gui.close_popup(); 
		},

		show: function(options) {
			options = options || {};
			var self = this;
			this._super(options);
			var order = this.pos.get_order();
			var loyalty_setting = this.pos.pos_loyalty_setting;             
			var partner = false
			if (order.get_client() != null)
				partner = order.get_client();
						   
			if (partner) {
				this.partner = options.partner.name || {};
				var curr_loyalty_points = 0
				partner.loyalty_amount = point_value;
				self.loyalty = partner.loyalty_points;
				self.loyalty_amount = point_value;
				if(loyalty_setting.length != 0)
				{
					this.redeem_points = loyalty_setting[0].redeem_points;
					var vchr = self.loyalty/this.redeem_points ;
					this.vouchers = Math.floor(vchr);
				}
				self.renderElement();
			}else{	
				self.gui.show_popup('error', {
					'title': _t('Unknown customer'),
					'body': _t('You cannot use redeeming loyalty points. Select customer first.'),
				});
			}
		},

		renderElement: function() {
			var self = this;
			this._super();
		},

		redeem_loyalty_points: function(ev){
			ev.stopPropagation();
			ev.preventDefault(); 
			ev.stopImmediatePropagation();
			var self = this;
			var order = this.pos.get_order();
			var selectedOrder = self.pos.get('selectedOrder');
			var orderlines = selectedOrder.orderlines;
			var total     = order.get_total_with_tax();
			var update_orderline_loyalty = 0 ;
			var loyalty_setting = this.pos.pos_loyalty_setting;			 

			if(loyalty_setting.length != 0)
			{
				var product_id = loyalty_setting[0].product_id[0];
				var product = this.pos.db.get_product_by_id(product_id);
			}
	   		entered_code = $("#entered_item_qty").val();
			remove_true = false
			if(parseInt(entered_code) <= this.vouchers)
			{
				if ((product.lst_price * parseInt(entered_code)) <= total) {
					var used_points = parseInt(entered_code) * self.redeem_points
					selectedOrder.add_product(product, {
						price: -product.lst_price,
						quantity: parseInt(entered_code),
					});
					update_orderline_loyalty = self.loyalty -  used_points;
					redeemed_points = used_points;
					remove_line = orderlines.models[orderlines.length-1].id;
					order.set('update_after_redeem',update_orderline_loyalty);
					update_orderline_loyalty = update_orderline_loyalty;
					order.set('redeem_done', true);
					order.set("redeem_point",used_points);
					self.gui.show_screen('products');
				}
				else{
					self.gui.show_popup('alert', {
						title: _t('Please enter valid amount'),
						body:_t('You are trying to redeem more than order amount.'),
						
					});
				}
			}
			else{
				self.gui.show_popup('alert', {
					title: _t('Please enter valid amount'),
					body:_t('Please enter valid voucher amount.'),
				});
			}
		},

	});
	gui.define_popup({
		name: 'redeem_loyalty_popup_widget',
		widget: LoyaltyPopupWidget
	});

	// End LoyaltyPopupWidget start

	var LoyaltyButtonWidget = screens.ActionButtonWidget.extend({
		template: 'LoyaltyButtonWidget',
		button_click: function() {
			var order = this.pos.get_order();
			var self = this;
			var partner = false
			if(order.orderlines.length>0)
			{
				if(this.pos.pos_loyalty_setting.length != 0)
				{
					if (order.get_client() != null)
						partner = order.get_client();
										
					if(order.get('redeem_done')){
						self.gui.show_popup('error', {
							'title': _t('Redeem Product'),
							'body': _t('Sorry, you already added the redeem product.'),
						}); 
					}
					else if(this.pos.pos_loyalty_setting[0].redeem_points < 1)
					{
						self.gui.show_popup('error', {
							'title': _t('No Redemption Rule'),
							'body': _t('Please add Redemption Rule in loyalty configuration'),
						}); 
					}
					else{
						this.gui.show_popup('redeem_loyalty_popup_widget', {'partner':partner});
					} 
				}    
			}
			else{
				self.gui.show_popup('error', {
					'title': _t('Empty Order'),
					'body': _t('Please select some products'),
				}); 
			}
				   
		},
	});

	screens.define_action_button({
		'name': 'Redeem Loyalty Points',
		'widget': LoyaltyButtonWidget,
		'condition': function() {
			return true;
		},
	});


	screens.PaymentScreenWidget.include({

		validate_order: function(force_validation){
			var self = this;
			var order = this.pos.get_order();
			var client = order.get_client();
			var max_order_amt = self.pos.config.max_order_amt;
			if(client)
			{
				rpc.query({
					model: 'pos.order',
					method: 'update_partner_points',
					args: [client.id,parseInt(order.get('temp_loyalty_point'))],
				},{'async':false}).then(function(output) {})
			}
			if(max_order_amt > 0)
			{
				if(order.get_total_with_tax() > max_order_amt){
					self.pos.gui.show_popup('confirm', {
						'title': _t('Order Validation !!!!'),
						'body': _t('Order amount is more than maximum amount of configuration'),
						confirm: function () {
							if (self.order_is_valid(force_validation)) {
								self.finalize_validation();
							}
						},
						cancel: function () {
							return self.pos.gui.close_popup();
						}
					});
				}
				else{
					if (self.order_is_valid(force_validation)) {
						self.finalize_validation();
					}
				}	
			}	
			else{
				if (self.order_is_valid(force_validation)) {
					self.finalize_validation();
				}
			}		
		},
	 
	});
	
		

});
