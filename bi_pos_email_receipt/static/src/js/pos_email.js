odoo.define('bi_pos_email_receipt.pos_email', function(require){
	'use strict';

	var models = require('point_of_sale.models');
	var screens = require('point_of_sale.screens');
	var core = require('web.core');
	var gui = require('point_of_sale.gui');
	var popups = require('point_of_sale.popups');
	//var Model = require('web.DataModel');
	var field_utils = require('web.field_utils');
	var rpc = require('web.rpc');
	var session = require('web.session');
	var time = require('web.time');
	var _t = core._t;

	var utils = require('web.utils');
	// PosNotePopupWidget Popup start
	var color = true;
	var config = false;
	var PosEmailWidget = popups.extend({
		template: 'PosEmailWidget',
		init: function(parent, args) {
			this._super(parent, args);
			this.options = {};
		},
		events: {
		'click .button.confirm':  'click_confirm1',
		'click .button.cancel':  'close_popup1',
		},

		close_popup1: function(ev){
			ev.stopPropagation();
			ev.preventDefault(); 
			ev.stopImmediatePropagation();
		   	this.gui.close_popup(); 
		},

		click_confirm1: function(){
			var self = this;
			var order = this.pos.get_order();
			var new_email = this.$("#entered_email").val()
			order.set_email(new_email);
			if($('#update_email').prop('checked') == true){
				var client = this.pos.get_client()

				rpc.query({
					model: 'pos.order',
					method: 'update_partner_emails',
					args: [1,client.id , new_email],
				}).then(function(output) {
				   if(output){
					// partner_model.domain.push(['shop_ids','in',output]);
					self.gui.close_popup();
					self.gui.show_screen('clientlist');
					}              
				});

			}
			else if(!$('#update_email').prop('checked') == true){
				this.gui.close_popup();
			}   
		},

		renderElement: function() {
				var self = this;
				this._super();
				var order = this.pos.get_order();
				var client = this.pos.get_client();
				var selectedOrder = self.pos.get('selectedOrder');
				if(client && client.email){
					this.$("#entered_email").val(client.email)
					order.set_email(this.$("#entered_email").val())
				}
			},

	});
	gui.define_popup({
		name: 'pos_email_popup_widget',
		widget: PosEmailWidget
	});

	screens.PaymentScreenWidget.include({
		click_emails: function(){
			var order = this.pos.get_order();
			if (color==true) {
				this.$('.button.email').addClass('highlight');
				order.set_staystr(true)
			} else {
				this.$('.button.email').removeClass('highlight');
				order.set_staystr(false)
			}
		},

		show: function(){
			var self = this;
			var order  = self.pos.get_order();
			var client = order.get_client();
			if(client && client.email)
			{	
				this.$('.button.email').addClass('highlight');
				order.set_staystr(true)
			}
			else{
				this.$('.button.email').removeClass('highlight');
				order.set_staystr(false)
			}
			
			this._super();
			
			self.$('.button.editemail').click(function(){
				$('body').keypress(this.keyboard_handler);
				$('body').keydown(this.keyboard_keydown_handler);
				window.document.body.addEventListener('keypress',this.keyboard_handler);
				window.document.body.addEventListener('keydown',this.keyboard_keydown_handler);
				self.gui.show_popup('pos_email_popup_widget', {});
				window.document.body.removeEventListener('keypress',self.keyboard_handler);
				window.document.body.removeEventListener('keydown',self.keyboard_keydown_handler);
				$('#entered_email').on('focus', function() {
					$('body').off(this.keyboard_handler);
					$('body').off(this.keyboard_keydown_handler);
					window.document.body.removeEventListener('keypress', self.keyboard_handler);
					window.document.body.removeEventListener('keydown', self.keyboard_keydown_handler);
				});
				$('#entered_email').on('change', function() {
					$('body').keypress(this.keyboard_handler);
					$('body').keydown(this.keyboard_keydown_handler);
					window.document.body.addEventListener('keypress', this.keyboard_handler);
					window.document.body.addEventListener('keydown', self.keyboard_keydown_handler);
				});
			});
		},


		renderElement: function() {
			var self = this;
			this._super();
			this.$('.button.email').click(function(){
				var order  = self.pos.get_order();
				var client = order.get_client();
				if(client)
				{
					if(client.email)
					{
						if(self.$('.button.email').hasClass('highlight'))
						{
							color=false    
						}else{
							color=true
						}
						self.click_emails();
					}
					else{
						self.gui.show_popup('alert', {
							title: _t('Unkonwn Customer Email ID'),
							body: _t('Please add an email ID of customer.'),
						});
					}
				}
				else{
					self.gui.show_popup('alert', {
						title: _t('Unkonwn Customer '),
						body: _t('Please select customer first.'),
					});
				}
			});
	},
	});


	var OrderSuper = models.Order;
	models.Order = models.Order.extend({

		init: function(parent, options) {
			var self = this;
			this._super(parent,options);
			this.email_receipt = false
			this.set_staystr();
			this.set_email();

		},

		set_staystr: function(email_true){
		this.assert_editable();
			this.email_receipt = email_true;
		},
		set_email: function(email){
		this.assert_editable();
			this.new_email = email;
		},
		
		get_to_stay: function(){
			return this.email_receipt;
		},

		get_to_email: function(){
			return this.new_email;
		},
		
		export_as_JSON: function() {
			var self = this;
			var loaded = OrderSuper.prototype.export_as_JSON.call(this);
			loaded.email_receipt = self.get_to_stay();
			loaded.new_email = self.get_to_email();
			return loaded;
		},

		
	});
	
});