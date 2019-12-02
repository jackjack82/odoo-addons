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

	// ClientListScreenWidget start
	gui.Gui.prototype.screen_classes.filter(function(el) { return el.name == 'clientlist'})[0].widget.include({

		get_loyalty_history: function (partner) {
			var self = this;
			console.log("partner ===============",partner)
			var fields = ['id','date','order_id', 'transaction_type', 'points', 'total_points'];
			var loyalty_domain = [['partner_id', 'in', [partner.id]]];
			var load_loyalty = [];
			rpc.query({
					model: 'pos.loyalty.history',
					method: 'search_read',
					args: [loyalty_domain,fields],
			}, {async: false}).then(function(output) {
				load_loyalty = output;
				self.pos.set({'loyalty_history_list' : output});
			}); 
		},

		render_loyalty_list: function(loyalty_history_list){
			var self = this;
			var content = this.$el[0].querySelector('.loyalty-list-contents');
			content.innerHTML = "";
			var current_date = null;
			console.log(loyalty_history_list,"nathiiiiiiiiiiiiiiiiii")
			if(loyalty_history_list.length > 0){
				console.log(loyalty_history_list,"11111111111")
				for(var i = 0, len = Math.min(loyalty_history_list.length,1000); i < len; i++){
					var loyalty    = loyalty_history_list[i];
					var loyalty_history_line_html = QWeb.render('LoayltyLine',{widget: this, loyalty:loyalty});
					var loyalty_history_line = document.createElement('tbody');
					loyalty_history_line.innerHTML = loyalty_history_line_html;
					loyalty_history_line = loyalty_history_line.childNodes[1];
					content.appendChild(loyalty_history_line);
				}
			}
			else{
					console.log(loyalty_history_list,"22222222222222222");
					var no_rec = "<div style='text-align: center;border-top: solid 5px rgb(110,200,155);font-size: 17px;margin-top: 10px;padding: 10px;'><span>No Loyalty History Record Found<span></div>";
					$('.loyalty').html(no_rec);
				}
		},

		display_client_details: function(visibility,partner,clickpos){
			var self = this;
			var searchbox = this.$('.searchbox input');
			var contents = this.$('.client-details-contents');
			var parent   = this.$('.client-list').parent();
			var scroll   = parent.scrollTop();
			var height   = contents.height();

			contents.off('click','.button.edit'); 
			contents.off('click','.button.save'); 
			contents.off('click','.button.undo'); 
			contents.on('click','.button.edit',function(){ self.edit_client_details(partner); });
			contents.on('click','.button.save',function(){ self.save_client_details(partner); });
			contents.on('click','.button.undo',function(){ self.undo_client_details(partner); });
			this.editing_client = false;
			this.uploaded_picture = null;
			self.get_loyalty_history(partner);
			var loyalty_history_list =  self.pos.get('loyalty_history_list');

			if(visibility === 'show'){
				contents.empty();
				contents.append($(QWeb.render('ClientDetails',{widget:this,partner:partner})));
				self.render_loyalty_list(loyalty_history_list);
				var new_height   = contents.height();

				if(!this.details_visible){
					// resize client list to take into account client details
					parent.height('-=' + new_height);

					if(clickpos < scroll + new_height + 20 ){
						parent.scrollTop( clickpos - 20 );
					}else{
						parent.scrollTop(parent.scrollTop() + new_height);
					}
				}else{
					parent.scrollTop(parent.scrollTop() - height + new_height);
				}

				this.details_visible = true;
				this.toggle_save_button();
			} else if (visibility === 'edit') {
				// Connect the keyboard to the edited field
				if (this.pos.config.iface_vkeyboard && this.chrome.widget.keyboard) {
					contents.off('click', '.detail');
					searchbox.off('click');
					contents.on('click', '.detail', function(ev){
						self.chrome.widget.keyboard.connect(ev.target);
						self.chrome.widget.keyboard.show();
					});
					searchbox.on('click', function() {
						self.chrome.widget.keyboard.connect($(this));
					});
				}

				this.editing_client = true;
				contents.empty();
				contents.append($(QWeb.render('ClientDetailsEdit',{widget:this,partner:partner})));
				this.toggle_save_button();

				// Browsers attempt to scroll invisible input elements
				// into view (eg. when hidden behind keyboard). They don't
				// seem to take into account that some elements are not
				// scrollable.
				contents.find('input').blur(function() {
					setTimeout(function() {
						self.$('.window').scrollTop(0);
					}, 0);
				});

				contents.find('.image-uploader').on('change',function(event){
					self.load_image_file(event.target.files[0],function(res){
						if (res) {
							contents.find('.client-picture img, .client-picture .fa').remove();
							contents.find('.client-picture').append("<img src='"+res+"'>");
							contents.find('.detail.picture').remove();
							self.uploaded_picture = res;
						}
					});
				});
			} else if (visibility === 'hide') {
				contents.empty();
				parent.height('100%');
				if( height > scroll ){
					contents.css({height:height+'px'});
					contents.animate({height:0},400,function(){
						contents.css({height:''});
					});
				}else{
					parent.scrollTop( parent.scrollTop() - height);
				}
				this.details_visible = false;
				this.toggle_save_button();
			}
		},
		
	
	});
	// End ClientListScreenWidget
	
	var _super = models.Order;
	var OrderSuper = models.Order;
	models.Order = models.Order.extend({
		initialize: function(attributes, options) {
			OrderSuper.prototype.initialize.apply(this, arguments);
			this.set({ redeem_done: false });
			this.redeemed_points = this.redeemed_points || 0;
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
			return parseInt(this.redeemed_points);
		},

		export_as_JSON: function() {
			var json = OrderSuper.prototype.export_as_JSON.apply(this, arguments);
			var self = this;
			var selectedOrder = self.pos.get_order();
			if (selectedOrder != undefined) {
				if(selectedOrder.get('redeem_done') == true)
				{
					json.redeemed_points = parseInt(this.redeemed_points);
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
			$('body').keypress(this.keyboard_handler);
			$('body').keydown(this.keyboard_keydown_handler);
			window.document.body.addEventListener('keypress',this.keyboard_handler);
			window.document.body.addEventListener('keydown',this.keyboard_keydown_handler);
			$('#entered_item_qty').on('focus', function() {
				$('body').off(this.keyboard_handler);
				$('body').off(this.keyboard_keydown_handler);
				window.document.body.removeEventListener('keypress', self.keyboard_handler);
				window.document.body.removeEventListener('keydown', self.keyboard_keydown_handler);
			});
			$('#entered_item_qty').on('change', function() {
				$('body').keypress(this.keyboard_handler);
				$('body').keydown(this.keyboard_keydown_handler);
				window.document.body.addEventListener('keypress', this.keyboard_handler);
				window.document.body.addEventListener('keydown', self.keyboard_keydown_handler);
			});
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
					order.redeemed_points = used_points;
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
			$('body').keypress(this.keyboard_handler);
			$('body').keydown(this.keyboard_keydown_handler);
			window.document.body.addEventListener('keypress',this.keyboard_handler);
			window.document.body.addEventListener('keydown',this.keyboard_keydown_handler);
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
						window.document.body.removeEventListener('keypress',self.keyboard_handler);
						window.document.body.removeEventListener('keydown',self.keyboard_keydown_handler);
						$('#entered_item_qty').on('focus', function() {
							$('body').off(this.keyboard_handler);
							$('body').off(this.keyboard_keydown_handler);
							window.document.body.removeEventListener('keypress', self.keyboard_handler);
							window.document.body.removeEventListener('keydown', self.keyboard_keydown_handler);
						});
						$('#entered_item_qty').on('change', function() {
							$('body').keypress(this.keyboard_handler);
							$('body').keydown(this.keyboard_keydown_handler);
							window.document.body.addEventListener('keypress', this.keyboard_handler);
							window.document.body.addEventListener('keydown', self.keyboard_keydown_handler);
						});
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
